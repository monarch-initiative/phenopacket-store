import os
import re
import typing
import warnings

import pandas as pd

from collections import defaultdict

from phenopackets.schema.v2.phenopackets_pb2 import Phenopacket
from phenopackets.schema.v2.core.base_pb2 import TimeElement, Age
from phenopackets.schema.v2.core.interpretation_pb2 import Diagnosis
from phenopackets.schema.v2.core.individual_pb2 import Sex, Individual, VitalStatus
from phenopackets.schema.v2.core.meta_data_pb2 import MetaData

from phenopackets.vrsatile.v1.vrsatile_pb2 import VariationDescriptor

from ppktstore.model import PhenopacketStore


iso_duration_pt = re.compile(
    r"^P((?P<years>\d+)Y)?((?P<months>\d+)M)?((?P<days>\d+)D)?(T((?P<hours>\d+)H)?((?P<minutes>\d+)M)?((?P<seconds>\d+)S)?)?$"
)
unit_to_days = {
    "years": 365.25,
    "months": 30,
    "days": 1,
    "hours": 1 / 24,
    "minutes": 1 / (24 * 60),
    "seconds": 1 / (24 * 60 * 60),
}


def summarize_diseases_and_genotype(
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
                    pp_path = os.path.join(cohort.path, pp_info.path)
                    if gene is None:
                        raise ValueError(f"Could not get gene string for {pp_path}")
                    if len(alleles) == 2:
                        allele1, allele2 = alleles
                    elif len(alleles) == 1:
                        allele1, allele2 = alleles[0], ""
                    else:
                        raise ValueError(
                            f"Length of alleles {len(alleles)} was not `1` or `2` for {pp_path}"
                        )

                    data["disease"].append(dx.disease.label)
                    data["disease_id"].append(dx.disease.id)
                    data["patient_id"].append(pp.subject.id)
                    data["gene"].append(gene)
                    data["allele_1"].append(allele1)
                    data["allele_2"].append(allele2)
                    data["PMID"].append(pmid)
                    data["cohort"].append(cohort.name)
                    data["filename"].append(pp_path)

    columns = pd.Index(
        [
            "patient_id",
            "cohort",
            "disease_id",
            "disease",
            "gene",
            "allele_1",
            "allele_2",
            "PMID",
            "filename",
        ]
    )

    return pd.DataFrame(data, columns=columns)


def summarize_genotype_phenotype(
    phenopacket_store: PhenopacketStore,
) -> pd.DataFrame:
    columns = pd.Index(
        [
            "cohort",
            "directory",
            "filename",
            "phenopacket.id",
            "disease",
            "n_hpo",
            "n_var",
            "n_alleles",
            "n_encounters",
        ]
    )
    data = defaultdict(list)
    for cohort in phenopacket_store.cohorts():
        for pp_info in cohort.phenopackets:
            pp = pp_info.phenopacket
            dx_set = set()
            n_var = 0
            n_alleles = 0
            if pp.interpretations is not None:
                for interpretation in pp.interpretations:
                    dx = interpretation.diagnosis
                    disease = dx.disease
                    d_string = f"{disease.label} ({disease.id})"
                    dx_set.add(d_string)
                    for gi in dx.genomic_interpretations:
                        n_var += 1
                        vint = gi.variant_interpretation
                        if vint.variation_descriptor is not None:
                            vdesc = vint.variation_descriptor
                            if vdesc.allelic_state is not None:
                                gtype = vdesc.allelic_state
                                if gtype.label == "heterozygous":  # "GENO:0000135"
                                    n_alleles += 1
                                elif gtype.label == "homozygous":  # "GENO:0000136"
                                    n_alleles += 2
                                elif gtype.label == "hemizygous":  # "GENO:0000134"
                                    n_alleles += 1

            data["cohort"].append(cohort.name)
            data["directory"].append(cohort.path)
            data["phenopacket.id"].append(pp.id)
            data["disease"].append(";".join(dx_set))
            data["n_hpo"].append(len(pp.phenotypic_features))
            data["n_var"].append(n_var)
            data["n_alleles"].append(n_alleles)
            data["n_encounters"].append(_get_encounter_count(pp))
            data["filename"].append(pp_info.path)

    return pd.DataFrame(data=data, columns=columns)


def summarize_cohort_sizes(
    phenopacket_store: PhenopacketStore,
) -> pd.DataFrame:
    # TODO: remove
    warnings.warn("The function will be removed", DeprecationWarning, stacklevel=2)
    rows = defaultdict(list)

    for cohort_info in phenopacket_store.cohorts():
        rows["Cohort"].append(cohort_info.name)
        rows["Directory"].append(cohort_info.path)
        rows["Count"].append(len(cohort_info.phenopackets))

    return pd.DataFrame(rows)


def summarize_individuals(
    store: PhenopacketStore,
) -> pd.DataFrame:
    data = defaultdict(list)
    for cohort_info in store.cohorts():
        for pp_info in cohort_info.phenopackets:
            pp = pp_info.phenopacket
            subject = pp.subject

            data["id"].append(f"{pp.id}-{subject.id}")
            data["sex"].append(Sex.Name(subject.sex))
            n_days = _extract_age(subject)
            data["age_in_days"].append(n_days)
            data["age_in_years"].append(n_days / unit_to_days["years"])

            vs = None
            if subject.HasField("vital_status"):
                vs = VitalStatus.Status.Name(subject.vital_status.status)
            else:
                vs = None
            data["vital_status"].append(vs)

    columns = pd.Index(["id", "sex", "age_in_days", "age_in_years", "vital_status"])
    return pd.DataFrame(data=data, columns=columns)


def _get_encounter_count(
    pp: Phenopacket,
) -> int:
    encounters = set()
    for pf in pp.phenotypic_features:
        if pf.onset.age.iso8601duration is not None:
            encounters.add(pf.onset.age.iso8601duration)
        else:
            encounters.add("n/a")
    return len(encounters)


def _get_pmid(
    meta_data: MetaData,
) -> str:
    if meta_data.external_references:
        return meta_data.external_references[0].id
    else:
        # should never happen
        raise ValueError("Cannot extract PMID")


def _get_gene_and_alleles(
    diagnosis: Diagnosis,
) -> typing.Tuple[typing.Optional[str], typing.Sequence[str]]:
    """
    Extract the gene symbol, failing that the label, for a variant from the Interpretation object.
    Also get the alleles.

    return: a tuple with a gene symbol (or `None` if unfound) and a sequence of HGVS "c" or "g" strings.
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
) -> typing.List[str]:
    alleles = list()
    if variation_descriptor.HasField("structural_type"):
        stype = variation_descriptor.structural_type
        alleles.append(stype.label)
    else:
        raise ValueError(f"Could not find structural_type field")
    return alleles


def _extract_age(
    subject: Individual,
) -> float:
    if subject.HasField("time_at_last_encounter"):
        tale = subject.time_at_last_encounter
        if tale.HasField("age"):
            age = tale.age
            ageperiod = age.iso8601duration
            if ageperiod is not None or ageperiod != "":
                return _parse_to_days(ageperiod)

    return float("nan")


def _parse_to_days(
    age_period: str,
) -> float:
    match = iso_duration_pt.match(age_period)
    if match is None:
        return float("nan")
    else:
        n_days = 0.0

        for unit, multiplier in unit_to_days.items():
            val = match.group(unit)
            if val is not None:
                n_days += float(val) * multiplier

        return n_days
