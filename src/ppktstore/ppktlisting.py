import os
from os.path import join

from google.protobuf.json_format import Parse
from mdutils.mdutils import MdUtils
from mdutils import Html
from phenopackets import Phenopacket
from src.ppktstore import Cohort, PPacket


class PPKtListing:
    mdFile = None
    _cohorts = {}

    def __init__(self, notebook_dir, outFile) -> None:
        self._cohorts = {}
        self._readPPKts(notebook_dir)
        self._createMDFile(outFile)

    def _readPPKts(self, notebook_dir):
        if not os.path.isdir(notebook_dir):
            raise ValueError(f"Could not find phenopacket notebook directory at {notebook_dir}")

        notebookLinks = {}
        for (dirpath, dirnames, filenames) in os.walk(notebook_dir):
            if dirpath.endswith("phenopackets") and not dirpath.endswith("v1phenopackets"):
                lpath_components = dirpath.split(os.sep)
                cohort_name = self._get_cohort_name(lpath_components, dirpath)
                json_files = filter(lambda f: f.endswith('.json'), filenames)
                dxMap = {}
                cohortCount = 0
                for jsonFile in json_files:
                    with open(os.path.join(dirpath, jsonFile)) as f:
                        ppack = Parse(f.read(), Phenopacket())
                        ppackData = self._readPPKTdata(ppack)
                        cohortCount += 1
                        if not ppackData:
                            continue
                        for dx in ppackData:
                            dxMap[dx] = ppackData[dx]

                self._cohorts[cohort_name] = {
                    'count': cohortCount,
                    'dx': dxMap
                }
            else:
                if not dirpath.endswith("input"):
                    notebookLinks[dirpath] = filenames
        for path in notebookLinks:
            lpath_components = path.split(os.sep)
            cohort_name = lpath_components[-1]
            if not cohort_name in self._cohorts:
                continue
            chosenFile = None
            for notebookFile in notebookLinks[path]:
                if notebookFile.endswith('.ipynb'):
                    if not chosenFile:
                        chosenFile = notebookFile
                    if notebookFile.lower() == cohort_name.lower() + '_summary.ipynb':
                        chosenFile = notebookFile
            if chosenFile:
                self._cohorts[cohort_name]['nb'] = join(path, chosenFile)
        print(self._cohorts)

    def _readPPKTdata(self, ppack):
        if not ppack.interpretations:
            return None

        dxList = {}
        for interpretation in ppack.interpretations:
            if not interpretation.diagnosis:
                continue
            dx = interpretation.diagnosis
            dxList[dx.disease.id] = dx.disease.label
        return dxList

    def _get_cohort_name(self, lpath_components, dirpath):
        if len(lpath_components) < 3:
            raise ValueError(f"Unexpected path with {len(lpath_components)} components: {dirpath}")
        return lpath_components[-2]

    def _createMDFile(self, outFile):
        self.mdFile = MdUtils(file_name=outFile)
        self.mdFile.new_header(level=1, title='Collections')
        self.mdFile.new_paragraph(
            'Phenopacket store is a repository of [GA4GH phenopackets](https://pubmed.ncbi.nlm.nih.gov/35705716){:target="_blank"}. '
            'that were mainly created using the Python library [pyphetools](https://github.com/monarch-initiative/pyphetools/){:target="_blank"}. '
            'All of the phenopackets were derived from publised case or cohort reports. We have created one page for each of the collections of '
            'phenopackets offered by this repository.')
        tableData = ["Cohort", "Comments"]
        rowCount = 1
        for cohort in self._cohorts:
            cohortData = self._cohorts[cohort]
            if not 'dx' in cohortData:
                continue
            cohortLink = cohort
            if 'nb' in cohortData:
                cohortLink = '[' + cohort + '](' + cohortData['nb'] + '){:target="_blank"}'
            commentsText = str(cohortData['count']) + ' Phenopackets;'
            for entry in cohortData['dx']:
                label = cohortData['dx'][entry]
                dxLink = self._getDXLink(entry)
                if not dxLink:
                    dxLink = ''
                commentsText += '[' + label + '](' + dxLink + '){:target="_blank"}'

            tableData.extend([cohortLink, commentsText])
            rowCount += 1
        self.mdFile.new_line()
        self.mdFile.new_table(columns=2, rows=rowCount, text=tableData, text_align='left')

    def _getDXLink(self, dxId):
        parts = dxId.split(':')
        if len(parts) != 2:
            return None
        if parts[0].lower() == 'omim':
            return 'https://omim.org/entry/' + parts[1]
        return 'http://purl.obolibrary.org/obo/' + dxId.replace(':', '_')

    def serialize(self):
        self.mdFile.create_md_file()
