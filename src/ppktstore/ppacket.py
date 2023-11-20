from google.protobuf.json_format import Parse
from phenopackets import Phenopacket


class PPacket:

    def __init__(self, fname:str) -> None:
        self._fname = fname

        with open(fname) as f:
            ppack = Parse(f.read(), Phenopacket())

        self._id = ppack.id
        self._n_hpo = len(ppack.phenotypic_features)
        n_var = 0
        n_alleles = 0
        dx_set = set()
        if ppack.interpretations is None:
            n_dx = 0
        else:
            for interpretation in ppack.interpretations:
                if interpretation.diagnosis is not None:
                    dx = interpretation.diagnosis
                    disease = dx.disease
                    d_string = f"{disease.label} ({disease.id})"
                    dx_set.add(d_string)
                    for genomic_interpretation in dx.genomic_interpretations:
                        n_var += 1
                        vint = genomic_interpretation.variant_interpretation
                        if vint.variation_descriptor is not None:
                            vdesc =   vint.variation_descriptor
                            if vdesc.allelic_state is not None:
                                gtype = vdesc.allelic_state
                                if gtype.label == "heterozygous": # "GENO:0000135"
                                    n_alleles += 1
                                elif gtype.label == "homozygous": # "GENO:0000136"
                                    n_alleles += 2
                                elif gtype.label == "hemizygous": # "GENO:0000134"
                                    n_alleles += 1
            n_dx = len(dx_set)
        self._n_var = n_var
        self._n_alleles = n_alleles
        self._n_dx = n_dx
        self._disease = ";".join(dx_set)

    def get_dict(self):
        d = {
            "phenopacket.id": self._id,
            "disease": self._disease,
            "n_hpo": self._n_hpo,
            "n_var": self._n_var,
            "n_alleles": self._n_alleles,
            "filename": self._fname
        }
        return d
