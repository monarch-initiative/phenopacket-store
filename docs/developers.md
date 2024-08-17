# For developers

Phenopacket Store repository presents collections of
[GA4GH phenopackets](https://pubmed.ncbi.nlm.nih.gov/35705716){:target="_blank"}
that can be used to test phenopacket-based software.

Each collection features phenopackets representing clinical information 
about individuals with Mendelian disease-associated variants in specific genes, 
or in some case, collections of phenopackets derived from published cohorts or studies.


## pyphetools

Most of the phenopackets were created using the 
[pyphetools](https://github.com/monarch-initiative/pyphetools){:target="_blank"} library. 
Details about how the phenopackets were generated can be found in the 
[notebooks](https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks){:target="_blank"} folder. 
The folder is organized according to gene or collection.
In some cases, the phenopackets were generated with other software, 
and then we present a notebook that summarizes the phenopackets.


## Generate release archive

All phenopackets are stored in subfolders of the notebooks folder,
which is organized according to cohort.

We use [Phenopacket Store Toolkit](https://github.com/monarch-initiative/phenopacket-store-toolkit)
(`ppktstore`) to package the phenopackets into a release ZIP file.

Run the following in order to create the release ZIP archive.

First, make sure to start in the top-level folder of the phenopacket store repository.
Then, install `phenopacket-store-toolkit` in `release` profile into your active Python environment.

```shell
python3 -m pip install phenopacket-store-toolkit[release]
```

`ppktstore` comes with a command line interface (CLI) which includes the `package` command 
for generating the archive:

```shell
python3 -m ppktstore package --notebook-dir notebooks --release-tag 0.1.18 --output all_phenopackets
```

The command will collect the phenopacketes of the `notebooks` directory 
and pack the phenopackets into `all_phenopackets.zip` archive. We use `0.1.18` as the release tag.


## Running the notebooks locally

As an alternative to using the phenopackets from one of the release archives, 
the phenopackets can also be generated locally by running Jupyter notebooks.  

There are several ways of doing this and we prefer the following method. 
First, create a virtual environment (shown here as `my_venv`, but choose any name you like) and activate it. 
Then, install the following packages:

* `pyphetools` required for generating phenopackets
* `ipykernel` for using `my_venv` as a Jupyter kernel

```shell
# Create and activate the Python environment
ENV_NAME=my_venv
python3 -m venv ${ENV_NAME}
source ${ENV_NAME}/bin/activate

# Install both packages
python3 -m pip install pyphetools ipykernel

# Register the environment with Jupyter to use as a notebook kernel
python3 -m ipykernel install --user --name ${ENV_NAME} --display-name "Phenopacket Store Env"
```

After the installation, a new kernel called `Phenopacket Store Env` should be available in Jupyter. 
Use the kernel to run the notebooks at will Make sure to choose the kernel when running the notebooks 
in the [notebooks](https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks){:target="_blank"} folder.
