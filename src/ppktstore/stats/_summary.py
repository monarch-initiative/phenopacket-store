import typing

import pandas as pd

from collections import defaultdict

from phenopackets.schema.v2.core.meta_data_pb2 import MetaData
from phenopackets.schema.v2.core.interpretation_pb2 import Diagnosis

from phenopackets.vrsatile.v1.vrsatile_pb2 import VariationDescriptor

from ppktstore.model import PhenopacketStore


def create_summary_df(
    phenopacket_store: PhenopacketStore,
) -> pd.DataFrame:
    """
    Create a summary table for all phenopackets of the store
    """
    data = defaultdict(list)
    for cohort in phenopacket_store.cohorts():
        for pp_info in cohort.phenopackets:
            pp = pp_info.phenopacket
            for interpretation in pp.interpretations:
                if interpretation.diagnosis:
                    dx = interpretation.diagnosis
                    pmid = _get_pmid(meta_data=pp.meta_data)
                    gene, alleles = _get_gene_and_alleles(diagnosis=dx)
                    if gene is None:
                        raise ValueError(
                            f"Could not get gene string for {pp_info.path}"
                        )
                    if len(alleles) == 2:
                        allele1, allele2 = alleles
                    elif len(alleles) == 1:
                        allele1, allele2 = alleles[0], ""
                    else:
                        raise ValueError(
                            f"Length of alleles {len(alleles)} was not `1` or `2` for {pp_info.path}"
                        )

                    data["disease"].append(dx.disease.label)
                    data["disease_id"].append(dx.disease.id)
                    data["patient_id"].append(pp.subject.id)
                    data["gene"].append(gene)
                    data["allele_1"].append(allele1)
                    data["allele_2"].append(allele2)
                    data["PMID"].append(pmid)
                    data["cohort"].append(cohort.name)
                    data["filename"].append(pp_info.path)

    return pd.DataFrame(data)


def _get_pmid(
    meta_data: MetaData,
) -> str:
    if meta_data.external_references:
        return meta_data.external_references[0].id
    else:
        # should never happen
        raise ValueError("Cannot extract PMID")


def _get_gene_and_alleles(diagnosis: Diagnosis) -> typing.Tuple[str, typing.List[str]]:
    """
    Extract the gene symbol, failing that the label, for a variant from the Interpretation object.
    Also get the alleles.
    """
    gene = None
    alleles = []
    for genomic_interpretation in diagnosis.genomic_interpretations:
        if genomic_interpretation.variant_interpretation:
            if genomic_interpretation.variant_interpretation.variation_descriptor:
                var_desc = (
                    genomic_interpretation.variant_interpretation.variation_descriptor
                )
                gene = _get_gene_symbol(variant_descriptor=var_desc)
                if var_desc.expressions:
                    hgvsC = ""
                    hgvsG = ""
                    for expr in var_desc.expressions:
                        if expr.syntax == "hgvs.c":
                            hgvsC = expr.value
                        if expr.syntax == "hgvs.g":
                            hgvsG = expr.value
                    if hgvsC:
                        alleles.append(hgvsC)
                    elif hgvsG:
                        alleles.append(hgvsG)
                # get structural variant, if needed
                if len(alleles) == 0:
                    alleles = _get_structural_var(var_desc)
                # get genotype
                genotype = var_desc.allelic_state
                if genotype.label == "homozygous" and len(alleles) > 0:
                    alleles.append(alleles[0])
    return gene, alleles


def _get_gene_symbol(
    variant_descriptor: VariationDescriptor,
) -> str:
    gene = None
    if variant_descriptor.HasField("gene_context"):
        gene = variant_descriptor.gene_context.symbol
    if gene is None:
        gene = variant_descriptor.label
    return gene


def _get_structural_var(
    variation_descriptor: VariationDescriptor,
) -> typing.Sequence[str]:
    alleles = list()
    if variation_descriptor.HasField("structural_type"):
        stype = variation_descriptor.structural_type
        alleles.append(stype.label)
    else:
        raise ValueError(f"Could not find structural_type field")
    return alleles
