# For developers

The phenopacket store repository presents collections of [GA4GH phenopackets](https://pubmed.ncbi.nlm.nih.gov/35705716){:target="_blank"}. that can be used to test phenopacket-based software.

Each collection features phenopackets representing clinical infomration about individuals with Mendelian disease-associated variants in specific genes, or in some case, collections of phenopackets derived from published cohorts or studies.

## pyphetools

Most of the phenopackets were developed using the [pyphetools](https://github.com/monarch-initiative/pyphetools) library. Details about how
the phenopackets were generated can be found in the corresponding [notebooks](https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks){:target="_blank"} folder organized according to gene or collection. In some cases, the phenopackets were generated with
other software, and then we present a notebook that summarizes the phenopackets.

All phenopackets are stored in the [phenpackets](https://github.com/monarch-initiative/phenopacket-store/tree/main/phenopackets){:target="_blank"} subfolder, also organized according to
gene.

There are many ways to collect all phenopackets from all of the subfolders. Here is a simple example in Python.


```
import os
import random

path_to_phenopackets_folder = "phenopackets" # adjust as needed

def get_all_phenopackets(top_level_dir):
    phenopacket_list = []
    for dir in os.listdir(top_level_dir):
        dirpath = os.path.join(top_level_dir, dir)
        for file in os.listdir(dirpath):
            path_to_phenopacket = os.path.join(dir, file)
            phenopacket_list.append(path_to_phenopacket)
    return phenopacket_list


pheno_pack_list = get_all_phenopackets(path_to_phenopackets_folder)

print(f"Found a total of {len(pheno_pack_list)} phenopackets.")
print("Here is a random sample of 10 entries:")
for f in random.sample(pheno_pack_list, 10):
    print(f)
```

This will produce output such as the following.

```
Found a total of 1508 phenopackets.
Here is a random sample of 10 entries
STXBP1/PMID_35190816_STX_26633542_No_ID_2.json
STXBP1/PMID_35190816_STX_32139178_Patient_Neonatal26.json
PPP2R1A/PMID_37761890_6.json
SCN2A/phenopacket_fam299.json
SCN2A/phenopacket_fam46.json
SCN2A/phenopacket_fam420.json
LMNA/Novelli_2002_12075506-FAM1-VII:1.json
FBN1/PMID_10756346_D46.json
SMARCC2/PMID_37551667_Ind-01.json
SUOX/PMID_36303223_individual_4_PMID_12112661.json
```