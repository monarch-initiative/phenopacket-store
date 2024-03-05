# Python (Jupyter) notebook for the Excel template

The following sections explain how to use Python code to create phenopackets from data stored using the [Excel template](excel.md).


## Preparing the notebook.

We first import the necessary libraries. Note that for conciseness, we import all classes from the pyphetools modules below. It is often better
to import only the specifically needed classes.

```python
import pandas as pd
from IPython.display import display, HTML
pd.set_option('display.max_colwidth', None) # show entire column contents, important!
from collections import defaultdict
from pyphetools.creation import *
from pyphetools.visualization import *
from pyphetools.validation import *
import pyphetools
print(f"Using pyphetools version {pyphetools.__version__}")
```

Load the [Human Phenotype Ontology (HPO)](https://hpo.jax.org/app/) (`v2024-01-16` in this example). 
Note that here we show code that downloads the HPO file from a remote URL. 
However, path to a local `hp.json` file will work too, while saving the remote bandwidth. 

Last, update the ORCID identifier to your own [ORCID](https://orcid.org/){:target="_blank"}  id.

```python
hpo_version = '2024-01-16'
hpo_url = f'https://github.com/obophenotype/human-phenotype-ontology/releases/download/v{hpo_version}/hp.json'
parser = HpoParser(hpo_json_file=hpo_url)
hpo_cr = parser.get_hpo_concept_recognizer()
hpo_ontology = parser.get_ontology()
created_by="ORCID:0000-0002-0736-9199"
print(f"HPO version {parser.get_version()}")
```

import the template file and show the contents (Adjust the head command to show as many lines as needed to check the data).

```
df = pd.read_excel("input/ATP13A2_Kufor_Rakeb_individuals.xlsx")
df.head(2)
```
Create the encoder.

```
encoder = CaseTemplateEncoder(df=df, hpo_cr=hpo_cr, created_by=created_by)
individuals = encoder.get_individuals()
```
Create the VariantManager object. Supply it with the corresponding gene symbol and transcript. If the disease being curated displays monoallelic variants (e.g., autosomal dominant), omit the  ``allele_2_column_name`` argument.


```python
vmanager = VariantManager(df=df,
                          individual_column_name="individual_id",
                          gene_symbol="ATP13A2",
                          transcript="NM_022089.4",
                          allele_1_column_name="allele_1",
                          allele_2_column_name="allele_2")
```

Check results of variant encoding.
```python
vmanager.to_summary()
```
This will show (correctly) mapped as well as unmapped variants. If an HGVS variant is unmapped, it will need to be corrected. See  [variant notation](variant_notation.md) for suggestions. If the variants are chromosomal, there are special functions that are used. See the corresponding [pyphetools](https://monarch-initiative.github.io/pyphetools/){:target="_blank"} documentation.


Add the variants to the individual objects.

```python
vmanager.add_variants_to_individuals(individuals)
```

Perform quality control. The QC will show errors that need to be corrected as well as warnings that are for information only.

```python
cvalidator = CohortValidator(cohort=individuals, ontology=hpo_ontology, min_hpo=1,
                                allelic_requirement=AllelicRequirement.BI_ALLELIC)
qc = QcVisualizer(cohort_validator=cvalidator)
display(HTML(qc.to_summary_html()))
```

Display summary of phenopackets
```python
individuals = cvalidator.get_error_free_individual_list()
table = IndividualTable(individuals)
display(HTML(table.to_html()))
```
Output the phenopackets to file.
```python
encoder.output_individuals_as_phenopackets(individual_list=individuals)
```

See the [pyphetools documentation](https://monarch-initiative.github.io/pyphetools/developers/hpoa_editing/){:target="_blank"} for information about exporting HPOA files from collections of phenoapckets.