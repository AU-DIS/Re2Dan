"""
Extracts information from the parsed documents to be used in the search engine
"""

import json
import os
import csv
from tqdm import tqdm
import pandas as pd

parsed_docs = pd.read_pickle('../2_parsing/edok_parsed_docs.pkl')
filename = 'edok_text_extracted.pkl'
columns = ['docid', 'title', 'keywords', 'description', 'text', 'url', 'filters']
text_details = pd.DataFrame(columns=columns)

def getFilters(levelDisplay):
    levelDisplay = levelDisplay.split('¤')
    filters = {}
    for filter in levelDisplay:
        # May be just the unit, or the unit and department
        filter_split = filter.split(" > ")
        assert len(filter_split) < 3
        unit = filter_split[0]
        dept = filter_split[1] if len(filter_split) == 2 else "All"
        if not unit in filters.keys(): filters[unit] = []
        filters[unit].append(dept)
    return filters

for doc_id in tqdm(parsed_docs):
    doc = parsed_docs[doc_id]
    dbfilepath = doc['document_metadata']['dbfilepath'].strip("/")
    doc_url = f"https://e-dok.rm.dk/edok/Admin/GUI.nsf/Desktop.html?open&openlink=https://e-dok.rm.dk/edok/enduser/portal.nsf/Main.html?open&unid={doc_id}&dbpath=/{dbfilepath}/&windowwidth=1100&windowheight=600&windowtitle=S%F8g"
    data = pd.Series({
        'docid': doc_id,
        'title': doc["Afsnit"],
        'keywords': doc["Emneord"] if "Emneord" in doc else [],
        'description': doc["Description"] if "Description" in doc else "",
        'text': doc["content"],
        'url': doc_url,
        'filters': getFilters(doc["LevelDisplay"])
    })
    text_details = pd.concat([text_details, data.to_frame().T], ignore_index=True)

text_details.to_pickle(filename)
