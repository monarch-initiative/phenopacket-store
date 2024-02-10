import os
import shutil
import tarfile
import tempfile

import pandas as pd
from google.protobuf.json_format import Parse
from phenopackets import Phenopacket

from .cohort import Cohort


class PPKtStore:

    def __init__(self, notebook_dir) -> None:
        if not os.path.isdir(notebook_dir):
            raise ValueError(f"Could not find phenopacket notebook directory at {notebook_dir}")
        self._cohorts = []
        for (dirpath, dirnames, filenames) in os.walk(notebook_dir):
            if dirpath.endswith("phenopackets") and not dirpath.endswith("v1phenopackets"):
                lpath_components = dirpath.split(os.sep)
                cohort_name = self._get_cohort_name(lpath_components)
                json_files = filter(lambda f: f.endswith('.json'), filenames)
                c = Cohort(name=cohort_name, dirpath=dirpath, files=json_files)
                self._cohorts.append(c)

    def _get_cohort_name(self, lpath_components):
        if len(lpath_components) < 3:
            raise ValueError(f"Unexpected path with {len(lpath_components)} components: {dirpath}")
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

    def get_store_gzip(self, outfilename: str, flat=False):
        tsvFileName = outfilename + '.tsv'
        if not outfilename.endswith(".tgz"):
            print("Adding archive suffix to outfilename")
            outfilename = outfilename + ".tgz"
        with tempfile.TemporaryDirectory() as tmpdirname:
            n_copied_files = self._copy_files_to_temporary_directory(tmpdirname, flat)
            self._create_tsv_file(os.path.join(tmpdirname, tsvFileName))

            with tarfile.open(outfilename, "w:gz") as tar:
                tar.add(tmpdirname, arcname='.')
        print(f"Added {n_copied_files} files to tar archive {outfilename}")

    def get_store_zip(self, outfilename: str, flat=False):
        tsvFileName = outfilename + '.tsv'
        if outfilename.endswith(".zip"):
            raise ValueError("Do not add .zip to file name; this is done automatically")
        with tempfile.TemporaryDirectory() as tmpdirname:
            n_copied_files = self._copy_files_to_temporary_directory(tmpdirname, flat)
            self._create_tsv_file(os.path.join(tmpdirname, tsvFileName))

            shutil.make_archive(outfilename, 'zip', tmpdirname)
        f = os.path.abspath(os.getcwd())
        print(f"Added {n_copied_files} files to zip archive at {f}/{outfilename}")

    def _copy_files_to_temporary_directory(self, tmpdirname: str, flat=False) -> int:
        n_copied_files = 0
        for cohort in self._cohorts:
            temp_cohort_dir = tmpdirname
            if not flat:
                temp_cohort_dir = os.path.join(tmpdirname, cohort.name)
                os.makedirs(temp_cohort_dir)
            # original files
            files = cohort.phenopacket_files
            for f in files:
                shutil.copy(f, temp_cohort_dir)
                n_copied_files += 1
        return n_copied_files

    def _create_tsv_file(self, tsvFileName: str):
        column_names = ['disease', 'disease_id', 'patient_id', 'gene', 'allele_1', 'allele_2', 'PMID']
        rows = []

        for cohort in self._cohorts:
            for entry in cohort.get_detailed_dict():
                with open(entry['filename']) as f:
                    ppack = Parse(f.read(), Phenopacket())
                    if not ppack.interpretations:
                        continue
                    for interpretation in ppack.interpretations:
                        if not interpretation.diagnosis:
                            continue
                        dx = interpretation.diagnosis
                        gene = cohort
                        if genomic_interpretation.variant_interpretation:
                            if genomic_interpretation.variant_interpretation.variation_descriptor:
                                if genomic_interpretation.variant_interpretation.variation_descriptor.gene_context:
                                    if genomic_interpretation.variant_interpretation.variation_descriptor.gene_context.symbol:
                                        gene = genomic_interpretation.variant_interpretation.variation_descriptor.gene_context.symbol
                        pmid = ''
                        if ppack.meta_data.external_references:
                            pmid = ppack.meta_data.external_references[0].id
                        else:
                            print('Warning: Cannot extract PMID from [{}] in cohort: {}'.format(entry['filename'],
                                                                                                cohort))

                        for genomic_interpretation in dx.genomic_interpretations:
                            newRow = {
                                column_names[0]: dx.disease.label,
                                column_names[1]: dx.disease.id,
                                column_names[2]: ppack.subject.id,
                                column_names[3]: gene,
                                column_names[4]: '',
                                column_names[5]: '',
                                column_names[6]: pmid
                            }
                            rows.append(newRow)
        df = pd.DataFrame.from_records(rows, columns=column_names)
        with open(tsvFileName, 'w') as write_tsv:
            write_tsv.write(df.to_csv(sep='\t', index=False))
