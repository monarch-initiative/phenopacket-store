import dataclasses
import os
import pathlib
import typing
import zipfile

from collections import defaultdict

from google.protobuf.json_format import Parse
from phenopackets import Phenopacket


@dataclasses.dataclass
class PhenopacketInfo:
    """
    Phenopacket plus metadata.
    """
    
    path: str
    """
    Path of the phenopacket source relative from the enclosing cohort.
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
    Path of the cohort relative from the enclosing source.
    """

    phenopackets: typing.Collection[PhenopacketInfo]
    """
    The cohort phenopacket infos.
    """

    def __len__(self) -> int:
        return len(self.phenopackets)


class PhenopacketStore:

    @staticmethod
    def from_release_zip(
        zip_path: str,
    ):
        """
        Read `PhenopacketStore` from a release ZIP archive.
         
        The archive structure must match the structure of the ZIP archives 
        created by :class:`ppktstore.archive.PhenopacketStoreArchiver`.
        Only JSON file format is supported at the moment.

        :param zip_path: path to the ZIP release archive.
        :returns: :class:`PhenopacketStore` with data read from the archive.
        """
        if not os.path.isfile(zip_path):
            raise ValueError(f'File does not exist {zip_path}')
        if not zipfile.is_zipfile(zip_path):
            raise ValueError(f'Does not seem to be a ZIP file: {zip_path}')
        
        cohorts = []
        with zipfile.ZipFile(zip_path, mode='r') as zf:           
            root_path = zipfile.Path(zf)

            # Prepare paths to cohort folders 
            # and collate paths to cohort phenopackets.
            cohort2path = {}
            cohort2pp_paths = defaultdict(list)
            for entry in zf.infolist():
                entry_path = zipfile.Path(zf, at=entry.filename)
                if entry_path.is_dir():
                    if entry_path.parent == root_path:
                        name = entry_path.name
                    else:
                        cohort_name = entry_path.name
                        cohort2path[cohort_name] = entry_path
                elif entry_path.is_file() and entry_path.suffix == '.json':
                    # This SHOULD be a phenopacket!
                    cohort = entry_path.parent.name  # type: ignore
                    cohort2pp_paths[cohort].append(entry_path)
                    
            for cohort, cohort_path in cohort2path.items():
                if cohort in cohort2pp_paths:
                    rel_cohort_path = zipfile.Path(zf, at=cohort_path.relative_to(root_path))
                    pp_infos = []
                    for pp_path in cohort2pp_paths[cohort]:
                        path = pp_path.relative_to(rel_cohort_path)
                        pp = Parse(pp_path.read_text(), Phenopacket())
                        pi = PhenopacketInfo(
                            path=str(path),
                            phenopacket=pp,
                        )
                        pp_infos.append(pi)
                    
                    ci = CohortInfo(
                        name=cohort,
                        path=str(rel_cohort_path),
                        phenopackets=tuple(pp_infos),
                    )
                    cohorts.append(ci)

        root_path = pathlib.Path(str(root_path))

        return PhenopacketStore(
            name=name,
            path=root_path,
            cohorts=cohorts,
        )

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
        nb_path = pathlib.Path(nb_dir)
        for cohort_name in os.listdir(nb_path):
            cohort_dir = nb_path.joinpath(cohort_name)
            if cohort_dir.is_dir():
                cohort_path = cohort_dir.joinpath(pp_dir)
                if cohort_path.is_dir():
                    pp_infos = []
                    rel_cohort_path = cohort_path.relative_to(nb_path)
                    for filename in os.listdir(cohort_path):
                        if filename.endswith(".json"):
                            filepath = cohort_path.joinpath(filename)
                            pp = Parse(filepath.read_text(), Phenopacket())
                            pi = PhenopacketInfo(
                                path=filename,
                                phenopacket=pp,
                            )
                            pp_infos.append(pi)

                    cohorts.append(
                        CohortInfo(
                            name=cohort_name,
                            path=str(rel_cohort_path),
                            phenopackets=tuple(pp_infos),
                        )
                    )

        return PhenopacketStore(
            name=nb_path.name,
            path=nb_path,
            cohorts=cohorts,
        )

    def __init__(
        self,
        name: str,
        path: pathlib.Path,
        cohorts: typing.Iterable[CohortInfo],
    ):
        self._name = name
        self._path = path
        self._cohorts = {cohort.name: cohort for cohort in cohorts}

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def path(self) -> pathlib.Path:
        return self._path

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
