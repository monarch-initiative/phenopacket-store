import abc
import typing

from ppktstore.model import PhenopacketStore


class QcChecker(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def check(
        self,
        phenopacket_store: PhenopacketStore,
    ) -> typing.Mapping[str, typing.Sequence[str]]:
        pass


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
