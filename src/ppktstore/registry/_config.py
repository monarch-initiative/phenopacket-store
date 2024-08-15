import re
import os
import pathlib
import platform
import typing


from ._api import (
    PhenopacketStoreRegistry,
    PhenopacketStoreReleaseService,
    RemotePhenopacketStoreService,
)
from ._github import (
    GitHubPhenopacketStoreReleaseService,
    GitHubRemotePhenopacketStoreService,
)


def configure_phenopacket_registry(
    store_dir: typing.Optional[typing.Union[str, pathlib.Path]] = None,
    release_service: PhenopacketStoreReleaseService = GitHubPhenopacketStoreReleaseService(),
    remote_phenopacket_store_service: RemotePhenopacketStoreService = GitHubRemotePhenopacketStoreService(),
) -> PhenopacketStoreRegistry:
    if store_dir is None:
        store_dir = get_default_ontology_store_dir()
    else:
        if isinstance(store_dir, str):
            store_dir = pathlib.Path(store_dir)
        elif isinstance(store_dir, pathlib.Path):
            pass
        else:
            raise ValueError("`store_dir` must be a `str` or `pathlib.Path`")

    if os.path.isdir(store_dir):
        return PhenopacketStoreRegistry(
            data_dir=store_dir,
            release_service=release_service,
            remote_phenopacket_store_service=remote_phenopacket_store_service,
        )
    else:
        raise ValueError("`store_dir` must point to an existing directory")


def get_default_ontology_store_dir() -> pathlib.Path:
    """
    Get a platform specific absolute path to the data directory.

    The data directory points to `$HOME/.phenopacket-store` on UNIX and `$HOME/phenopacket-store` on Windows.
    The folder is created if it does not exist.
    """
    ps = platform.system()

    if re.match("(linux)|(darwin)", ps, re.IGNORECASE):
        store_dir_name = ".phenopacket-store"
    elif re.match("windows", ps, re.IGNORECASE):
        store_dir_name = "phenopacket-store"
    else:
        raise ValueError(f"Unsupported platform {ps}")

    dir_name = os.path.join(pathlib.Path.home(), store_dir_name)

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    return pathlib.Path(dir_name)
