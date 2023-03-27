# c2s2-clin
C2S2 Clinical Data

Let's use this site to collect the Python scripts we will uses to create phenopackets to validate C2S2.

This repository contains notebooks and original data used to generate the GA4GH phenopackets used in the [C2C2](https://github.com/monarch-initiative/C2S2) project, in which we analyze cohorts of individuals with variants in genes for the presence of subgroups (for instance, germline mutations in SMARCB1 are associarteds with the diseases Coffin-Siris syndrome 3, Rhabdoid tumor predisposition syndrome 1, and Schwannomatosis-1, susceptibility to).

## Setup
This package requires  [pyphentools](https://pypi.org/project/pyphetools/), which can be installed from PyPI:
```
pip install pyphetools --upgrade
```
Alternatively, to co-develop features in pyphetools and this project, one can do a local install as follows (after cd'ing to the pyphetools )
```
 pip install -e .
 ```
 

## Genes
Add data for phenopackets for each of the genes to the following subdirectories:

1. [SMARCB1](notebooks/SMARCB1/)
2. [ANKH](notebooks/ANKH/)
3. [WFS1](notebooks/WFS1)
4. [SON](notebooks/SON)
5. [COL3A1](notebooks/COL3A1)
6. [OPD1](notebooks/OPD1)
