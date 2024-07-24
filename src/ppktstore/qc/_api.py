import abc
import typing

from ppktstore.model import PhenopacketStore


class QcCheck(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def make_id(self) -> str:
        """
        Get a `str` with the identifier of the Q/C check.
        """
        pass

    @abc.abstractmethod
    def apply(
        self,
        phenopacket_store: PhenopacketStore,
    ) -> typing.Sequence[str]:
        """
        Check `phenopacket_store` and return a sequence of `str`s with errors.
        """
        pass


class QcResults:
    """
    Results of the Q/C check suite.
    """

    def __init__(
        self,
        results: typing.Mapping[str, typing.Sequence[str]],
    ):
        self._results = results

    def iter_results(
        self,
    ) -> typing.Iterable[typing.Tuple[str, typing.Sequence[str]]]:
        return self._results.items()

    def is_ok(self) -> bool:
        return all(len(issues) == 0 for issues in self._results.values())


class QcChecker(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def check(
        self,
        phenopacket_store: PhenopacketStore,
    ) -> QcResults:
        pass
