import pickle
import spacy
from tqdm import tqdm
from re2dan.demo.inverted_index.inverted_index_pyterrier import InvertedIndexPyterrier as InvertedIndex

docs_file = '../../files/documents/2_parsing/edok_parsed_docs.pkl'

with open(docs_file,'rb') as file:
    all_documents = pickle.load(file)
        
    fields = {'Afsnit' : 1.0, 'content': 1.0, 'Emneord':1.0}

    nlp = spacy.load("da_core_news_lg")
    inverted = InvertedIndex(nlp, fields=fields, path=None)
    inverted.index_document(all_documents)