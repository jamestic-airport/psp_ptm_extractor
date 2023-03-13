import requests
from bs4 import BeautifulSoup
import pprint
import json
import csv

# Define the protein and the URL to retrieve information
protein = "10696"
url = f"https://www.phosphosite.org/proteinAction?id={protein}&showAllSites=true"

# Send a GET request to the URL and retrieve the HTML content
response = requests.get(url)
html = response.content

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
print(soup.prettify())
# PTMS are stored in the div class 'data container' under the param id 'PTMsites'
ptms_param = soup.find('param', id = 'PTMsites')

if ptms_param:
    ptms = ptms_param['value'] # This is a json string
    ptms = json.loads(ptms) # Converts json string to list of dicts
else:
    print('No PTMS for this ribosomal protein.')
    exit(5)

# Headers are 'HTP', 'ID', 'LTP', 'MODCOLOR', 'MODIFICATION', 'NMER', 'POS', 'PUBMED', 'REF', 'allNum'
headers = ['MODIFICATION', 'ID', 'NMER', 'REF', 'HTP', 'LTP', 'PUBMED', 'allNum']

# Writing into output.tsv
with open('output.tsv', 'w', newline='') as file:
    writer = csv.DictWriter(file, delimiter='\t', fieldnames=headers) # Create a TSV writer object
    writer.writeheader() # Write the header row to the file
    for row in ptms: # Write each dictionary in the list to a row in the file
        writer.writerow({key: value for key, value in row.items() if key in headers})
file.close()





