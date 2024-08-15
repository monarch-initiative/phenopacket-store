# phenopacket store

[![DOI](https://zenodo.org/badge/580002593.svg)](https://zenodo.org/doi/10.5281/zenodo.13168726)


This repository offers cohorts of [GA4GH Phenopackets](https://phenopacket-schema.readthedocs.io/en/latest/) that
represent individuals with Mendelian diseases.

Please see the [online documentation](https://monarch-initiative.github.io/phenopacket-store) for information about available cohorts.

## Availability

Phenopacket store releases are available for download from the 
[Releases](https://github.com/monarch-initiative/phenopacket-store/releases) section.

The *latest* release ZIP archive is available for download from a stable URL:

**ZIP**
```
https://github.com/monarch-initiative/phenopacket-store/releases/latest/download/all_phenopackets.zip
```

## Python support

We provide special support for Python in terms of `ppktstore` library to simplify using Phenopacket Store data 
in phenopacket-driven applications.

The `ppktstore` library is available to install from PyPi:

```shell
python3 -m pip install ppktstore
```

After installation, the library can be used to quickly load phenopackets.
First, we create Phenopacket Store registry, an object for managing local data files
of Phenopacket Store releases:

>>> from ppktstore.registry import configure_phenopacket_registry
>>> registry = configure_phenopacket_registry()

We can use `registry` to load phenopackets of a cohort, e.g. *SUOX* of release `0.1.18`:

>>> with registry.open_phenopacket_store(release="0.1.18") as ps:
...   phenopackets = list(ps.iter_cohort_phenopackets("SUOX"))
>>> len(phenopackets)
35

The registry peeks into the local data folder to check the existence of the ZIP file for release `0.1.18`.
If the file is missing, the registry will download the file from Github. Then, Phenopacket Store `ps` is opened 
and handed over as a context manager. The context manager ensures a proper closing of the ZIP file.
Last, we load 35 *SUOX* phenopackets.


## Contributing

The cohorts were curated from data medical publications, mainly by parsing the tables or supplemental tables. 
The curation was done in Jupyter notebooks using [pyphetools](https://pypi.org/project/pyphetools/) library. 
Pull requests with additional notebooks in the same style are welcome.
