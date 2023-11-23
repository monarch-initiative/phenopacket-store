import os
import tempfile
import shutil
import tarfile
import pandas as pd
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

    def get_store_gzip(self, outfilename):
        if not outfilename.endswith(".tgz"):
            print("Adding archive suffix to outfilename")
            outfilename = outfilename + ".tgz"
        with tempfile.TemporaryDirectory() as tmpdirname:
            n_copied_files =  self._copy_files_to_temporary_directory(tmpdirname)
            shutil.make_archive(outfilename, 'tar', tmpdirname)
            tgz_name =  tmpdirname + ".tgz"
            n_added_files = 0
            with tarfile.open(tgz_name, "w:gz" ) as tar:
                for name in os.listdir( tmpdirname ):
                    abs_path = os.path.join(tmpdirname, name)
                    tar.add(abs_path)
                    if os.path.isdir(abs_path):
                        for f in os.listdir(abs_path):
                            abs_file_path = os.path.join(abs_path, f)
                            tar.add(abs_file_path)
                            n_added_files += 1
            shutil.move(tgz_name, outfilename)
        f = os.path.abspath(os.getcwd())
        print(f"Added {n_copied_files} files to tar archive at {f}/{outfilename}")

    def get_store_zip(self, outfilename):
        if outfilename.endswith(".zip"):
            raise ValueError("Do not add .zip to file name; this is done automatically")
        with tempfile.TemporaryDirectory() as tmpdirname:
            n_copied_files =  self._copy_files_to_temporary_directory(tmpdirname)
            shutil.make_archive(outfilename, 'zip', tmpdirname)
        f = os.path.abspath(os.getcwd())
        print(f"Added {n_copied_files} files to zip archive at {f}/{outfilename}")


    def _copy_files_to_temporary_directory(self, tmpdirname) -> int:
        n_copied_files = 0
        for cohort in self._cohorts:
            temp_cohort_dir = os.path.join(tmpdirname,cohort.name)
            os.makedirs(temp_cohort_dir)
            # original files
            files = cohort.phenopacket_files
            for f in files:
                shutil.copy(f, temp_cohort_dir)
                n_copied_files += 1
        return n_copied_files






