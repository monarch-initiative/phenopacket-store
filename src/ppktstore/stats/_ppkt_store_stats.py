import os
import typing
import zipfile
import re
import numpy as np
import pandas as pd
from collections import defaultdict
import phenopackets as PPKt
from google.protobuf.json_format import Parse

class PPKtStoreStats:
    """Calculate descriptive statistics about the phenopackets in the repository and generate figures to illustrate distributions.
    """

    def __init__(self, input_zipfile: str) -> None:
        """input a dataframe with the data about the release
        In a typical use case this class would be used to check the release prior to uploading the file to GitHub.

        Args:
            input_zipfile (str): Path to the release archive (ZIP) for phenoapcket-store

        Raises:
            FileNotFoundError: if file cannot be found
            ValueError: if the file does not end with the suffix ".zip"
        """
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

    @staticmethod
    def _extract_specific_cohort_phenopackets_df(
            archive: zipfile.ZipFile,
            cohort:str
    ) -> typing.List[PPKt.Phenopacket]:
        """Files that belong to a specific cohort, e.g., LIRICAL, will be identifiable as
              LIRICAL/PMID_123_individual1.json


        Args:
            archive (zipfile.ZipFile): archive with all zipped files
            cohort (str): name of cohort (should be equal to one of the folders of phenopacket-store)

        Raises:
            FileNotFoundError: if the archive zip file cannot be found

        Returns:
            pd.DataFrame: _description_
        """
        all_ppkt = None
        for info in archive.infolist():
            if info.is_dir():
                continue
            if info.filename == "all_phenopackets.tsv":
                all_ppkt = info
                break
        if all_ppkt is None:
            raise FileNotFoundError("Could not find \"all_phenopackets.tsv\" in zip archive")
        list_of_phenopackets = list()
        regex = f"{cohort}/.*\.json"
        with archive.open(all_ppkt) as f:
            for info in archive.infolist():
                match = re.search(regex, info.filename)
                if match:
                    with archive.open(info.filename) as f:
                        byte_version_of_file = f.read()
                        text_version_of_file = byte_version_of_file.decode("utf-8")
                        ppack = Parse(text_version_of_file, PPKt.Phenopacket())
                        list_of_phenopackets.append(ppack)
        return list_of_phenopackets

    @staticmethod
    def _get_list_of_cohorts(
            archive: zipfile.ZipFile,
    ) -> pd.DataFrame:
        all_cohort_names = list()
        for info in archive.infolist():
            if info.is_dir():
                all_cohort_names.append(info.filename)
        return all_cohort_names

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

    def check_disease_id(self):
        invalid_list = list()
        OMIM_REGEX = r"^OMIM:\d{6}$"
        MONDO_REGEX = r"^MONOD:\d+$"
        for _, row in self._df.iterrows():
            disease_id = row["disease_id"]
            disease_label = row["disease"]
            omim_match = re.search(OMIM_REGEX, disease_id)
            mondo_match = re.search(MONDO_REGEX, disease_id)
            if not omim_match and not mondo_match:
                invalid_list.append({"disease_id": disease_id, "label": disease_label})
        if len(invalid_list) == 0:
            print ("No problems found.")
            return  pd.DataFrame(["disease_id", "label"])
        else:
            print(f"Found {len(invalid_list)} problematic disease identifiers")
            return pd.DataFrame(invalid_list)


    @staticmethod
    def _get_disease_name(ppkt:PPKt.Phenopacket) -> typing.Tuple[str,str]:
        if len(ppkt.diseases) == 1:
            disease = ppkt.diseases[0]
            label = disease.term.label
            disease_id = disease.term.id
            return label, disease_id
        else:
            raise ValueError(f"Cannot use this method for phenopackets with no or with multiple diseases (n={len(ppkt.diseases)})")


    @staticmethod
    def _get_variant_list(ppkt:PPKt.Phenopacket) -> typing.List[str]:
        var_list = list()
        for interpretation in ppkt.interpretations:
            if interpretation.HasField("diagnosis"):
                dx = interpretation.diagnosis
                for gi in dx.genomic_interpretations:
                    stillLookingForVar = True
                    if gi.HasField("variant_interpretation"):
                        vi = gi.variant_interpretation
                        if vi.HasField("variation_descriptor"):
                            vdesc = vi.variation_descriptor
                            for e in vdesc.expressions:
                                if e.syntax == "hgvs.c":
                                    var_list.append(e.value)
                                    stillLookingForVar = False
                            if stillLookingForVar:
                                if vdesc.HasField("label"):
                                    var_list.append(vdesc.label)
                                    stillLookingForVar = False
                    if stillLookingForVar:
                        var_list.append("could not find variant")
        return var_list


    def count_diseases_in_cohort(self, input_zipfile, cohort) -> pd.DataFrame:
        if not os.path.isfile(input_zipfile):
            raise FileNotFoundError(f"Not a file: {input_zipfile}")
        if not input_zipfile.endswith(".zip"):
            raise ValueError(f"`input_zipfile` must point to a ZIP archive with suffix .zip, but was \"{input_zipfile}\"")
        ppkt_list =  PPKtStoreStats._extract_specific_cohort_phenopackets_df(zipfile.ZipFile(input_zipfile, 'r'), cohort=cohort)
        disease_id_to_label_d = dict()
        disease_counter_d = defaultdict(int)
        for ppkt in ppkt_list:
            label, disease_id = PPKtStoreStats._get_disease_name(ppkt=ppkt)
            disease_counter_d[disease_id] += 1
            disease_id_to_label_d[disease_id] = label
        item_list = list()
        for k,v in disease_counter_d.items():
            label = disease_id_to_label_d.get(k)
            d = {"disease_id":k, "label":label, "count": v}
            item_list.append(d)
        df = pd.DataFrame(item_list)
        df.sort_values(by=['count'], ascending=False, inplace=True)
        df.set_index("disease_id", inplace=True)
        return df

    def show_phenopacket_ids_by_variant_in_cohort(self, input_zipfile, cohort) -> pd.DataFrame:
        if not os.path.isfile(input_zipfile):
            raise FileNotFoundError(f"Not a file: {input_zipfile}")
        if not input_zipfile.endswith(".zip"):
            raise ValueError(f"`input_zipfile` must point to a ZIP archive with suffix .zip, but was \"{input_zipfile}\"")
        ppkt_list =  PPKtStoreStats._extract_specific_cohort_phenopackets_df(zipfile.ZipFile(input_zipfile, 'r'), cohort=cohort)
        variant_to_ppkt_id_d = defaultdict(list)
        for ppkt in ppkt_list:
            varlist = PPKtStoreStats._get_variant_list(ppkt=ppkt)
            for v in varlist:
                variant_to_ppkt_id_d[v].append(ppkt.id)
        item_list = list()
        for variant, patient_id_list in variant_to_ppkt_id_d.items():
            for pat_id in patient_id_list:
                item_list.append({"variant": variant, "individual_id": pat_id})
        return pd.DataFrame(item_list)

    def find_phenopackets_with_no_variants(self, input_zipfile) -> typing.List[str]:
        if not os.path.isfile(input_zipfile):
            raise FileNotFoundError(f"Not a file: {input_zipfile}")
        if not input_zipfile.endswith(".zip"):
            raise ValueError(f"`input_zipfile` must point to a ZIP archive with suffix .zip, but was \"{input_zipfile}\"")
        ppkt_with_no_var_list = list()
        all_cohort_names = PPKtStoreStats._get_list_of_cohorts(zipfile.ZipFile(input_zipfile, 'r'))
        for cohort in all_cohort_names:
            ppkt_list =  PPKtStoreStats._extract_specific_cohort_phenopackets_df(zipfile.ZipFile(input_zipfile, 'r'), cohort=cohort)
            for ppkt in ppkt_list:
                var_list = PPKtStoreStats._get_variant_list(ppkt=ppkt)
                if len(var_list) == 0:
                    ppkt_with_no_var_list.append({"cohort": cohort, "phenopacket": ppkt.id})
        return pd.DataFrame(ppkt_with_no_var_list)


