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
[GetPhenopackets](https://github.com/monarch-initiative/phenopacket-store/blob/main/GetPhenopackets.ipynb){:target="_blank"} for details.

## Running the notebooks locally

There are several ways of doing this. We prefer the following method. First, create a virtual environment (shown here as my_venv, but choose any name you like) and activiate it. Then, install pyphetools and some packages required to run Jupyter notebooks. Use the ipykernel package to enable the use of the virtual environment in a notebook. Finally, open or create a notebook and choose the kernel

```
python3 -m venv my_venv
source my_venv/bin/activate
pip install --upgrade pip
pip install pyphetools jupyter ipykernel
python -m ipykernel install --name my_venv --user
jupyter-notebook
```

Make sure to choose the kernel called 'my_venv' in the notebook.

