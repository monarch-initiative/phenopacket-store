import phenopackets as php
from google.protobuf.json_format import MessageToJson
from collections import defaultdict


from pyphetools.creation import *



parser = HpoParser()
hpo_cr = parser.get_hpo_concept_recognizer()
hpo_version = parser.get_version()
metadata = MetaData(created_by="ORCID:0000-0002-0736-9199")
metadata.default_versions_with_hpo(version=hpo_version)


# With respect to transcript NM_002834.5 of PTPN11
ptpn11_variants = {
    "family A": "c.409_413del",
    "family B":"c.458_463delinsAAGAACACAGGGGAGAGCA",
    "family C": "c.353_354del",
    "family I": "c.295A>T",
    "family D":"c.1315del",
    "family E": "c.1516C>T",
    "family F": "c.643-2A>C",
    "family G": "c.1093-1G>T",
    "family H": "c.680_683del",
    "family O": "c.1225-1G>A"
}

disease_id = 'OMIM:156250'
disease_label = 'Metachondromatosis'

genome = 'hg38'
default_genotype = 'heterozygous'
transcript='NM_002834.5'
varValidator = VariantValidator(genome_build=genome, transcript=transcript)


pmid = "PMID:21533187"
for pat_id, variant in ptpn11_variants.items():
    print(f"Creating phenopacket for {pat_id} and variant {variant}")
    encoder = CaseEncoder(concept_recognizer=hpo_cr, pmid=pmid)
    hpo_term = "Multiple exostoses" # HP:0002762
    encoder.add_term(label=hpo_term)
    var = varValidator.encode_hgvs(hgvs=variant)
    ppacket = encoder.get_phenopacket(individual_id=pat_id, disease_id=disease_id, 
                                  disease_label=disease_label, variants=var, metadata=metadata.to_ga4gh())
    json_string = MessageToJson(ppacket)
    print(json_string)
    encoder.output_phenopacket(outdir=".", phenopacket=ppacket)



