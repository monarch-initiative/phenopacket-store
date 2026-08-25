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

## Update the HPO version

The Phenopacket Store Q/C pipeline uses HPO to prevent usage of the obsolete terms, the annotation consistency, and several other checks.
The checks are run using a specific HPO release.

The HPO version should be updated periodically to keep Phenopacket Store up-to-date. However, the version update can lead to Q/C issues that were not present with the older HPO. Therefore, the versions should be updated within a pull request (PR) that addresses all the Q/C issues. Here we show how to do this in a shell script.

We will need a terminal window with Python 3.12 or better.

To start, we install the [phenopacket-store-toolkit](https://github.com/monarch-initiative/phenopacket-store-toolkit) package.

```shell
python3 -m pip install phenopacket-store-toolkit[release]
```

The package performs the Q/C with an HPO release of interest (e.g. `v2026-06-23` in this example):

```shell
python3 -m ppktstore qc --notebook-dir notebooks --hpo-release v2026-06-23
```
> The HPO version must correspond to one of the HPO release tags
> listed on the [HPO release](https://github.com/obophenotype/human-phenotype-ontology/tags) site.

The `qc` command scans the notebook directory for the phenopackets, runs the Q/C, and displays the errors and warnings in the terminal.
An example output is listed here:

```
▸ notebooks
  ▸ SEC61A1
    ▸ 4
      ▸ phenotypic_features
          errors:
          • annotation to Gingivitis [HP:0000230] (#11) is redundant due to annotation to Recurrent gingivitis [HP:0034284] (#7)
  ▸ RFXAP
    ▸ 2
      ▸ phenotypic_features
        ▸ 6
          ▸ type
            ▸ id
                errors:
                • `HP:0003347` has been deprecated
```

Two issues are reported. The first issue describes a redundant phenotypic feature in the phenopacket `4` from the `SEC61A1` cohort and
the second issue points out the usage of a deprecated HPO term in the 6th phenotypic feature of the phenopacket `2` of the `RFXAP` cohort.
At this point, fixing the issues is the responsibility of the curator.
