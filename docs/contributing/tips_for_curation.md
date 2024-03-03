# Tips for accurate curation

This document explains the intended use of the fields of the template and provides guidance on common problems.

### PMID:
Please use the form ``PMID:38143450``. Please remove the space, if any, between the colon and the number.

### Indentifier:

Please use the identifier used in the original publication. If the original publication has a Table, it is usually obvious what identifier to use. In other cases, no explicit identifier is given. Try to extract a short identifier that will be obvious to others who might look at your curation later on. For instance, if the paper is a case report that states this:

!!! example

    Here we present the case of a 28-year-old man with X-linked immunodeficiency with magnesium defect, Epstein–Barr virus (EBV) infection and neoplasia (XMEN) disease.

Then use “28-year-old man” as the identifier (see [PMID:38143450](https://pubmed.ncbi.nlm.nih.gov/38143450/)).

### Disease id and name

Please use the OMIM identifier. This can be taken from the OMIM webpage for the disease. For instance, [OMIM:300853](https://omim.org/entry/300853) shows Phenotype MIM number 300853. Please enter this as ``OMIM:300853``. The ``Phenotype`` (i.e., disease) is shown in the table as ``Immunodeficiency, X-linked, with magnesium defect, Epstein-Barr virus infection and neoplasia``. Please use this label. This will make it much easier for software to correctly identify the disease that is being curated.

### Comment
Sometimes it is hard to curate information and it is a good idea to enter some additional information about the case to help others understand the curation. Please use the ``comment`` field for this. The following box shows an example of the kind of comment that might be useful.

!!! example

    incl Table 1 with many neurological symptoms in these two patients + Table 2 with neurological symptoms in pther XMEN patients

### Transcript

It can be difficult to choose the optimal transcript, and articles about one and the same disease may even use different transcripts. We try to use the transcript that is preferred by ClinVar. See [Varint notation](variant_notation.md) for explanations.

We recommend using [VariantValidator](https://variantvalidator.org/service/validate/) to check the variant identifiers used in original publications.

Note that incorrect variant nomenclature is still common in the literature. For instance, ``c.C414A`` should be ``c.414C>A``.

# HPO Term columns

Please use only HPO terms for these columns. Do not use terms from other ontologies or terminologies such as OMIM, ORPHA, or other sources.


Please use exactly the original HPO term label, e.g., do not use the words they used in the original publication, instead use the label found on the HPO website

For instance, if the original publication states ``recurrent bronchopulmonary infection``, go to the HPO website to determine the corresponding HPO term, which in this case is [Recurrent bronchopulmonary infections](https://hpo.jax.org/app/browse/term/HP:0006538){:target="_blank"}. If ``hypogammaglobulinemia`` is used in the original publication, choose [Decreased circulating antibody level](https://hpo.jax.org/app/browse/term/HP:0004313){:target="_blank"}.

This will make the curation unambiguous and reduce potential errors.

### New terms

The HPO is still incomplete. If you find a phenotypic abnormality in a publication but cannot find a corresponding HPO term, enter the label for
the term in the first row and ``NTR`` (new term request) in the second row. The HPO team will help to decide if there is an existing term for the abnormality or will create a new term. Following this, the Excel file can be updated.

### Scope

The HPO describes phenotypic abnormalities in a clinical context. It does not cover topics such as molecular mechanisms. Terms such as “loss-of function” are not in scope.
