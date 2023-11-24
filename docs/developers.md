# For developers

The phenopacket store repository presents collections of [GA4GH phenopackets](https://pubmed.ncbi.nlm.nih.gov/35705716){:target="_blank"}. that can be used to test phenopacket-based software.

Each collection features phenopackets representing clinical infomration about individuals with Mendelian disease-associated variants in specific genes, or in some case, collections of phenopackets derived from published cohorts or studies.

## pyphetools

Most of the phenopackets were developed using the [pyphetools](https://github.com/monarch-initiative/pyphetools) library. Details about how
the phenopackets were generated can be found in the corresponding [notebooks](https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks){:target="_blank"} folder organized according to gene or collection. In some cases, the phenopackets were generated with
other software, and then we present a notebook that summarizes the phenopackets.

## Extracting all phenopackets

All phenopackets are stored in subfolders of the notebooks folder, which is organized according to cohort.

phenopacket-store has a small python package that facilitates exporting all available phenopackets. See
[](https://github.com/monarch-initiative/phenopacket-store/blob/main/GetPhenopackets.ipynb){:target="_blank"} for details.

