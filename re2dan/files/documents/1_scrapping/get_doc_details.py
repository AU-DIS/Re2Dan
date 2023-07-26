"""
Get documents from eDok page. get_doc_ids.py must be run first to obtain list of available IDs and dbfilepath.
"""

import time
import os
import requests
import json
import html_text
import pandas as pd
from tqdm import tqdm
from pathlib import Path

DELAY = 0.25
DOCUMENT_URL = "https://e-dok.rm.dk/{dbfilepath}/aLoadInfoDokRead?OpenAgent&id={documentId}"

# Process document details
def getDocumentDetails(dbfilepath, documentId):
    try:
        r = requests.get(DOCUMENT_URL.format(dbfilepath=dbfilepath, documentId=documentId))
        r_json = r.json()
        time.sleep(DELAY)
    except:
        return None
    if not r_json["success"]:
        return None
    doc_json = r_json["data"]
    document_body = str(html_text.extract_text(doc_json["BodyWeb"]))
    doc_json["body"] = document_body
    doc_json["document_metadata"] = {'dbfilepath': dbfilepath}
    return doc_json

all_docs = pd.read_csv('./search_ids.csv')
Path("./documents/").mkdir(parents=True, exist_ok=True)
for document in tqdm(all_docs.iterrows(), total=len(all_docs)):
    # Get document details
    dbfilepath = document[1][1]
    documentId = document[1][0]
    doc_json = getDocumentDetails(dbfilepath, documentId)
    if doc_json:
        # Create empty starting JSON file
        with open(f"./documents/{documentId}.json", 'w+') as file:
            file.write(json.dumps(doc_json, indent=4, ensure_ascii=False))