import argparse
import glob
from collections import defaultdict
import json
import pprint

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("--directory", "-d", required=True, help="name of the directory with phenopackets")
args = ap.parse_args()
input_dir = args.directory

# display a friendly message to the user
print(f"Counting phenopackets by disease in {input_dir}.")


def get_all_phenopackets(indir):
    files = []
    for name in glob.glob(indir  + '/*.json'):
        files.append(name)
    return files
        
       
def get_disease_name(json_file):
    with open(json_file) as f:
        data = json.load(f)
        if 'interpretations' in data:
            interpretations = data['interpretations']
            if len(interpretations) == 1:
                interpretation = interpretations[0]
                if 'diagnosis' in interpretation:
                    diagnosis = interpretation['diagnosis']
                    if 'disease' in diagnosis:
                        disease = diagnosis['disease']
                        return disease.get('label')
    #if we get here, parsing failed
    print(f"[ERROR] Could not find diagnosis in {json_file}")
    return 'N/A'
        
        
        
phenopacket_json_files = get_all_phenopackets(indir=input_dir)
diagnosis_count_d = defaultdict(int)
total_count = 0
for jfile in phenopacket_json_files:
    dname = get_disease_name(jfile)
    diagnosis_count_d[dname] += 1
    total_count += 1
    
for k, v in diagnosis_count_d.items():
    print(f"{k}: {v}/{total_count}")

