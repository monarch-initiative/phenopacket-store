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
                if len(lpath_components) != 3:
                    raise ValueError(f"Unexpected path with {len(lpath_components)} components: {dirpath}")
                cohort_name = lpath_components[1]
                json_files = filter(lambda f: f.endswith('.json'), filenames)
                c = Cohort(name=cohort_name, dirpath=dirpath, files=json_files)
                self._cohorts.append(c)

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
            for cohort in self._cohorts:
                temp_cohort_dir = os.path.join(tmpdirname,cohort.name)
                os.makedirs(temp_cohort_dir)
                # original files
                files = cohort.phenopacket_files
                for f in files:
                    print(f"f={f}")
                    print(f"temp_cohort_dir={temp_cohort_dir}")
                    shutil.copy(f, temp_cohort_dir)  # dst can be a folder;
            tgz_name =  tmpdirname + ".tgz"
            with tarfile.open(tgz_name, "w:gz" ) as tar:
                for name in os.listdir( tmpdirname ):
                    tar.add(name)
            shutil.copy(tgz_name, outfilename)

    def get_store_zip(self, outfilename):
        if not outfilename.endswith(".zip"):
            print("Adding zip suffix to outfilename")
            outfilename = outfilename + ".zip"
        with tempfile.TemporaryDirectory() as tmpdirname:
            for cohort in self._cohorts:
                temp_cohort_dir = os.path.join(tmpdirname,cohort.name)
                os.makedirs(temp_cohort_dir)
                # original files
                files = cohort.fnames
                for f in files:
                    print(f"f={f}")
                    infile = os.path.join(cohort.directory, f)
                    print(f"temp_cohort_dir={temp_cohort_dir}")
                    outfile = os.path.join(temp_cohort_dir, f)
                    shutil.copy(infile, outfile)
        shutil.make_archive(outfilename, 'zip', tmpdirname)





