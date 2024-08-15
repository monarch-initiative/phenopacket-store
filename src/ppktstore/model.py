import abc
import dataclasses
import os
import pathlib
import typing
import zipfile

from collections import defaultdict

from google.protobuf.json_format import Parse
from phenopackets.schema.v2.phenopackets_pb2 import Phenopacket


class PhenopacketInfo(metaclass=abc.ABCMeta):
    """
    Phenopacket plus metadata.
    """

    @property
    @abc.abstractmethod
    def path(self) -> str:
        """
        Path of the phenopacket source relative from the enclosing cohort.
        """

    @property
    @abc.abstractmethod
    def phenopacket(self) -> Phenopacket:
        """
        The phenopacket.
        """
        pass


class EagerPhenopacketInfo(PhenopacketInfo):
    """
    Phenopacket info with eagerly loaded phenopacket.
    """

    @staticmethod
    def from_path(path: str, pp_path: pathlib.Path):
        pp = Parse(pp_path.read_text(), Phenopacket())
        return EagerPhenopacketInfo(path, pp)

    def __init__(
        self,
        path: str,
        phenopacket: Phenopacket,
    ):
        self._path = path
        self._phenopacket = phenopacket

    @property
    def path(self) -> str:
        return self._path

    @property
    def phenopacket(self) -> Phenopacket:
        return self._phenopacket

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, EagerPhenopacketInfo)
            and self._path == value._path
            and self._phenopacket == value._phenopacket
        )

    def __hash__(self) -> int:
        return hash((self._path, self._phenopacket))

    def __str__(self) -> str:
        return f"EagerPhenopacketInfo(path={self._path})"

    def __repr__(self) -> str:
        return str(self)


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

    def iter_phenopackets(self) -> typing.Iterator[Phenopacket]:
        """
        Get an iterator with all phenopackets of the cohort.
        """
        return map(lambda pi: pi.phenopacket, self.phenopackets)

    def __len__(self) -> int:
        return len(self.phenopackets)


class PhenopacketStore(metaclass=abc.ABCMeta):

    @staticmethod
    def from_release_zip(
        zip_file: zipfile.ZipFile,
        strategy: typing.Literal["eager", "lazy"] = "eager",
    ):
        """
        Read `PhenopacketStore` from a release ZIP archive.

        The archive structure must match the structure of the ZIP archives
        created by :class:`ppktstore.archive.PhenopacketStoreArchiver`.
        Only JSON phenopacket format is supported at the moment.

        The phenopackets can be loaded eagerly or in a lazy fashion.
        The `'eager'` strategy will load all phenopackets during the load
        at the expense of the loading time and higher RAM usage.
        The `'lazy'` strategy only scans the ZIP for phenopackets
        and the phenopacket parsing is done on demand, only when accessing
        the :attr:`PhenopacketInfo.phenopacket` property.
        In result, the lazy loading will only succeed if the ZIP handle is opened.

        .. note::

          We recommend using Python's context manager to ensure `zip_handle` is closed:

          >>> import zipfile
          >>> with zipfile.ZipFile("all_phenopackets.zip") as zf:  # doctest: +SKIP
          ...   ps = PhenopacketStore.from_release_zip(zf)
          ...   # Do things here...

        :param zip_file: a ZIP archive handle.
        :param strategy: a `str` with strategy for loading phenopackets, one of `{'eager', 'lazy'}`.
        :returns: :class:`PhenopacketStore` with data read from the archive.
        """
        assert strategy in (
            "eager",
            "lazy",
        ), f"Strategy must be either `eager` or `lazy`: {strategy}"

        root = zipfile.Path(zip_file)

        # Prepare paths to cohort folders
        # and collate paths to cohort phenopackets.
        cohort2path = {}
        cohort2pp_paths = defaultdict(list)
        for entry in zip_file.infolist():
            entry_path = zipfile.Path(zip_file, at=entry.filename)
            if entry_path.is_dir():
                if entry_path.parent == root:
                    name = entry_path.name
                else:
                    cohort_name = entry_path.name
                    cohort2path[cohort_name] = entry_path
            elif entry_path.is_file() and entry_path.suffix == ".json":
                # This SHOULD be a phenopacket!
                cohort = entry_path.parent.name  # type: ignore
                cohort2pp_paths[cohort].append(entry_path)

        # Put cohorts together
        cohorts = []
        for cohort, cohort_path in cohort2path.items():
            if cohort in cohort2pp_paths:
                rel_cohort_path = zipfile.Path(
                    zip_file, at=cohort_path.relative_to(root)
                )
                pp_infos = []
                for pp_path in cohort2pp_paths[cohort]:
                    path = pp_path.relative_to(cohort_path)
                    if strategy == "eager":
                        pi = EagerPhenopacketInfo.from_path(path, pp_path)
                    elif strategy == "lazy":
                        pi = ZipPhenopacketInfo(
                            path=path,
                            pp_path=pp_path,
                        )
                    pp_infos.append(pi)

                ci = CohortInfo(
                    name=cohort,
                    path=str(rel_cohort_path),
                    phenopackets=tuple(pp_infos),
                )
                cohorts.append(ci)

        path = pathlib.Path(str(root))
        return DefaultPhenopacketStore(
            name=name,
            path=path,
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

        The phenopackets are loaded *eagerly* into memory.
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
                            pi = EagerPhenopacketInfo(
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

        return DefaultPhenopacketStore(
            name=nb_path.name,
            path=nb_path,
            cohorts=cohorts,
        )

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def path(self) -> pathlib.Path:
        pass

    @abc.abstractmethod
    def cohorts(self) -> typing.Collection[CohortInfo]:
        pass

    @abc.abstractmethod
    def cohort_for_name(
        self,
        name: str,
    ) -> CohortInfo:
        pass

    def iter_cohort_phenopackets(
        self,
        name: str,
    ) -> typing.Iterator[Phenopacket]:
        """
        Get an iterator with all phenopackets of a cohort.

        :param name: a `str` with the cohort name.
        """
        return self.cohort_for_name(name).iter_phenopackets()

    def cohort_names(self) -> typing.Iterator[str]:
        return map(lambda ci: ci.name, self.cohorts())

    def cohort_count(self) -> int:
        return len(self.cohorts())

    def phenopacket_count(self) -> int:
        return sum(len(cohort) for cohort in self.cohorts())


class DefaultPhenopacketStore(PhenopacketStore):

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

    def cohort_for_name(
        self,
        name: str,
    ) -> CohortInfo:
        return self._cohorts[name]


class ZipPhenopacketInfo(PhenopacketInfo):
    """
    Loads phenopacket from a Zip file on demand.
    """

    # NOT PART OF THE PUBLIC API

    def __init__(
        self,
        path: str,
        pp_path: zipfile.Path,
    ):
        self._path = path
        self._pp_path = pp_path

    @property
    def path(self) -> str:
        return self._path

    @property
    def phenopacket(self) -> Phenopacket:
        return Parse(self._pp_path.read_text(), Phenopacket())

    def __str__(self) -> str:
        return f"ZipPhenopacketInfo(path={self._pp_path})"

    def __repr__(self) -> str:
        return f"ZipPhenopacketInfo(path={self._path}, pp_path={self._pp_path})"
