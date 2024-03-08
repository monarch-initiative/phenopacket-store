# Excel Template

We have designed a format for Excel templates that can be used to quickly and efficiently generate collections of Phenopackets. This is currently the prefered way for clinicians and translational researchers to contribute to this project. The [pyphetools](https://github.com/monarch-initiative/pyphetools){:target="_blank"}  library provides other means for bioinformaticians (please ask us).

The template can be downloaded [here](../_static/template.xlsx){:target="_blank"}.

# A format for cohort descriptions in excel

The schema of the template consists in two rows that specify the nature of the data. There is a fixed set of columns that capture basic demographic data together with the disease, the source publication, and the variants. The second half of the template should be used to record information about
HPO terms curated from the publications.

## Fixed columns
The first (leftmost) 11 or 12 columns specify basic demographic data together with the disease, the source publication, and the variants.
The first two rows are used to specify the datatypes and should not be changed. The following tables show the first two rows together with
one example row with data extracted from a publication (We show two tables for better legibility)


|  PMID	| title	| individual_id	| Comment | disease_id	 | disease_label|
|:------|:------|:--------------|:--------|:-------------|:-------------|
| str	| str	| str       	| optional|  str         | 	        str |
| PMID:33087723| 	Early-onset autoimmunity associated with SOCS1 haploinsufficiency| 	A1|	|	OMIM:603597|	Autoinflammatory syndrome, familial, with or without immunodeficiency|


1. **PMID** (str, i.e., string): The PubMed identifier of the publication being curated.
2. **title** (str): The title of the publication being curated.
3. **individual_id** (str): The identifier of the individual being described in the original publication. This field is required. Please add ‘individual’ if the original article does not provide an identifier (if needed, individual 1, individual 2,...).
4. **comment** (str): This field is provided to record additional information that will not be used for creating phenopackets but may be helpful for future reference. It can be left empty.
5. **disease_id** (str). The disease identifer (e.g., ``OMIM:154700`` or  ``MONDO:0007947``).
6. **disease_label** (str). The name of the disease (e.g. ``Marfan syndrome``).




|  transcript| 	allele_1| allele_2 | variant.comment| 	age_of_onset| age_at_last_encounter |sex	  | HPO	|
|:-----------|:---------|:---------|:---------------|:--------------|:----------------------|:--------|:----|
|  str       |      str | str      |optional        |  	age      	| age                   | M:F:O:U | na	|
| NM_003745.2|c.368C>G  |	    na |p.P123R         |Infantile onset|    	P21Y	        | F       | na  |

7. **transcript** (str): The identifier of the transcript. NCBI RefSeq or ENSEMBL identifiers are preferred.
8. **allele_1** (str): A string representing the first pathogenic allele (variant) according to [HGVS](https://hgvs-nomenclature.org/stable/background/simple/) nomenclature.
9. **allele_2** (str): This field should not be used for monoallelic diseases (e.g. autosomal dominant, XLR). The column can eigther be omitted or can be filled with "na" to denote "not applicable". It the column is present and is left empty, this will be flagged as an error. For biallelic diseases (autosomal recessive), specific the second allele (which will be the same as the first for homozygous genotypes).
10. **variant.comment** (str): This field is provided to record additional information that will not be used for creating phenopackets but may be helpful for future reference.
11. **age_of_onset**: The age of onset of disease, recorded using [iso8601 convention](https://en.wikipedia.org/wiki/ISO_8601#Durations) or an HPO [Onset](https://hpo.jax.org/app/browse/term/HP:0003674){:target="_blank"} term.
12. **sex** (M:F:U:O): one of M (male), female (F), other(O), or unknown (U)
13. **HPO** (na): This acts as a separator column to denote that all folowing columns specify HPO annotations (See below). Add the string na to each cell in this column.

### HPO Term Columns
All of the following columns denote HPO terms. The first row has the HPO term label. Be sure to use the same label as is shown on the HPO
webpage and do not chance the capitalization. The second row has the corresponding HPO id. The following table shows several examples, whereby
the individual_id column from above is shown for ease of exposition.




|individual_id |  Hepatitis  | 	Pancreatitis| 	Lymphadenopathy| 	Splenomegaly   |
|:-------------|:------------|:-------------|:-----------------|:------------------|
|              | HP:0012115  |HP:0001733    |  HP:0002716      |   HP:0001744      |
| A            | observed    | excluded     |                  | P4Y2M             |
| B            |P3Y          |    na        | observed         | excluded          |

Each table cell can contain either
1. observed: The phenotypic abnormality denoted by the HPO term was present
2. excluded: The phenotypic abnormality denoted by the HPO term was investigated and ruled out.
3. An [iso8601](https://en.wikipedia.org/wiki/ISO_8601#Durations) string denoting the age of onset.
4. na or empty (blank): Information not available or phenotypic feature not measured.

In this example, individual A was observed to have hepatitis (but age of onset is unknown or not available), pancreatitis was ruled out, no information is available about lymphadenopathy, and splenomegaly was first observed at age 4 years and 2 months.

Individual B was found to have hepatitis first observed at age 3 years, no information was available about pancreatitis, lymphadenopathy was observed (but age of onset is unknown or not available), and splenomegaly  was ruled out.











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