# Phenopacket Store


This repository contains a collection of Jupyter notebooks that generate
[GA4GH phenopackets](https://pubmed.ncbi.nlm.nih.gov/35705716){:target="_blank"}.
for analysis projects. 
The phenopackets represent case reports about individuals with Mendelian diseases.

A publication describing the case report curation methodology
as well as the best practices for future curation is available
at [Danis *et al.*, HGG Advances 2025](https://www.cell.com/hgg-advances/fulltext/S2666-2477(24)00111-8)

The notebooks are contained in the 
[notebooks](https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks){:target="_blank"} 
folder organized according to an affected gene.


## Summary statistics

See [Collections](collections.md) for a short documentation page for each case report collection included in this repository.
The summary statistics for the entire phenopacket store as well as with Q/C checks can be seen in 
[PhenopacketStoreStats](https://github.com/monarch-initiative/phenopacket-store/tree/main/PhenopacketStoreStats.ipynb){:target="_blank"} 
notebook.

## Availability

All case report collections are periodically released in a ZIP archive,
which is available for download from the [Releases](https://github.com/monarch-initiative/phenopacket-store/releases){:target="_blank"} section.

### Versioned release

A specific Phenopacket store version can also be accessed programmatically. Just replace the `VERSION` placeholder 
with a release tag from the [Releases](https://github.com/monarch-initiative/phenopacket-store/releases) section:

```
https://github.com/monarch-initiative/phenopacket-store/releases/download/VERSION/all_phenopackets.zip
```

For instance:
```
https://github.com/monarch-initiative/phenopacket-store/releases/download/0.1.16/all_phenopackets.zip
```
for the `0.1.16` version.

### Latest release

The *latest* release is also available for download programmatically:

**ZIP**

Download the latest ZIP archive with `wget`:
```shell
wget https://github.com/monarch-initiative/phenopacket-store/releases/latest/download/all_phenopackets.zip
```

or with `curl`:
```shell
curl -Lo all_phenopackets.zip https://github.com/monarch-initiative/phenopacket-store/releases/latest/download/all_phenopackets.zip
```


## Citing Phenopacket Store

If you use Phenopacket Store in a scientific publication, we would appreciate citations to the following paper:

[A corpus of GA4GH phenopackets: Case-level phenotyping for genomic diagnostics and discovery](https://www.cell.com/hgg-advances/fulltext/S2666-2477(24)00111-8), Danis et al., Human Genetics and Genomics Advances, Volume 6, Issue 1, 100371


## Feedback

The best place to leave feedback, ask questions, and report bugs is the GitHub [Issue Tracker](https://github.com/monarch-initiative/phenopacket-store/issues){:target="_blank"}.
