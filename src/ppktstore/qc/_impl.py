import typing

from collections import Counter, defaultdict

from ppktstore.model import PhenopacketStore

from ._api import QcCheck, QcChecker, QcResults


class UniqueIdsCheck(QcCheck):
    """
    Check that phenopacket id is unique within the entire phenopacket store.
    """

    def make_id(self) -> str:
        return "unique_ids_check"

    def apply(self, phenopacket_store: PhenopacketStore) -> typing.Sequence[str]:
        id_counter = Counter()
        pp_id2cohort = defaultdict(set)

        for cohort in phenopacket_store.cohorts():
            for pp_info in cohort.phenopackets:
                pp_id = pp_info.phenopacket.id
                pp_id2cohort[pp_id].add(cohort.name)
                id_counter[pp_id] += 1

        repeated = {pp_id: count for pp_id, count in id_counter.items() if count > 1}

        errors = []
        for pp_id, count in repeated.items():
            msg = f"`{pp_id}` is present in {count} cohorts: {pp_id2cohort[pp_id]}"
            errors.append(msg)
        return errors


class DefaultQcChecker(QcChecker):

    def __init__(
        self,
        checks: typing.Iterable[QcCheck],
    ):
        self._checks = tuple(checks)

    def check(
        self,
        phenopacket_store: PhenopacketStore,
    ) -> QcResults:
        results = {}

        for check in self._checks:
            check_id = check.make_id()
            results[check_id] = check.apply(phenopacket_store)

        return QcResults(results=results)
