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

We provide special support for Python with [Phenopacket Store Toolkit](https://github.com/monarch-initiative/phenopacket-store-toolkit)
to simplify using the Phenopacket Store data in the downstream applications.

The toolkit is available for installation from PyPi:

```shell
python3 -m pip install phenopacket-store-toolkit
```

The toolkit makes loading phenopackets super easy.
First, we create Phenopacket Store registry, an object for managing local data files
of Phenopacket Store releases:

```python
from ppktstore.registry import configure_phenopacket_registry
registry = configure_phenopacket_registry()
```

By default, the `registry` keeps the files in data directory at `$HOME/.phenopacket-store` (or similar on Windows), but this can be configured if desired.

Then, we can use `registry` to load phenopackets of a cohort, e.g. *SUOX* of release `0.1.18`:

```python
with registry.open_phenopacket_store(release="0.1.18") as ps:
  phenopackets = list(ps.iter_cohort_phenopackets("SUOX"))
assert len(phenopackets) == 35
```

The registry peeks into the data directory to check if the `0.1.18` release ZIP file has already been downloaded.
If absent, the registry will download the ZIP file from Github. Then, we open Phenopacket Store as `ps` and we load 35 phenopackets of *SUOX* cohort.


## Contributing

The cohorts were curated from data medical publications, mainly by parsing the tables or supplemental tables. 
The curation was done in Jupyter notebooks using [pyphetools](https://pypi.org/project/pyphetools/) library. 
Pull requests with additional notebooks in the same style are welcome.
