import enum
import logging
import os
import re
import shutil
import tarfile
import tempfile
import typing

from ppktstore.model import PhenopacketStore
from ppktstore.stats import summarize_diseases_and_genotype

class ArchiveFormat(enum.Enum):
    """
    Phenopacket store archive format.
    """

    ZIP = 0
    TGZ = 1

    def __str__(self) -> str:
        if self == ArchiveFormat.ZIP:
            return 'ZIP'
        elif self == ArchiveFormat.TGZ:
            return 'TGZ'
        else:
            raise ValueError(f'Unknown archive format {self}')


class PhenopacketStoreArchiver:
    """
    This class helps organize the task of extracting all phenopackets from the notebooks of
    phenopacket-store and of archiving them with (:func:`prepare_archive`) function.

    The phenopackets are placed into the subfolders determined by the cohort names (`flat=False`)
    or into a single top-level directory (`flat=True`).

    A TSV summary file is included in the archive.
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._suffix_pt = re.compile(r'(?P<suffix>\.\w+(\.\w+)?)$')

    @staticmethod
    def _get_cohort_name(
        lpath_components: typing.Sequence[str]
    ):
        if len(lpath_components) < 3:
            raise ValueError(f"Unexpected path with {len(lpath_components)} components: {lpath_components}")
        return lpath_components[-2]

    def prepare_archive(
        self,
        store: PhenopacketStore,
        format: ArchiveFormat,
        filename: str,
        top_level_folder: str = 'phenopacket_store',
        flat: bool = False,
    ):
        """
        Build archive for phenopacket store.

        :param store: phenopacket store with the phenopacket cohorts.
        :param filename: path for storing the archive file with *NO* file suffix.
          The archive suffix will be added to the file name (e.g. `.tgz` or `.zip`).
        :param top_level_folder: the name of the top-level folder where all cohorts/phenopackets will be placed into.
        :param flat: `True` if the phenopackets from all cohorts should be copied into one directory,
          or `False` if the phenopackets should be copied into subdirectories corresponding to cohorts
        """
        if format == ArchiveFormat.TGZ:
            self._make_gzip(
                store=store, 
                filename=filename,
                top_level_folder=top_level_folder,
                flat=flat,
            )
        elif format == ArchiveFormat.ZIP:
            self._make_zip(
                store=store, 
                filename=filename,
                top_level_folder=top_level_folder,
                flat=flat,
            )
        else:
            raise ValueError(f'Unknown format {format}')
        

    def _make_gzip(
        self,
        store: PhenopacketStore,
        filename: str,
        top_level_folder: str,
        flat: bool,
    ):
        """
        Pack all phenopackets into a TAR GZ archive and store the archive at `outfilename`.

        :param store: phenopacket store with the phenopacket cohorts.
        :param filename: path for storing the archive file with *NO* file suffix.
          The `.tgz` suffix will be added to the archive name by this function
        :param top_level_folder: the name of the top-level folder.
        :param flat: `True` if the phenopackets from all cohorts should be copied into one directory,
          or `False` if the phenopackets should be copied into subdirectories corresponding to cohorts
        """
        self._check_no_suffix_in_filename(filename)

        with tempfile.TemporaryDirectory() as tmpdirname:
            self._pack_content_into_temp_directory(store, tmpdirname, flat, top_level_folder)

            with tarfile.open(f'{filename}.tgz', "w:gz") as tar:
                tar.add(tmpdirname, arcname='')

    def _make_zip(
        self,
        store: PhenopacketStore,
        filename: str,
        top_level_folder: str,
        flat: bool = False,
    ):
        """
        Pack all phenopackets into a ZIP archive and store the archive at `outfilename`.

        :param store: phenopacket store with the phenopacket cohorts.
        :param filename: path for storing the ZIP file with NO file suffix.
          The `.zip` suffix will be added to the archive name by this function
        :param top_level_folder: the name of the top-level folder.
        :param flat: `True` if the phenopackets from all cohorts should be copied into one directory, 
          or `False` if the phenopackets should be copied into subdirectories corresponding to cohorts
        """
        self._check_no_suffix_in_filename(filename)

        with tempfile.TemporaryDirectory() as tmpdirname:
            self._pack_content_into_temp_directory(store, tmpdirname, flat, top_level_folder)

            shutil.make_archive(filename, 'zip', tmpdirname)

    def _check_no_suffix_in_filename(
            self,
            outfilename: str,
    ):
        matcher = self._suffix_pt.search(outfilename)
        if matcher:
            suffix = outfilename[matcher.start('suffix'):matcher.end('suffix')]
            raise ValueError(f'The path must not include suffix but found {suffix} in {outfilename}')

    def _pack_content_into_temp_directory(
        self,
        store: PhenopacketStore,
        tmpdirname: str,
        flat: bool,
        top_level_folder: str
    ):
        # Insert a top-level directory
        top_level = os.path.join(tmpdirname, top_level_folder)
        os.makedirs(top_level, exist_ok=True)

        # Create the summary TSV
        summary_filename = os.path.join(top_level, 'phenopacket_store.summary.tsv')
        summary_df = summarize_diseases_and_genotype(store)
        summary_df.to_csv(
            summary_filename,
            sep='\t', index=False,
        )

        # Copy phenopackets into the destination folder
        n_copied_files = self._copy_files_to_temporary_directory(store, top_level, flat)
        self._logger.info("Added %s files to the archive", n_copied_files)

    def _copy_files_to_temporary_directory(
            self,
            store: PhenopacketStore,
            tmpdirname: str,
            flat: bool = False,
    ) -> int:
        n_copied_files = 0
        for cohort_info in store.cohorts():
            temp_cohort_dir = tmpdirname
            if not flat:
                temp_cohort_dir = os.path.join(tmpdirname, cohort_info.name)
                os.makedirs(temp_cohort_dir)
            
            # original files
            cohort_path = store.path.joinpath(cohort_info.path)
            for pp_info in cohort_info.phenopackets:    
                pp_path = cohort_path.joinpath(pp_info.path)
                shutil.copy(pp_path, temp_cohort_dir)
                n_copied_files += 1
        return n_copied_files

    @staticmethod
    def get_filename(pathname):
        # TODO: seems to be unused. Consider removing.
        fields = pathname.split(os.path.sep)
        fname = fields[-1]
        if not fname.endswith(".json"):
            raise ValueError(f"Malformed path {pathname}")
        else:
            return fname
