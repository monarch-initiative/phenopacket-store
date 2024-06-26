import os
import typing
import zipfile
import re
import numpy as np
import pandas as pd
from collections import defaultdict
import phenopackets as PPKt
from google.protobuf.json_format import Parse
from ..__init__ import __version__ as ppkt_version

    


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
        archive = zipfile.ZipFile(input_zipfile, 'r')
        self._df = PPKtStoreStats._extract_all_phenopackets_df(archive)
        self._cohort_to_phenopacket_d = PPKtStoreStats._extract_all_cohort_phenopackets(archive)
      
    def get_cohort_to_phenopacket_d(self):
        return self._cohort_to_phenopacket_d

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
                if len(fields) != 7:
                    raise ValueError(f"Malformed line with {len(fields)} fields: {L}")
                list_of_lists.append(fields)
        columns = ['disease', 'disease_id', 'patient_id', 'gene', 'allele_1', 'allele_2', 'PMID']
        return pd.DataFrame(data=list_of_lists, columns=columns)
    
    @staticmethod
    def _extract_all_cohort_phenopackets(archive: zipfile.ZipFile) -> typing.Dict:
        cohort_to_ppkt_d = defaultdict(list)
        total = 0
        for info in archive.infolist():
            if info.is_dir():
                continue
            if info.filename.endswith(".json"):
                with archive.open(info.filename) as f:
                    byte_version_of_file = f.read()
                    text_version_of_file = byte_version_of_file.decode("utf-8")
                    ppack = Parse(text_version_of_file, PPKt.Phenopacket())
                    fields = info.filename.split("/")
                    if len(fields) == 2:
                        cohort = fields[0]
                        cohort_to_ppkt_d[cohort].append(ppack)
                        total += 1
                    else:
                        print("[ERROR] Could not parse path: ", info.filename)
        print(f"Extracted {total} phenopackets in {len(cohort_to_ppkt_d)} cohorts.")
        return cohort_to_ppkt_d

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
        if cohort.endswith("/"):
            cohort = cohort[:-1]
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
        genes_to_ppkt_d = defaultdict(int)
        diseases_to_ppkt_id = defaultdict(int)
        genes_to_disease_d = defaultdict(set)
        unique_alleles = set()
        for _, row in df.iterrows():
            gene = row["gene"]
            disease_id = row["disease_id"]
            allele_1 = row["allele_1"]
            allele_2 = row["allele_2"]
            genes_to_ppkt_d[gene] += 1
            diseases_to_ppkt_id[disease_id] += 1
            genes_to_disease_d[gene].add(disease_id)
            unique_alleles.add(allele_1)
            if allele_2 is not None and allele_2.startswith("NM_"):
                unique_alleles.add(allele_2)
        stats_d = dict()
        stats_d["version"] = ppkt_version
        stats_d["phenopackets"] = len(df)
        stats_d["diseases"] = len(df["disease_id"].unique())
        stats_d["genes"] = len(df["gene"].unique())

        stats_d["alleles"] = len(unique_alleles)
        stats_d["PMIDs"] = len(df["PMID"].unique())
        individuals_per_disease = list(diseases_to_ppkt_id.values())
        stats_d["individuals per disease (max)"] = np.max(individuals_per_disease)
        stats_d["individuals per disease (min)"] = np.min(individuals_per_disease)
        stats_d["individuals per disease (mean)"] = np.mean(individuals_per_disease)
        stats_d["individuals per disease (median)"] = np.median(individuals_per_disease)
        #stats_d["individuals per disease (n>=10)"] = len([x for x in individuals_per_disease if x >= 10])
        #stats_d["individuals per disease (n>=20)"] = len([x for x in individuals_per_disease if x >= 20])
        #stats_d["individuals per disease (n>=50)"] = len([x for x in individuals_per_disease if x >= 50])
       # stats_d["individuals per disease (n>=100)"] = len([x for x in individuals_per_disease if x >= 100])
        # Some genes are associated with multiple diseases
        gene_by_disease_df = df[['gene', 'disease_id']].drop_duplicates()
        gbd_counts_df = gene_by_disease_df.groupby('disease_id').count().value_counts(ascending=False).reset_index(name='count')
        stats_d["genes associated with a single disease"] = len([x for x in genes_to_disease_d.keys() if len(genes_to_disease_d[x]) == 1])
        stats_d["genes associated with two diseases"] = len([x for x in genes_to_disease_d.keys() if len(genes_to_disease_d[x]) == 2])
        stats_d["genes associated with multiple diseases"] = len([x for x in genes_to_disease_d.keys() if len(genes_to_disease_d[x]) > 2])
        max_gene = None
        max_count = 0
        for k,v in genes_to_disease_d.items():
            n_diseases = len(v)
            if n_diseases > max_count:
                max_count = n_diseases
                max_gene = k
        max_msg = f"{max_gene} with {max_count} associated diseases"
        stats_d["gene with maximum number of diseases"] = max_msg
        individuals_per_gene = list(genes_to_ppkt_d.values())
        #stats_d["individuals per gene (max)"] = np.max(individuals_per_gene)
       # stats_d["individuals per gene (min)"] = np.min(individuals_per_gene)
        #stats_d["individuals per gene (mean)"] = np.mean(individuals_per_gene)
        #stats_d["individuals per gene (median)"] = np.median(individuals_per_gene)
       # stats_d["individuals per gene (n>=10)"] = len([x for x in individuals_per_gene if x >= 10])
        #stats_d["individuals per gene (n>=20)"] = len([x for x in individuals_per_gene if x >= 20])
        #stats_d["individuals per gene (n>=50)"] = len([x for x in individuals_per_gene if x >= 50])
       # stats_d["individuals per gene (n>=100)"] = len([x for x in individuals_per_gene if x >= 100])
        all_hpo_d = self.get_all_unique_hpo_d()
        total_hpo = len(all_hpo_d)
        stats_d["total HPO terms used"] = total_hpo

        return stats_d
    

    def get_counts_per_disease(self) -> typing.Dict[str,int]:
        disease_to_count_d = defaultdict(int)
        for ppkt_list in self._cohort_to_phenopacket_d.values():
            for ppkt in ppkt_list:
                if len(ppkt.diseases) == 0:
                    raise ValueError(f"Empty disease list")
                if len(ppkt.diseases) != 1:
                    print("Warning, number of diseases ", len(ppkt.diseases))
                disease_id = ppkt.diseases[0].term.id
                disease_to_count_d[disease_id] += 1
        return disease_to_count_d
    
    def get_counts_per_disease_df(self) -> pd.DataFrame:
        disease_to_count_d = self.get_counts_per_disease()
        items = list()
        for k,v in disease_to_count_d.items():
            items.append({"disease":k, "count": v})
        return pd.DataFrame(items, index=None)
            



    def get_all_unique_hpo_d(self) -> typing.Dict[str,str]:
        """return a dictionary with key=HPO id, value=label of all HPOs used in phenopacket-store
        """
        all_hpo_d = dict()
        for ppkt_list in self._cohort_to_phenopacket_d.values():
            for ppkt in ppkt_list:
                for pf in ppkt.phenotypic_features:
                    all_hpo_d[pf.type.id] = pf.type.label
        print(f"Got {len(all_hpo_d)} unique HPOs")
        return all_hpo_d
    

    def check_disease_id(self):
        """
        Check the entire dataset for erroneous disease identifiers (i.e., not conforming to OMIM or MONDO ids)
        """
        invalid_list = list()
        OMIM_REGEX = r"^OMIM:\d{6}$"
        MONDO_REGEX = r"^MONOD:\d+$"
        for _, row in self._df.iterrows():
            disease_id = row["disease_id"]
            disease_label = row["disease"]
            individual_id = row["patient_id"]
            PMID = row["PMID"]
            omim_match = re.search(OMIM_REGEX, disease_id)
            mondo_match = re.search(MONDO_REGEX, disease_id)
            if not omim_match and not mondo_match:
                invalid_list.append({"disease_id": disease_id, "label": disease_label, "individual_id": individual_id, 'PMID': PMID})
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
    def _get_gene(ppkt:PPKt.Phenopacket) -> str:
        for interpretation in ppkt.interpretations:
            if interpretation.HasField("diagnosis"):
                dx = interpretation.diagnosis
                for gi in dx.genomic_interpretations:
                    if gi.HasField("variant_interpretation"):
                        vi = gi.variant_interpretation
                        if vi.HasField("variation_descriptor"):
                            vdesc = vi.variation_descriptor
                            return vdesc.gene_context.symbol
        return "na"

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
                            if vdesc.HasField("structural_type"):
                                stillLookingForVar = False
                                continue
                            elif vdesc.HasField("vcf_record"):
                                # This is the case with the LIRICAL variants
                                stillLookingForVar = False
                                continue
                            for e in vdesc.expressions:
                                if e.syntax == "hgvs.c":
                                    var_list.append(e.value)
                                    stillLookingForVar = False
                            if stillLookingForVar:
                                try:
                                    if len(vdesc.label) > 0:
                                        var_list.append(vdesc.label)
                                        stillLookingForVar = False
                                except:
                                    pass
                    if stillLookingForVar:
                        print(f"[WARNING] could not find variant for phenopacket {ppkt.id}")
        return var_list
    

    def get_disease_to_phenopacket_count_d(self) -> typing.Dict[str, int]:
        disease_to_ppkt_count_d = defaultdict(int)
        for ppkt_list in self._cohort_to_phenopacket_d.values():
            for ppkt in ppkt_list:
                if len(ppkt.diseases) != 1:
                    print(f"Warning: Got {len(ppkt.diseases)} for {ppkt.id}. Skipping")
                    continue
                disease_id = ppkt.diseases[0].term.id
                disease_to_ppkt_count_d[disease_id] += 1
        print(f"Extracted a total of {len(disease_to_ppkt_count_d)} diseases")
        return disease_to_ppkt_count_d
    
    def _get_gene_symbol(self, ppkt) -> str:
        if len(ppkt.interpretations) == 0:
            print(f"Warning: Got no interpretations for {ppkt.id}. Skipping")
            return None
        try:
            interpretation = ppkt.interpretations[0]
            dx = interpretation.diagnosis
            g_interpretation = dx.genomic_interpretations[0]
            vi = g_interpretation.variant_interpretation
            vdesc = vi.variation_descriptor
            gene_symbol = vdesc.gene_context.symbol
            return gene_symbol
        except Exception as ee:
            print(f"Warning: Got no gene symbbol for {ppkt.id} because of {str(ee)}. Skipping")
        return None
    
    def get_gene_to_phenopacket_count_d(self) -> typing.Dict[str, int]:
        gene_to_ppkt_count_d = defaultdict(int)
        for ppkt_list in self._cohort_to_phenopacket_d.values():
            for ppkt in ppkt_list:
                gene_symbol = self._get_gene_symbol(ppkt=ppkt)
                if gene_symbol is not None:
                    gene_to_ppkt_count_d[gene_symbol] += 1
                else:
                    print(f"[ERROR] Count not identify gene for phenopacket {ppkt.id}")
        print(f"Extracted a total of {len(gene_to_ppkt_count_d)} genes")
        return gene_to_ppkt_count_d



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

    def show_possible_duplicates_by_variant(self, input_zipfile, cohort) -> pd.DataFrame:
        if not os.path.isfile(input_zipfile):
            raise FileNotFoundError(f"Not a file: {input_zipfile}")
        if not input_zipfile.endswith(".zip"):
            raise ValueError(f"`input_zipfile` must point to a ZIP archive with suffix .zip, but was \"{input_zipfile}\"")
        ppkt_list =  PPKtStoreStats._extract_specific_cohort_phenopackets_df(zipfile.ZipFile(input_zipfile, 'r'), cohort=cohort)
        item_list = self._get_possible_duplicates_by_variant(ppkt_list=ppkt_list)
        if len(item_list) == 0:
            print(f"No candidate duplicates found for {cohort}")
        return pd.DataFrame(item_list)

    def show_phenopackets_with_gene(self, input_zipfile, cohort, gene_symbol) -> pd.DataFrame:
        ppkt_with_gene_lst = list()
        if not os.path.isfile(input_zipfile):
            raise FileNotFoundError(f"Not a file: {input_zipfile}")
        if not input_zipfile.endswith(".zip"):
            raise ValueError(f"`input_zipfile` must point to a ZIP archive with suffix .zip, but was \"{input_zipfile}\"")
        ppkt_list =  PPKtStoreStats._extract_specific_cohort_phenopackets_df(zipfile.ZipFile(input_zipfile, 'r'), cohort=cohort)
        for ppkt in ppkt_list:
            symbol = PPKtStoreStats._get_gene(ppkt=ppkt)
            if symbol == gene_symbol:
                ppkt_with_gene_lst.append({"gene": gene_symbol, "phenopacket": ppkt.id})
        return pd.DataFrame(ppkt_with_gene_lst)


    def _get_possible_duplicates_by_variant(self, ppkt_list) -> typing.List[typing.Dict[str,str]]:
        """
        This function identifies cohorts in which some variant is present more than once. Usually, this just means
        that the same variant was found in different individuals. We have used this function to identify cohorts
        for focussed checks to identify potential duplicates, which were removed.
        """
        variant_to_ppkt_id_d = defaultdict(list)
        for ppkt in ppkt_list:
            varlist = PPKtStoreStats._get_variant_list(ppkt=ppkt)
            for v in varlist:
                variant_to_ppkt_id_d[v].append(ppkt.id)
        item_list = list()
        for variant, patient_id_list in variant_to_ppkt_id_d.items():
            if len(patient_id_list) == 1:
                continue ## cannot be duplicate
            for pat_id in patient_id_list:
                item_list.append({"variant": variant, "individual_id": pat_id})
        return item_list

    def show_cohorts_with_possible_duplicates(self, input_zipfile) -> pd.DataFrame:
        cohorts = PPKtStoreStats._get_list_of_cohorts(zipfile.ZipFile(input_zipfile, 'r'))
        cohort_list = list()
        for cohort in cohorts:
            print(cohort)
            ppkt_list =  PPKtStoreStats._extract_specific_cohort_phenopackets_df(zipfile.ZipFile(input_zipfile, 'r'), cohort=cohort)
            item_list = self._get_possible_duplicates_by_variant(ppkt_list=ppkt_list)
            if len(item_list) == 0:
                continue
            else:
                for i in item_list:
                    i["cohort"] = cohort
                    cohort_list.append(i)
        return pd.DataFrame(cohort_list)



    def find_phenopackets_with_no_variants(self, input_zipfile) -> pd.DataFrame:
        if not os.path.isfile(input_zipfile):
            raise FileNotFoundError(f"Not a file: {input_zipfile}")
        if not input_zipfile.endswith(".zip"):
            raise ValueError(f"`input_zipfile` must point to a ZIP archive with suffix .zip, but was \"{input_zipfile}\"")
        ppkt_with_no_var_list = list()
        all_cohort_names = PPKtStoreStats._get_list_of_cohorts(zipfile.ZipFile(input_zipfile, 'r'))
        for cohort in all_cohort_names:
            ppkt_list =  PPKtStoreStats._extract_specific_cohort_phenopackets_df(zipfile.ZipFile(input_zipfile, 'r'), cohort=cohort)
            for ppkt in ppkt_list:
                if len(ppkt.interpretations) == 0:
                    ppkt_with_no_var_list.append({"cohort": cohort, "phenopacket": ppkt.id})
        if len(ppkt_with_no_var_list) == 0:
            print("All phenopackets had at least one variant")
        return pd.DataFrame(ppkt_with_no_var_list)
    
    def find_phenopackets_with_no_disease(self, input_zipfile) -> pd.DataFrame:
        if not os.path.isfile(input_zipfile):
            raise FileNotFoundError(f"Not a file: {input_zipfile}")
        if not input_zipfile.endswith(".zip"):
            raise ValueError(f"`input_zipfile` must point to a ZIP archive with suffix .zip, but was \"{input_zipfile}\"")
        ppkt_with_disease_list = list()
        all_cohort_names = PPKtStoreStats._get_list_of_cohorts(zipfile.ZipFile(input_zipfile, 'r'))
        for cohort in all_cohort_names:
            ppkt_list =  PPKtStoreStats._extract_specific_cohort_phenopackets_df(zipfile.ZipFile(input_zipfile, 'r'), cohort=cohort)
            for ppkt in ppkt_list:
                if len(ppkt.diseases) == 0:
                    ppkt_with_disease_list.append({"cohort": cohort, "phenopacket": ppkt.id})
        if len(ppkt_with_disease_list) == 0:
            print("All phenopackets had a disease diagnosis")
        return pd.DataFrame(ppkt_with_disease_list)


