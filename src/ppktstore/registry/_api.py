import abc
import io
import logging
import os
import pathlib
import re
import shutil
import typing
import zipfile

from ppktstore.model import PhenopacketStore


SEMVER_VERSION_PT = re.compile(
    r"v?(?P<major>\d+)(\.(?P<minor>\d+))?(\.(?P<patch>\d+))?"
)
"""
Pattern for matching basic semantic versioning tags such as `v0.1.2`, `1.2.3`, `1`, or `1.2`.
"""


class PhenopacketStoreReleaseService(metaclass=abc.ABCMeta):
    """
    `PhenopacketStoreReleaseService` knows how to fetch
    the Phenopacket Store release tags (e.g. `0.1.18`).
    """

    @abc.abstractmethod
    def fetch_tags(
        self,
    ) -> typing.Iterable[str]:
        """
        Fetch sequence of Phenopacket Store release tags.
        """
        pass


class RemotePhenopacketStoreService(metaclass=abc.ABCMeta):
    """
    `RemotePhenopacketStoreService` knows how to open a :class:`typing.BinaryIO`
    for reading content of a particular Phenopacket Store `release`.
    """

    @abc.abstractmethod
    def fetch_resource(
        self,
        release: str,
    ) -> io.BufferedIOBase:
        """
        Open a connection for reading bytes of the remote resource.

        :param release: a `str` with the desired Phenopacket Store release.
        :return: a binary IO for reading the Phenopacket Store data.
        """
        pass


class ZipPhenopacketStoreAdaptor:
    """
    A context manager for handling opening and closing of the Phenopacket Store release ZIP handle.

    Phenopackets are loaded in a lazy fashion - no phenopackets are loaded upon store opening.
    """

    def __init__(
        self,
        zip_path: pathlib.Path,
    ):
        assert isinstance(zip_path, pathlib.Path)
        self._path = zip_path
        self._zip_file = None

    def __enter__(self) -> PhenopacketStore:
        assert self._zip_file is None

        self._zip_file = zipfile.ZipFile(self._path)
        return PhenopacketStore.from_release_zip(
            zip_file=self._zip_file,
            strategy="lazy",
        )

    def __exit__(self, exc_type, exc_value, exc_traceback):
        assert isinstance(self._zip_file, zipfile.ZipFile)
        self._zip_file.close()
        self._zip_file = None


class PhenopacketStoreRegistry:
    """
    `PhenopacketStoreRegistry` manages Phenopacket Store releases on a local system.

    The registry fetches a ZIP archive with a specific version of Phenopacket Store
    (or the *latest* version) from GitHub and stores it in a data directory.
    Any subsequent openings of Phenopacket Store will use the local ZIP file.
    """

    def __init__(
        self,
        data_dir: pathlib.Path,
        release_service: PhenopacketStoreReleaseService,
        remote_phenopacket_store_service: RemotePhenopacketStoreService,
    ):
        self._logger = logging.getLogger(__name__)

        assert os.path.isdir(data_dir), "`data_dir` must point to a directory"
        self._data_dir = data_dir

        assert isinstance(release_service, PhenopacketStoreReleaseService)
        self._release_service = release_service

        assert isinstance(
            remote_phenopacket_store_service, RemotePhenopacketStoreService
        )
        self._remote_ps_service = remote_phenopacket_store_service

    def open_phenopacket_store(
        self,
        release: typing.Optional[str] = None,
    ) -> ZipPhenopacketStoreAdaptor:
        """
        Open Phenopacket Store.

        Provides an adaptor object that should be used as a context manager to ensure proper resource cleanup.

        **Example**

        Let's load all phenopackets of the *SUOX* cohort from the `0.1.18` release of Phenopacket Store:

        >>> from ppktstore.registry import configure_phenopacket_registry
        >>> registry = configure_phenopacket_registry()
        >>> with registry.open_phenopacket_store(release="0.1.18") as ps:  # doctest: +SKIP
        ...   phenopackets = list(ps.iter_cohort_phenopackets("SUOX"))
        >>> len(phenopackets)  # doctest: +SKIP
        35

        :param release: a `str` with Phenopacket Store release tag (e.g. `0.1.18`) or `None`
          if the *latest* release should be loaded.
        """
        if release is None:
            release = self._fetch_latest_release_if_missing()

        fpath_ps_release_zip = self.resolve_registry_path(release)

        # Download Phenopacket Release ZIP if missing.
        if not os.path.isfile(fpath_ps_release_zip):
            fdir_ps = os.path.dirname(fpath_ps_release_zip)
            os.makedirs(fdir_ps, exist_ok=True)
            with (
                self._remote_ps_service.fetch_resource(release) as response,
                open(fpath_ps_release_zip, "wb") as fh_ps,
            ):
                fh_ps.write(response.read())

            self._logger.debug("Stored the ontology at %s", fpath_ps_release_zip)

        # Provide PS adaptor
        return ZipPhenopacketStoreAdaptor(fpath_ps_release_zip)

    def clear(
        self,
    ):
        """
        Clear all Phenopacket Store releases.
        """
        to_delete = os.listdir(self._data_dir)

        for item in to_delete:
            full_path = os.path.join(self._data_dir, item)
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)

    def resolve_registry_path(
        self,
        release: typing.Optional[str] = None,
    ) -> pathlib.Path:
        """
        Resolve the path of a specific Phenopacket Store release within the registry.

        Note, the path points to the location of the release ZIP in the local filesystem.
        The path may point to a non-existing file, if the load function has not been run yet.

        **Example**

        >>> from ppktstore.registry import configure_phenopacket_registry
        >>> registry = configure_phenopacket_registry()
        >>> registry.resolve_registry_path(release='0.1.18')  # doctest: +SKIP
        pathlib.Path('/home/user/.phenopacket-store/0.1.18.zip')

        :param release: an optional `str` with the desired PS release (if `None`, the latest release will be provided).
        :return: a path to the PS release file.
        """

        if release is None:
            # Fetch the latest release tag, assuming the lexicographic tag sort order.
            release = self._fetch_latest_release_if_missing()

        return pathlib.Path(os.path.join(self._data_dir, f"{release}.zip"))

    def _fetch_latest_release_if_missing(
        self,
    ) -> str:
        """
        Retrieve the latest Phenopacket Store release tag.

        :return: a `str` with the latest release tag
        :raises ValueError` if unable to retrieve the latest release tag from the release service
        """

        # Fetch the latest release tag, assuming the lexicographic tag sort order.
        tags = tuple(self._release_service.fetch_tags())

        latest_tag_idx = -1
        latest_components = None
        for i, tag in enumerate(tags):
            matcher = SEMVER_VERSION_PT.match(tag)
            if matcher is not None:
                major = matcher.group("major")
                minor = (
                    int(matcher.group("minor"))
                    if matcher.group("minor") is not None
                    else 0
                )
                patch = (
                    int(matcher.group("patch"))
                    if matcher.group("patch") is not None
                    else 0
                )
                current = (major, minor, patch)
                if latest_components is None or current > latest_components:
                    latest_components = current
                    latest_tag_idx = i
            else:
                self._logger.warning('Skipping the release tag %s that does not match semantic versioning', tag)

        if latest_tag_idx < 0:
            raise ValueError("Unable to retrieve the latest tag")
        return tags[latest_tag_idx]
