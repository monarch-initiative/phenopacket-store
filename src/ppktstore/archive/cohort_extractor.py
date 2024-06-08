import os
import typing
import shutil
import tarfile
import tempfile
from collections import defaultdict
import pandas as pd
from google.protobuf.json_format import Parse
from phenopackets import Phenopacket

from .cohort import Cohort


class CohortEntry:
    def __init__(self,
                 disease_id:str,
                 disease_label:str,
                 gene_symbol:str,
                 phenopacket_id:str,
                 pmid:str,
                 file_name:str) -> None:
        self._disease_id = disease_id
        self._disease_label = disease_label
        self._gene_symbol = gene_symbol
        self._phenopacket_id = phenopacket_id
        self._pmid = pmid
        self._file_name = file_name

    @property
    def disease_id(self):
        return self._disease_id
    
    @property
    def disease_label(self):
        return self._disease_label
    
    @property
    def gene_symbol(self):
        return self._gene_symbol
    
    @property
    def phenopacket_id(self):
        return self._phenopacket_id
    
    @property
    def pmid(self):
        return self._pmid
    
    @property
    def filename(self):
        return self._file_name


class CohortExtractor:
    """
    This class helps organize the task of extracting all phenopackets from the notebooks of
    phenopacket-store and of archiving them with zip and tar/gz.
    """
    def __init__(self, notebook_dir:str, one_ppkt_per_disease:bool=False) -> None:
        """
        :param notebook_dir: path to the directory that contains all of the subdirectories for cohorts
        """
        if not os.path.isdir(notebook_dir):
            raise ValueError(f"Could not find phenopacket notebook directory at {notebook_dir}")
        self._entries = []
        n_total_diseases = 0
        self._dx_to_file_d = defaultdict(list)
        for (dirpath, dirnames, filenames) in os.walk(notebook_dir):
            if dirpath.endswith("phenopackets") and not dirpath.endswith("v1phenopackets"):
                lpath_components = dirpath.split(os.sep)
                json_files = filter(lambda f: f.endswith('.json'), filenames)
                for jsonFile in json_files:
                    with open(os.path.join(dirpath, jsonFile)) as f:
                        ppack = Parse(f.read(), Phenopacket())
                        if len(ppack.diseases) != 1:
                            raise ValueError(f"Invalid number of diseases for phenopacket {ppack.id}: {len(ppack.diseases)}")
                        dx = ppack.diseases[0].term.id
                        if one_ppkt_per_disease and dx in self._dx_to_file_d:
                            continue # only take one example per disease
                        else:
                            disease_label = ppack.diseases[0].term.label
                            pmid = CohortExtractor.get_pmid(ppack.meta_data)
                            gene = CohortExtractor.get_gene(ppack.interpretations[0].diagnosis)
                            entry = CohortEntry(disease_id=dx, disease_label=disease_label, gene_symbol=gene, pmid=pmid, phenopacket_id=ppack.id, file_name=jsonFile)
                            self._entries.append(entry)
                            self._dx_to_file_d[dx].append(os.path.join(dirpath, jsonFile))
                            n_total_diseases += 1
            print(f"We found {n_total_diseases} diseases (one phenopacket per disease).")

        
        
    def _copy_files_to_temporary_directory(self, tmpdirname: str, flat=False) -> int:
        n_copied_files = 0
        for omim_id, file_list in self._dx_to_file_d.items():
            for file_path in file_list:
                temp_cohort_dir = tmpdirname
                # original files
                shutil.copy(file_path, temp_cohort_dir)
                n_copied_files += 1
        return n_copied_files
    
    def get_zip(self, outfilename: str):
        tsvFileName = outfilename + '.tsv'
        if outfilename.endswith(".zip"):
            raise ValueError("Do not add .zip to file name; this is done automatically")
        with tempfile.TemporaryDirectory() as tmpdirname:
            n_copied_files = self._copy_files_to_temporary_directory(tmpdirname, True)
            self._create_tsv_file(os.path.join(tmpdirname, tsvFileName))
            shutil.make_archive(outfilename, 'zip', tmpdirname)
        f = os.path.abspath(os.getcwd())
        print(f"Added {n_copied_files} files to zip archive at {f}/{outfilename}")

    def _create_tsv_file(self, tsvFileName:str="per_gene_cohort.tsv"):
        column_names = ['disease_label', 'disease_id',  'gene', 'phenopacket_id', 'pmid',  'file']
        rows = []
        for entry in self._entries:
            rows.append({
                column_names[0]: entry.disease_label, 
                column_names[1]: entry.disease_id,
                column_names[2]: entry.gene_symbol,
                column_names[3]: entry.phenopacket_id,
                column_names[4]: entry.pmid,
                column_names[5]: entry.filename,
            })
        df = pd.DataFrame.from_records(rows, columns=column_names)
        with open(tsvFileName, 'w') as write_tsv:
            write_tsv.write(df.to_csv(sep='\t', index=False))


    @staticmethod
    def get_gene(diagnosis) -> typing.Tuple[str, typing.List[str]]:
        """
        Extract the gene symbol, failing that the label, for a variant from the Interpretation object.
        Also get the alleles.
        """
        gene = None
        for genomic_interpretation in diagnosis.genomic_interpretations:
            if genomic_interpretation.variant_interpretation:
                if genomic_interpretation.variant_interpretation.variation_descriptor:
                    var_desc = genomic_interpretation.variant_interpretation.variation_descriptor
                    gene = None
                    if var_desc.HasField("gene_context"):
                        gene = var_desc.gene_context.symbol
                    if gene is None:
                        gene = var_desc.label
                    return gene
        return gene
    
    @staticmethod
    def get_pmid(meta_data) -> str:
        if meta_data.external_references:
           return meta_data.external_references[0].id
        else:
            # should never happen
            raise ValueError('Cannot extract PMID')
    

   