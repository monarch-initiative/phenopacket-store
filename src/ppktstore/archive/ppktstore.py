import logging
import os
import re
import shutil
import tarfile
import tempfile
import typing

import pandas as pd
from google.protobuf.json_format import Parse
from phenopackets import Phenopacket

from .cohort import Cohort


class PPKtStore:
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
            notebook_dir: str,
    ):
        """
        :param notebook_dir: path to the directory that contains all subdirectories for cohorts
        """
        if not os.path.isdir(notebook_dir):
            raise ValueError(f"Not a directory: {notebook_dir}")
        self._logger = logging.getLogger(__name__)
        self._cohorts = []
        for dirpath, dirnames, filenames in os.walk(notebook_dir):
            if dirpath.endswith("phenopackets"):
                lpath_components = dirpath.split(os.sep)
                cohort_name = PPKtStore._get_cohort_name(lpath_components)
                json_files = filter(lambda f: f.endswith('.json'), filenames)
                c = Cohort(name=cohort_name, dirpath=dirpath, files=json_files)
                self._cohorts.append(c)
        self._suffix_pt = re.compile(r'(?P<suffix>\.\w+(\.\w+)?)$')

    @staticmethod
    def _get_cohort_name(
            lpath_components: typing.Sequence[str]
    ):
        if len(lpath_components) < 3:
            raise ValueError(f"Unexpected path with {len(lpath_components)} components: {lpath_components}")
        return lpath_components[-2]

    def get_phenopacket_dataframe(self) -> pd.DataFrame:
        column_names = Cohort.get_detailed_header()
        rows = []
        for cohort in self._cohorts:
            items = cohort.get_detailed_dict()
            rows.extend(items)
        return pd.DataFrame.from_records(rows, columns=column_names)

    def get_summary_dir(self) -> pd.DataFrame:
        rows = []
        column_names = ["Cohort", "Directory", "Count"]
        for cohort in self._cohorts:
            d = {
                "Cohort": cohort.name,
                "Directory": cohort.directory,
                "Count": str(cohort.count)
            }
            rows.append(d)
        return pd.DataFrame.from_records(rows, columns=column_names)

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
        self._create_summary_tsv(tsv_file_name)

        # Copy phenopackets into the destination folder
        n_copied_files = self._copy_files_to_temporary_directory(top_level, flat)
        self._logger.info("Added %s files to zip archive at %s", n_copied_files, basename)

    def _copy_files_to_temporary_directory(
            self,
            tmpdirname: str,
            flat: bool = False,
    ) -> int:
        n_copied_files = 0
        for cohort in self._cohorts:
            temp_cohort_dir = tmpdirname
            if not flat:
                temp_cohort_dir = os.path.join(tmpdirname, cohort.name)
                os.makedirs(temp_cohort_dir)
            # original files
            for fpath_pp in cohort.phenopacket_files:
                shutil.copy(fpath_pp, temp_cohort_dir)
                n_copied_files += 1
        return n_copied_files

    @staticmethod
    def get_pmid(meta_data) -> str:
        if meta_data.external_references:
            return meta_data.external_references[0].id
        else:
            # should never happen
            raise ValueError('Cannot extract PMID')

    @staticmethod
    def get_structural_var(variation_descriptor) -> typing.List[str]:
        alleles = list()
        if variation_descriptor.HasField("structural_type"):
            stype = variation_descriptor.structural_type
            alleles.append(stype.label)
        else:
            raise ValueError(f"Could not find structural_type field")
        return alleles

    @staticmethod
    def get_gene_and_alleles(diagnosis) -> typing.Tuple[str, typing.List[str]]:
        """
        Extract the gene symbol, failing that the label, for a variant from the Interpretation object.
        Also get the alleles.
        """
        gene = None
        alleles = []
        for genomic_interpretation in diagnosis.genomic_interpretations:
            if genomic_interpretation.variant_interpretation:
                if genomic_interpretation.variant_interpretation.variation_descriptor:
                    var_desc = genomic_interpretation.variant_interpretation.variation_descriptor
                    gene = PPKtStore.get_gene_symbol(variant_descriptor=var_desc)
                    if var_desc.expressions:
                        hgvsC = ''
                        hgvsG = ''
                        for expr in var_desc.expressions:
                            if expr.syntax == 'hgvs.c':
                                hgvsC = expr.value
                            if expr.syntax == 'hgvs.g':
                                hgvsG = expr.value
                        if hgvsC:
                            alleles.append(hgvsC)
                        elif hgvsG:
                            alleles.append(hgvsG)
                    # get structural variant, if needed
                    if len(alleles) == 0:
                        alleles = PPKtStore.get_structural_var(var_desc)
                    # get genotype
                    genotype = var_desc.allelic_state
                    if genotype.label == "homozygous" and len(alleles) > 0:
                        alleles.append(alleles[0])
        return gene, alleles

    @staticmethod
    def get_gene_symbol(variant_descriptor) -> str:
        gene = None
        if variant_descriptor.HasField("gene_context"):
            gene = variant_descriptor.gene_context.symbol
        if gene is None:
            gene = variant_descriptor.label
        return gene


    @staticmethod
    def get_filename(pathname):
        os.path.sep
        fields = pathname.split(os.path.sep)
        fname = fields[-1]
        if not fname.endswith(".json"):
            raise ValueError(f"Malformed path {pathname}")
        else:
            return fname



    def _create_summary_tsv(
            self,
            tsv_file_name: str,
    ):
        column_names = ['disease', 'disease_id', 'patient_id', 'gene', 'allele_1', 'allele_2', 'PMID', 'cohort', 'filename']
        rows = []

        for cohort in self._cohorts:
            cohort_name = cohort.name
            for entry in cohort.get_detailed_dict():
                with open(entry['filename']) as f:
                    filename = os.path.basename(entry['filename'])
                    ppack = Parse(f.read(), Phenopacket())
                    if not ppack.interpretations:
                        continue
                    for interpretation in ppack.interpretations:
                        if not interpretation.diagnosis:
                            continue
                        dx = interpretation.diagnosis
                        pmid = PPKtStore.get_pmid(meta_data=ppack.meta_data)
                        gene, alleles = self.get_gene_and_alleles(diagnosis=dx)
                        if gene is None:
                            raise ValueError(f"Could not get gene string for {entry['filename']}")
                        if len(alleles) == 2:
                            allele1 = alleles[0]
                            allele2 = alleles[1]
                        elif len(alleles) == 1:
                            allele1 = alleles[0]
                            allele2 = ""
                        else:
                            raise ValueError(f"Length of alleles was {len(alleles)} for {entry['filename']}")
                        

                        rows.append(
                            {
                                column_names[0]: dx.disease.label,
                                column_names[1]: dx.disease.id,
                                column_names[2]: ppack.subject.id,
                                column_names[3]: gene,
                                column_names[4]: allele1,
                                column_names[5]: allele2,
                                column_names[6]: pmid,
                                column_names[7]: cohort_name,
                                column_names[8]: filename,
                            }
                        )
        df = pd.DataFrame.from_records(rows, columns=column_names)
        df.to_csv(
            tsv_file_name,
            sep='\t', index=False,
        )
