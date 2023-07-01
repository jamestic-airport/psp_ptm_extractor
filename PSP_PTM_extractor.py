import requests
from bs4 import BeautifulSoup
import pprint
import json
import csv
import pandas as pd


# Reads an excel spreadsheet of all ribosomal proteins. Creates a key value pair of all
# PSP codes to their matching single gene names. This is used to generate cleaner output
# for the final tsv table
def get_uniprot_names():

    df = pd.read_excel('Human_Ribosome_List.xlsx')
    proteins = df.to_dict(orient='records')
    code_dict = dict()
    for protein in proteins:
        psp_code = str(protein['PSP Code']).strip()
        entry = protein['Entry'].strip()
        entry_name = protein['Entry Name'].strip()
        code_dict[psp_code] = [entry, entry_name]
    return code_dict


# Read protein list from proteins.txt
filepath = 'short_proteins.txt'
with open(filepath, 'r') as file:
    protein_list = file.readlines()
    protein_list = [line.strip() for line in protein_list]
file.close

uniprot_names = get_uniprot_names()
#pprint.pprint(uniprot_names)
ptm_data = list()

for protein in protein_list:
    # MODIFICATION RETRIEVAL. For each protein, extract information on every modification found on that protein. 
    # Each modification is represented as a dictionary
    url = f"https://www.phosphosite.org/proteinAction?id={protein}&showAllSites=true" 
    response = requests.get(url) 
    html = response.content
    soup = BeautifulSoup(html, "html.parser") 

    ptms_param = soup.find('param', id = 'PTMsites') # PTMS are stored in the div class 'data container' under the param id 'PTMsites'. 
    if ptms_param:
        ptms = ptms_param['value'] # This is a json string
        modifications = json.loads(ptms) # Converts json string to list of dicts
    else:
        print(f'No PTMS for this ribosomal protein {protein}')
        continue

    # DATA EXTRACTION AND TABLE CREATION. Relevant information about each modification is extracted and
    # outputted as a pandas data frame.
    mod_type_list = []
    mod_pos_list = []
    paper_num_list = []

    mod_count = 0
    for mod in modifications:
        mod_type_list.append(mod['MODIFICATION'])
        mod_pos_list.append(mod['POS'])
        paper_num_list.append(mod['REF'])
        mod_count += 1
  
    df = pd.DataFrame({
        'Accession': uniprot_names[protein][0],
        'Entry': uniprot_names[protein][1],
        'Mod Type': mod_type_list,
        'Mod Position': mod_pos_list,
        'Localization Probability': 'none',
        'No of References': paper_num_list,
        'Database': 'PSP' 
    })

    pd.set_option('display.max_rows', None)   # Set option to display all rows
    pd.set_option('display.max_columns', None)   # Set option to display all columns    
    pd.set_option('display.width', None)
    print(df)

    # Cleaning up NMER string from 'EKVKVNG<font color=#993333>k</font>TGNLGNV' to 'EKVKVNGkTGNLGNV'
    for mod in modifications:
        nmer_string = mod.get('NMER')
        new_string = nmer_string.replace("<font color=#993333>", "").replace("</font>", "")
        mod['NMER'] = new_string
        mod['PROTEIN'] = uniprot_names.get(protein)
    ptm_data.extend(modifications)




