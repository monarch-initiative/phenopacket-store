import typing
from .ppacket import PPacket
import os

class Cohort:

    def __init__(self, name:str, dirpath:str, files:typing.Iterable[str]) -> None:
        self._name = name
        self._dirpath = dirpath
        self._fnames = tuple(files)
        self._ppacket = []
        self._files = []
        for file in self._fnames:
            self._ppacket.append(PPacket(os.path.join(dirpath, file)))
            self._files.append(os.path.join(dirpath, file))


    def get_detailed_dict(self):
        items = []
        for pp in self._ppacket:
            d = pp.get_dict()
            d["cohort"] = self._name
            d["directory"] = self._dirpath
            items.append(d)
        return items

    @property
    def name(self) -> str:
        return self._name

    @property
    def directory(self) -> str:
        return self._dirpath

    @property
    def count(self) -> int:
        return len(self._ppacket)

    @property
    def phenopacket_files(self) -> typing.Sequence[str]:
        return self._files

    @property
    def fnames(self) -> typing.Sequence[str]:
        return self._fnames

    @staticmethod
    def get_detailed_header() -> typing.Sequence[str]:
        return ["cohort", "directory","filename", "phenopacket.id", "disease", "n_hpo" , "n_var","n_alleles", "n_encounters"]



