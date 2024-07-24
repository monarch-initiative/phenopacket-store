import os
import typing

from google.protobuf.json_format import Parse
from phenopackets import Phenopacket


class PhenopacketStore:

    @staticmethod
    def from_notebook_dir(
        nb_dir: str,
        pp_dir: str = "phenopackets",
    ):
        """
        Create `PhenopacketStore` from Phenopacket store notebook dir `nb_dir`.

        We expect the `nb_dir` to include a folder per cohort,
        and the phenopackets should be stored in `nb_dir` sub-folder (``nb_dir=phenopackets`` by default).
        """
        cohorts = {}
        for cohort_name in os.listdir(nb_dir):
            cohort_dir = os.path.join(nb_dir, cohort_name)
            if os.path.isdir(cohort_dir):
                fpath_pp_dir = os.path.join(cohort_dir, pp_dir)
                if os.path.isdir(fpath_pp_dir):
                    cohort = []
                    for subpath in os.listdir(fpath_pp_dir):
                        if subpath.endswith(".json"):
                            fpath_pp = os.path.join(fpath_pp_dir, subpath)
                            with open(fpath_pp) as fh:
                                pp = Parse(fh.read(), Phenopacket())
                                cohort.append(pp)
                    
                    cohorts[cohort_name] = cohort

        return PhenopacketStore(
            cohorts=cohorts,
        )

    def __init__(
        self,
        cohorts: typing.Mapping[str, typing.Iterable[Phenopacket]],
    ):
        self._cohorts = {}
        for name, phenopackets in cohorts.items():
            self._cohorts[name] = tuple(phenopackets)

    def cohort_names(self) -> typing.Collection[str]:
        return self._cohorts.keys()

    def cohort_for_name(
        self,
        name: str,
    ) -> typing.Sequence[Phenopacket]:
        return self._cohorts[name]

    def cohort_count(self) -> int:
        return len(self.cohort_names())
    
    def phenopacket_count(self) -> int:
        pp_count = 0
        for cohort in self._cohorts.values():
            pp_count += len(cohort)
        return pp_count
