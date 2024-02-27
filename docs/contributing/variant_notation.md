# Variant Notation

We recommend that users choose one transcript for all HGVS variant descriptions in a project. In general, the most clinicallz relevant transcript should be chosen.


### Choosing the reference transcript for a project

An easy way to identify the optimal transcript is to search with the gene symbol in [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/){:target="_blank"}. For instance, searching on [FBN2](https://www.ncbi.nlm.nih.gov/clinvar/?term=FBN2%5Bgene%5D&redir=gene){:target="_blank"} reveals a page with variants such as this: **NM_001999.4(FBN2):c.8729A>G (p.Gln2910Arg)** (Note that you may need to skip over more complex structural variants that include the FBN2 and other genes to get to this entry). The transcript **NM_001999.4** is the one to use.

In general, we recommend using the MANE Select (or if available MANE Select Clinical).
This can be found using the [Ensembl](https://www.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g=ENSG00000138829;r=5:128257909-128659185) website for the gene in quenstion (here we see that the MANE Select transcript for FBN2 is ENST00000262464.9, which is equivalent to NM_001999.4). MANE refers to [MANE (Matched Annotation from NCBI and EBI)](https://www.ncbi.nlm.nih.gov/refseq/MANE/){:target="_blank"}

Rarely, one transcript alone is not enough to report all clinically relevant variation. We reocmmend consulting the MANE Plus Clinical set, which includes additional transcripts for genes where MANE Select alone is not sufficient to report all "Pathogenic (P)" or "Likely Pathogenic (LP)" clinical variants available in public resources.

### Checking and converting variants

Older literature often uses out-of-date HGVS notation and may use transcripts other than MANE select or the transcript used in ClinVar.


For example, [Abbas MM, et al. 2016](https://pubmed.ncbi.nlm.nih.gov/30713959/){:target="_blank"} describe a "A missense mutation c.T2525C:p.L842P in ATP13A2 (Ensemble transcript ID ENST00000341676)". There are two difficulties here. Firstly, the notation "cT2525C" is not correct [HGVS Nomenclature](https://hgvs-nomenclature.org/stable/){:target="_blank"} and should be "c.2525T>C". Secondly, the transcript used is not the desired one. By consulting the Ensembl webpage, we determined that ENST00000341676 is equivalent to NM_001141974.2.

There are various ways to check and convert notation.

- [Mutalyzer](https://mutalyzer.nl/){:target="_blank"}: Has tools to check notation and also to convert between transcript references
- [VariantValidator](https://variantvalidator.org/){:target="_blank"}: Has tools to check HGVS nomenclature and to compare differnet transcript references.

In this case, using VariantValidator, we determined that the correct notation is **NM_022089.4:c.2657T>C**. This can be difficult and please reach out to us in case of questions.




We can additionally check the transcript by going to the [VariantValidator](https://variantvalidator.org/){:target="_blank"} website and testing the HGVS nucleotide variant (i.e., NM_001999.4(FBN2):c.8729A>G) using the  **Validator** tool (paste the variant in the *Variant Description:* window). If we paste the resulting VCF-like notation GRCh38:5:128259465:T:C