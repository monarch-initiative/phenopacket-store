import typing

from collections import Counter, defaultdict

from ppktstore.model import PhenopacketStore

from ._api import QcCheck, QcChecker


class UniqueIdsCheck(QcCheck):
    """
    Check that phenopacket id is unique within the entire phenopacket store.
    """

    def make_id(self) -> str:
        return "unique_ids_check"

    def apply(self, phenopacket_store: PhenopacketStore) -> typing.Sequence[str]:
        id_counter = Counter()
        pp_id2cohort = defaultdict(set)

        for cohort_name in phenopacket_store.cohort_names():
            if cohort_name == 'ANKH':
                x = 123
            cohort = phenopacket_store.cohort_for_name(cohort_name)
            for phenopacket in cohort:
                pp_id = phenopacket.id
                pp_id2cohort[pp_id].add(cohort_name)
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
    ) -> typing.Mapping[str, typing.Sequence[str]]:
        results = {}

        for check in self._checks:
            check_id = check.make_id()
            results[check_id] = check.apply(phenopacket_store)

        return results
