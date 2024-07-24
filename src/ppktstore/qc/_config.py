from ._api import QcChecker
from ._impl import DefaultQcChecker, UniqueIdsCheck


def configure_qc_checker() -> QcChecker:
    checks = (UniqueIdsCheck(),)
    return DefaultQcChecker(checks=checks)
