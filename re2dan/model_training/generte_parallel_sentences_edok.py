import gzip
import pandas as pd
from tqdm import tqdm

translated = pd.read_pickle('edok/edok_all_translations.pickle')
original = pd.read_pickle('edok/eDok_parsed_documents.pickle')

with gzip.open('parallel-sentences/edok_parallel_sentences.tsv.gz', 'wt', encoding='utf8') as f:
    count = 0
    skipped = 0
    for doc_id in tqdm(translated, total=len(translated.keys())):
        english_doc = translated[doc_id]
        danish_doc = original[doc_id]
        for section_danish in english_doc['mapping_sections']:
            # For evey section name in danish, find danish content and english content
            try:
                section_english = english_doc['mapping_sections'][section_danish]
                english_content = english_doc['content'][section_english]
                danish_content = danish_doc['content'][section_danish]
                f.write(f'{english_content}\t{danish_content}\n')
                count += 1
            except:
                skipped += 1
    print("Translated sections", count)
    print("Skipped sections", skipped)