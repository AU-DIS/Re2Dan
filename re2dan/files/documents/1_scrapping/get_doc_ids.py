"""
Obtains list of IDs and corresponding dbfilepath for all the documents available in the eDok page without athentication.
List of documents obtained from search page with '*' as the search term and no filters.
"""

import time
import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

SEARCH_URL = "https://e-dok.rm.dk/edok/enduser/Portal.nsf/AEnterpriseSearchJSON?OpenAgent&q=*&startIndex={startIndex}"

startIndex = 1
doc_ids = pd.DataFrame([])
pbar = tqdm()
# Automatically stops when all results are obtained
with open('search_ids.csv','w') as file:
    file.write(f'documentId,dbfilepath\n')
    while True:
        url = SEARCH_URL.format(startIndex=startIndex)
        r = requests.get(url)
        time.sleep(0.25)

        # Get document IDs for current page
        soup = BeautifulSoup(r.text, 'html.parser')
        if soup.find("ol") is None: break  # No more results available on edok
        results = soup.find("ol").find_all("li")
        for i, result in enumerate(results):
            doc_internal_url = result.find("a")['href']
            doc_internal_url = doc_internal_url[:doc_internal_url.find("?")]
            documentId = doc_internal_url[doc_internal_url.rfind("/")+1:]
            dbfilepath = doc_internal_url[:doc_internal_url.rfind("/")]
            # Append documentId and dbfilepath
            file.write(f'{documentId},{dbfilepath}\n')

        startIndex += 10
        pbar.update(10)
    
pbar.close()