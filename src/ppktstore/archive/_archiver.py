import logging
import os
import re
import shutil
import tarfile
import tempfile
import typing

from collections import defaultdict

import pandas as pd

from ppktstore.model import PhenopacketStore
from ppktstore.stats import create_summary_df

from .cohort import Cohort


class PhenopacketStoreArchiver:
    """
    This class helps organize the task of extracting all phenopackets from the notebooks of
    phenopacket-store and of archiving them with zip (:func:`get_store_zip`)or tar/gz (:func:`get_store_gzip`)
    formats.

    The phenopackets are placed into the subfolders determined by the cohort names (`flat=False`)
    or into a single top-level directory (`flat=True`).

    A TSV summary file is included in the archive.
    """

    def __init__(
        self,
        phenopacket_store: PhenopacketStore,
    ):
        """
        :param notebook_dir: path to the directory that contains all subdirectories for cohorts
        """
        self._logger = logging.getLogger(__name__)
        self._phenopacket_store = phenopacket_store
        self._suffix_pt = re.compile(r'(?P<suffix>\.\w+(\.\w+)?)$')

    @staticmethod
    def _get_cohort_name(
        lpath_components: typing.Sequence[str]
    ):
        if len(lpath_components) < 3:
            raise ValueError(f"Unexpected path with {len(lpath_components)} components: {lpath_components}")
        return lpath_components[-2]

    def get_store_gzip(
            self,
            outfilename: str,
            flat: bool = False,
    ):
        """
        Pack all phenopackets into a TAR GZ archive and store the archive at `outfilename`.

        :param outfilename: path for storing the archive file with *NO* file suffix.
          The `.tgz` suffix will be added to the archive name by this function
        :param flat: `True` if the phenopackets from all cohorts should be copied into one directory,
          or `False` if the phenopackets should be copied into subdirectories corresponding to cohorts
        """
        self._check_no_suffix_in_filename(outfilename)

        basename = os.path.basename(outfilename)

        with tempfile.TemporaryDirectory() as tmpdirname:
            self._pack_content_into_temp_directory(tmpdirname, flat, basename)

            with tarfile.open(f'{outfilename}.tgz', "w:gz") as tar:
                tar.add(tmpdirname, arcname='')

    def get_store_zip(
            self,
            outfilename: str,
            flat: bool = False,
    ):
        """
        Pack all phenopackets into a ZIP archive and store the archive at `outfilename`.

        :param outfilename: path for storing the ZIP file with NO file suffix.
          The `.zip` suffix will be added to the archive name by this function
        :param flat: `True` if the phenopackets from all cohorts should be copied into one directory, 
          or `False` if the phenopackets should be copied into subdirectories corresponding to cohorts
        """
        self._check_no_suffix_in_filename(outfilename)

        basename = os.path.basename(outfilename)
        with tempfile.TemporaryDirectory() as tmpdirname:
            self._pack_content_into_temp_directory(tmpdirname, flat, basename)

            shutil.make_archive(outfilename, 'zip', tmpdirname)

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
        tmpdirname: str,
        flat: bool,
        basename: str
    ):
        # Insert a top-level directory
        top_level = os.path.join(tmpdirname, basename)
        os.makedirs(top_level, exist_ok=True)

        # Create the summary TSV
        tsv_file_name = os.path.join(top_level, f'{basename}.tsv')
        summary_df = create_summary_df(self._phenopacket_store)
        summary_df.to_csv(
            tsv_file_name,
            sep='\t', index=False,
        )

        # Copy phenopackets into the destination folder
        n_copied_files = self._copy_files_to_temporary_directory(top_level, flat)
        self._logger.info("Added %s files to zip archive at %s", n_copied_files, basename)

    def _copy_files_to_temporary_directory(
            self,
            tmpdirname: str,
            flat: bool = False,
    ) -> int:
        n_copied_files = 0
        for cohort_info in self._phenopacket_store.cohorts():
            temp_cohort_dir = tmpdirname
            if not flat:
                temp_cohort_dir = os.path.join(tmpdirname, cohort_info.name)
                os.makedirs(temp_cohort_dir)
            
            # original files
            cohort_path = self._phenopacket_store.path.joinpath(cohort_info.path)
            for pp_info in cohort_info.phenopackets:    
                pp_path = cohort_path.joinpath(pp_info.path)
                shutil.copy(pp_path, temp_cohort_dir)
                n_copied_files += 1
        return n_copied_files

    def get_phenopacket_dataframe(self) -> pd.DataFrame:
        # TODO: seems to be unused. Consider removing.
        column_names = Cohort.get_detailed_header()
        rows = []
        for cohort in self._cohorts:
            items = cohort.get_detailed_dict()
            rows.extend(items)
        return pd.DataFrame.from_records(rows, columns=column_names)

    def get_summary_dir(self) -> pd.DataFrame:
        # TODO: seems to be unused. Consider removing.
        rows = defaultdict(list)
        
        for cohort in self._phenopacket_store.cohorts():
            rows['Cohort'].append(cohort.name)
            rows['Directory'].append(cohort.path)
            rows['Count'].append(len(cohort))
        
        return pd.DataFrame(rows)

    @staticmethod
    def get_filename(pathname):
        # TODO: seems to be unused. Consider removing.
        fields = pathname.split(os.path.sep)
        fname = fields[-1]
        if not fname.endswith(".json"):
            raise ValueError(f"Malformed path {pathname}")
        else:
            return fname
