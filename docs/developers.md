# For developers

The phenopacket store repository presents collections of [GA4GH phenopackets](https://pubmed.ncbi.nlm.nih.gov/35705716){:target="_blank"}. that can be used to test phenopacket-based software.

Each collection features phenopackets representing clinical information about individuals with Mendelian disease-associated variants in specific genes, or in some case, collections of phenopackets derived from published cohorts or studies.

## pyphetools

Most of the phenopackets were developed using the [pyphetools](https://github.com/monarch-initiative/pyphetools){:target="_blank"} library. Details about how
the phenopackets were generated can be found in the corresponding 
[notebooks](https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks){:target="_blank"} folder 
organized according to gene or collection. 
In some cases, the phenopackets were generated with other software, and then we present 
a notebook that summarizes the phenopackets.

## Extracting all phenopackets

All phenopackets are stored in subfolders of the notebooks folder, which is organized according to cohort.

phenopacket-store has a small python package called `ppktstore` that facilitates exporting all available phenopackets. 
See [GetPhenopackets](https://github.com/monarch-initiative/phenopacket-store/blob/main/GetPhenopackets.ipynb){:target="_blank"} 
for details.

## Running the notebooks locally

As an alternative to using the phenopackets from the ZIP file, the phenopackets can also be generated locally 
by running Jupyter notebooks.  

There are several ways of doing this and we prefer the following method. 
First, create a virtual environment (shown here as `my_venv`, but choose any name you like) and activate it. 
Then, install the `ppktstore` package required for generating phenopackets, and the `ipykernel` package 
required to use `my_venv` as a Jupyter kernel:

```shell
# Create and activate the Python environment
ENV_NAME=my_env
python3 -m venv ${ENV_NAME}
source ${ENV_NAME}/bin/activate

# Install both packages
python3 -m pip install ppktstore ipykernel

# Register the environment with Jupyter to use as a notebook kernel
python3 -m ipykernel install --user --name ${ENV_NAME} --display-name "Phenopacket Store Env"
```

After the installation, a new kernel called `Phenopacket Store Env` should be available in Jupyter. 
Use the kernel to run the notebooks at will Make sure to choose the kernel when running the notebooks 
in the [notebooks](https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks){:target="_blank"} folder.

## Show the `phenopacket-store` statistics

The project includes code for showing descriptive statistics for the entire `phenopacket-store` 
as well as for the individual cohorts. The statistics can be seen in [ppktstore_stats](https://github.com/monarch-initiative/phenopacket-store/blob/main/ppktstore_stats.ipynb){:target="_blank"} notebook.

A few additional libraries must be installed into the Jupyter kernel in order to run the notebook locally. 
We demonstrate the installation below, assuming presence of a kernel described in the previous section: 

```shell
ENV_NAME=my_env
source ${ENV_NAME}/bin/activate

python3 -m pip install ppktstore[notebooks]
```

We activated the environment and installed the required libraries using `pip`. Now, the kernel is ready 
to generate the descriptive statistics.
