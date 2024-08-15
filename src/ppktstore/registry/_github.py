import certifi
import io
import json
import logging
import ssl
import typing

from urllib.request import urlopen

from ._api import PhenopacketStoreReleaseService, RemotePhenopacketStoreService


class GitHubPhenopacketStoreReleaseService(PhenopacketStoreReleaseService):
    """
    `GitHubPhenopacketStoreReleaseService` can fetch the Phenopacket Store release tags from GitHub.
    """

    def __init__(
        self,
        timeout: float = 10.0,
    ):
        self._logger = logging.getLogger(__name__)
        self._timeout = timeout
        self._tag_api_url = (
            "https://api.github.com/repos/monarch-initiative/phenopacket-store/tags"
        )
        self._ctx = ssl.create_default_context(cafile=certifi.where())

    def fetch_tags(self) -> typing.Iterable[str]:
        return self._get_tag_names()

    def _get_tag_names(
        self,
    ) -> typing.Iterable[str]:
        self._logger.debug("Pulling tag from %s", self._tag_api_url)

        with urlopen(
            self._tag_api_url,
            timeout=self._timeout,
            context=self._ctx,
        ) as fh:
            tags = json.load(fh)

        if len(tags) == 0:
            raise ValueError("No tags could be fetched from GitHub tag API")
        else:
            self._logger.debug("Fetched %d tags", len(tags))

        return tuple(tag["name"] for tag in tags)


class GitHubRemotePhenopacketStoreService(RemotePhenopacketStoreService):
    """
    `GitHubRemotePhenopacketStoreService` knows how to fetch Phenopacket Store data from GitHub.

    The release ZIP files are fetched.
    """

    def __init__(
        self,
        timeout: float = 30.0,
    ):
        self._logger = logging.getLogger(__name__)
        self._timeout = timeout
        self._ctx = ssl.create_default_context(cafile=certifi.where())
        self._release_url = \
            "https://github.com/monarch-initiative/phenopacket-store/releases/download/{release}/all_phenopackets.zip"

    def fetch_resource(
        self,
        release: str,
    ) -> io.BufferedIOBase:
        self._logger.debug("Using %s as the ontology release", release)

        url = self._release_url.format(
            release=release,
        )
        self._logger.info("Downloading Phenopacket Store from %s", url)

        return urlopen(
            url,
            timeout=self._timeout,
            context=self._ctx,
        )
