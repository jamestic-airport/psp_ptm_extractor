import requests
from bs4 import BeautifulSoup
import pprint
import json
import csv


# Read protein list from proteins.txt
with open('proteins.txt', 'r') as file:
    protein_list = file.readlines()
    # Strip any whitespace characters (including newline characters) from each line
    protein_list = [line.strip() for line in protein_list]
file.close


# Headers are 'HTP', 'ID', 'LTP', 'MODCOLOR', 'MODIFICATION', 'NMER', 'POS', 'PUBMED', 'REF', 'allNum'
headers = ['PROTEIN', 'MODIFICATION', 'ID', 'NMER', 'REF', 'HTP', 'LTP', 'PUBMED', 'allNum']
ptm_data = list()

for protein in protein_list:
    print(protein)
    url = f"https://www.phosphosite.org/proteinAction?id={protein}&showAllSites=true" # Retrieve PTM info from URL
    response = requests.get(url) # Send a GET request to the URL and retrieve the HTML content
    html = response.content
    soup = BeautifulSoup(html, "html.parser") # Parse the HTML content using BeautifulSoup

    # PTMS are stored in the div class 'data container' under the param id 'PTMsites'. Extract PMT information
    # into a list of dicts
    ptms_param = soup.find('param', id = 'PTMsites')
    if ptms_param:
        ptms = ptms_param['value'] # This is a json string
        ptms = json.loads(ptms) # Converts json string to list of dicts
    else:
        print('No PTMS for this ribosomal protein.')
        continue

    # Cleaning up NMER string from 'EKVKVNG<font color=#993333>k</font>TGNLGNV' to 'EKVKVNGkTGNLGNV'
    for fields in ptms:
        nmer_string = fields.get('NMER')
        new_string = nmer_string.replace("<font color=#993333>", "").replace("</font>", "")
        fields['NMER'] = new_string

        fields['PROTEIN'] = protein

    ptm_data.extend(ptms)
    print(type(ptms))


# Writing into output.tsv
with open('output.tsv', 'w', newline='') as file:
    writer = csv.DictWriter(file, delimiter='\t', fieldnames=headers) # Create a TSV writer object
    writer.writeheader() # Write the header row to the file
    for row in ptm_data: # Write each dictionary in the list to a row in the file
        writer.writerow({key: value for key, value in row.items() if key in headers})
file.close()



