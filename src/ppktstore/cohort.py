from typing import List
from .ppacket import PPacket
import os

class Cohort:

    def __init__(self, name:str, dirpath:str, files:List[str]) -> None:
        self._name = name
        self._dirpath = dirpath
        self._ppacket = [PPacket(os.path.join(dirpath, f)) for f in files]
        self._files = [os.path.join(dirpath, f) for f in files]
        self._fnames = files


    def get_detailed_dict(self):
        items = []
        for pp in self._ppacket:
            d = pp.get_dict()
            d["cohort"] = self._name
            d["directory"] = self._dirpath
            items.append(d)
        return items

    @property
    def name(self):
        return self._name

    @property
    def directory(self):
        return self._dirpath

    @property
    def count(self):
        return len(self._ppacket)

    @property
    def phenopacket_files(self):
        return self._files

    @property
    def fnames(self):
        return self._fnames

    @staticmethod
    def get_detailed_header():
        return ["cohort", "directory","filename", "phenopacket.id", "disease", "n_hpo" , "n_var","n_alleles"]



