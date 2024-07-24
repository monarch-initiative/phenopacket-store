import dataclasses
import os
import typing

from google.protobuf.json_format import Parse
from phenopackets import Phenopacket


@dataclasses.dataclass
class PhenopacketInfo:
    """
    Phenopacket plus metadata.
    """
    
    path: str
    """
    Path to the phenopacket source.
    """
    
    phenopacket: Phenopacket
    """
    The phenopacket.
    """


@dataclasses.dataclass
class CohortInfo:
    """
    Cohort of a Phenopacket store.

    Includes cohort-level metadata and a sequence of phenopacket infos for the included phenopackets.
    """

    name: str
    """
    Cohort name, e.g. `FBN1`.
    """

    path: str
    """
    Path where the cohort was ascertained from.
    """

    phenopackets: typing.Collection[PhenopacketInfo]
    """
    The cohort phenopacket infos.
    """

    def __len__(self) -> int:
        return len(self.phenopackets)


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
        cohorts = []
        for cohort_name in os.listdir(nb_dir):
            cohort_dir = os.path.join(nb_dir, cohort_name)
            if os.path.isdir(cohort_dir):
                cohort_path = os.path.join(cohort_dir, pp_dir)
                if os.path.isdir(cohort_path):
                    pp_infos = []
                    for filename in os.listdir(cohort_path):
                        if filename.endswith(".json"):
                            filepath = os.path.join(cohort_path, filename)
                            with open(filepath) as fh:
                                pp = Parse(fh.read(), Phenopacket())
                                pi = PhenopacketInfo(
                                    path=filepath,
                                    phenopacket=pp,
                                )
                                pp_infos.append(pi)

                    cohorts.append(
                        CohortInfo(
                            name=cohort_name,
                            path=cohort_path,
                            phenopackets=tuple(pp_infos),
                        )
                    )

        return PhenopacketStore(
            cohorts=cohorts,
        )

    def __init__(
        self,
        cohorts: typing.Iterable[CohortInfo],
    ):
        self._cohorts = {cohort.name: cohort for cohort in cohorts}

    def cohorts(self) -> typing.Collection[CohortInfo]:
        return self._cohorts.values()

    def cohort_names(self) -> typing.Iterable[str]:
        return self._cohorts.keys()

    def cohort_for_name(
        self,
        name: str,
    ) -> CohortInfo:
        return self._cohorts[name]

    def cohort_count(self) -> int:
        return len(self._cohorts)

    def phenopacket_count(self) -> int:
        return sum(len(cohort) for cohort in self._cohorts.values())
