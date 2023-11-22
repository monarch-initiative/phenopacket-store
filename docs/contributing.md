# Contributing

Contributions to phenopacket-store are welcome. The scope of phenopacket-store comprises cohorts of indiduals with rare disease with deep phenotype as well as genotypic data.

There are many ways of contributing. Almost all of the notebooks in this repository were created using the [pyphetools](https://monarch-initiative.github.io/pyphetools/) library, and users can learn how to use it by studying the notebooks listed on the [collections](collections.md) page. Alternatively, we welcome contributions made using templated Excel files as described below.

# A format for cohort descriptions in excel

The file should contain at least the following information; see explanations below.




|row_type| id | age | sex | allele |  Tall stature | Abnormal sternum morphology | Potassium |
|:---- |:----|:----|:----|:-----|:---------|:----|:------------- |
| header1 | str | ISO8601 | str | NM_000138.5 | simple  | option| threshold |
| header2 |  |  |  |  | HP:0000098 |  HP:0000767; HP:0000768| 3.5-5.2 mEq/L: High->Hyperkalemia{HP:0002153); Low->Hypokalemia(HP:0002900) |
| individual| patient A | P6Y | male | c.8326C>T | + | Pectus carinatum | n/a |
| individual| patient B | P9Y | female | c.7988G>C | - | Pectus excavatum | 5.8 |



## row_type
Each row must begin with one of the words "header1", "header2" or "individual". There should be one row for each individual in the cohort.

## id
This is an cohort-specific identifier that **must** be anonymized.

## age
This is the age of the individual at the time of the medical encounter at which the phenotypic features were recorded. The format of the column is recorded in the header1 line. Valid options are *ISO8601* for strings such as "P4Y" (four years of age) and "P71Y6M2D" for 71 years, 6 months, and 2 days; *Years* for 5 (5 years of age) or 7.5 (7 years and 6 months).

## sex
Use male, female, other, or unknown.

# HPO columns
The remaining columns contain information about HPO terms observed in the individuals. There are three types of column.

# Simple.
The top row contains the label of the term. The header1 row contains the word "simple". The header2 row contains the HPO id; in the example table, we see [Tall stature; HP:0000098](https://hpo.jax.org/app/browse/term/HP:0000098). If the feature is observed in an indivual, use "+"; if the feature was explicitly excluded, use "-". If the feature was not measured or no information is available, use "n/a".

# Option
This type of column is used for sets of related terms. The top row contains the label of the HPO superclass (herere [Abnormal sternum morphology HP:0000766](https://hpo.jax.org/app/browse/term/HP:0000766)). The header1 row contains the word "option". The header2 row contains the HPO ids of the terms that can be recorded in the column. In this example, it is the terms [Pectus carinatum; HP:0000768](https://hpo.jax.org/app/browse/term/HP:0000768) and
[Pectus excavatum HP:0000767](https://hpo.jax.org/app/browse/term/HP:0000767). In the individual rows, the corresponding label of the HPO term is written. Any number of terms can be put into one column in this way.

# Threshold
This type of column is used for numerical data with a normal range. Indicate the normal range and the HPO terms that are used for low or high values as shown.

# Text mining
This type of column is not preferred but if necessary can be used. An example is not shown here, but but "text mining" in the header1 row and nothing in the header2 row. We will use text mining to attempt to extract HPO terms from the texts in the column.
