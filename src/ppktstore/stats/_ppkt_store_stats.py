import os
import typing
import zipfile

import numpy as np
import pandas as pd


class PPKtStoreStats:

    def __init__(self, input_zipfile: str) -> None:
        if not os.path.isfile(input_zipfile):
            raise FileNotFoundError(f"Not a file: {input_zipfile}")
        if not input_zipfile.endswith(".zip"):
            raise ValueError(f"`input_zipfile` must point to a ZIP archive with suffix .zip, but was \"{input_zipfile}\"")
        self._df = self._extract_all_phenopackets_df(zipfile.ZipFile(input_zipfile, 'r'))

    @staticmethod
    def _extract_all_phenopackets_df(
            archive: zipfile.ZipFile,
    ) -> pd.DataFrame:
        all_ppkt = None
        for info in archive.infolist():
            if info.is_dir():
                continue
            if info.filename == "all_phenopackets.tsv":
                all_ppkt = info
                break
        if all_ppkt is None:
            raise FileNotFoundError("Could not find \"all_phenopackets.tsv\" in zip archive")
        with archive.open(all_ppkt) as f:
            list_of_lists = list()
            firstLine = True
            for line in f:
                if firstLine:
                    firstLine = False
                    continue
                L = line.decode("utf-8")
                fields = L.strip().split("\t")
                list_of_lists.append(fields)
        columns = ['disease', 'disease_id', 'patient_id', 'gene', 'allele_1', 'allele_2', ' PMID']
        return pd.DataFrame(data=list_of_lists, columns=columns)

    def get_df(self) -> pd.DataFrame:
        return self._df

    def get_descriptive_stats(self) -> typing.Mapping[str, typing.Any]:
        df = self._df
        stats_d = dict()
        stats_d["phenopackets"] = len(df)
        stats_d["diseases"] = len(df["disease_id"].unique())
        stats_d["genes"] = len(df["gene"].unique())
        # filter for len greater than 2 to avoid empties or na in allele_2 column
        unique_a1 = [a for a in df["allele_1"].unique() if a is not None and len(a) > 2]
        unique_a2 = [a for a in df["allele_2"].unique() if a is not None and len(a) > 2]
        unique_alleles = set(unique_a1)
        unique_alleles.update(unique_a2)
        stats_d["alleles"] = len(unique_alleles)
        stats_d["PMIDs"] = len(df[" PMID"].unique())
        individuals_per_disease = self.get_counts_per_disease()
        stats_d["individuals per disease (max)"] = np.max(individuals_per_disease)
        stats_d["individuals per disease (min)"] = np.min(individuals_per_disease)
        stats_d["individuals per disease (mean)"] = np.mean(individuals_per_disease)
        stats_d["individuals per disease (median)"] = np.median(individuals_per_disease)
        stats_d["individuals per disease (n>=10)"] = len([x for x in individuals_per_disease if x >= 10])
        stats_d["individuals per disease (n>=20)"] = len([x for x in individuals_per_disease if x >= 20])
        stats_d["individuals per disease (n>=50)"] = len([x for x in individuals_per_disease if x >= 50])
        stats_d["individuals per disease (n>=100)"] = len([x for x in individuals_per_disease if x >= 100])
        # Some genes are associated with multiple diseases
        gene_by_disease_df = df[['gene', 'disease_id']].drop_duplicates()
        gbd_counts_df = gene_by_disease_df['gene'].value_counts(ascending=False).reset_index(name='count')
        stats_d["genes associated with a single disease"] = len([x for x in gbd_counts_df["count"] if x == 1])
        stats_d["genes associated with two diseases"] = len([x for x in gbd_counts_df["count"] if x == 2])
        stats_d["genes associated with multiple diseases"] = len([x for x in gbd_counts_df["count"] if x > 1])
        max_gene = gbd_counts_df.iloc[0]["gene"]
        max_count = gbd_counts_df.iloc[0]["count"]
        max_msg = f"{max_gene} with {max_count} associated diseases"
        stats_d["gene with maximum number of diseases"] = max_msg
        ipg_df = df['gene'].value_counts(ascending=False).reset_index(name='count')
        individuals_per_gene = np.array(ipg_df["count"].to_list())
        stats_d["individuals per gene (max)"] = np.max(individuals_per_gene)
        stats_d["individuals per gene (min)"] = np.min(individuals_per_gene)
        stats_d["individuals per gene (mean)"] = np.mean(individuals_per_gene)
        stats_d["individuals per gene (median)"] = np.median(individuals_per_gene)
        stats_d["individuals per gene (n>=10)"] = len([x for x in individuals_per_gene if x >= 10])
        stats_d["individuals per gene (n>=20)"] = len([x for x in individuals_per_gene if x >= 20])
        stats_d["individuals per gene (n>=50)"] = len([x for x in individuals_per_gene if x >= 50])
        stats_d["individuals per gene (n>=100)"] = len([x for x in individuals_per_gene if x >= 100])

        return stats_d

    def get_counts_per_disease(self) -> pd.Series:
        return self._df['disease_id'].value_counts(ascending=False)
