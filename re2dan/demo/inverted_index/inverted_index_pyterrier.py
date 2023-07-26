import os
os.environ['JAVA_HOME'] = '' # TODO: Add path to jdk
from collections import defaultdict
import jnius_config
import pyterrier as pt
import spacy
from collections import deque
from tqdm import tqdm
import pandas as pd

class InvertedIndexPyterrier():
    def __init__(self, nlp, path=None, fields=None):  # path for the three indices

        jnius_config.vm_running = False # just in case
        if not pt.started():
            pt.init()

        if isinstance(fields, dict) or isinstance(fields, defaultdict):
            self.fields = fields
        else:
            self.fields = {x: 1.0 / len(fields) for x in fields}
        
        if path is not None:
            self.retriever = None
            if 'Emneord' in self.fields:
                retr_k = pt.BatchRetrieve(pt.IndexFactory.of(path + "_keywords/data.properties"),
                                          controls={"wmodel": "BM25"})
                if self.retriever is None:
                    self.retriever = self.fields['Emneord'] * retr_k
                else:
                    self.retriever += self.fields['Emneord'] * retr_k
            if 'Afsnit' in self.fields:
                retr_t = pt.BatchRetrieve(pt.IndexFactory.of(path + "_title/data.properties"),
                                          controls={"wmodel": "BM25"})
                self.retriever_Afsnit = self.fields['Afsnit'] * retr_t
                if self.retriever is None:
                    self.retriever = self.fields['Afsnit'] * retr_t
                else:
                    self.retriever += self.fields['Afsnit'] * retr_t
            if 'content' in self.fields:
                retr_c = pt.BatchRetrieve(pt.IndexFactory.of(path + "_content/data.properties"),
                                          controls={"wmodel": "BM25"})
                if self.retriever is None:
                    self.retriever = self.fields['content'] * retr_c
                else:
                    self.retriever += self.fields['content'] * retr_c

        self.nlp = nlp

    def pre_processing(self, x):
        words = deque()
        for t in self.nlp(x):
            if t.is_punct:
                continue
            if t.pos_ == 'X':
                if len(t) == 1 and not t.text.isalpha():
                    continue
            words.append(t.lemma_.lower())
        return words

    def index_document(self, df_documents):  # allows to build, saves in memory on local path

        def pre_processing_docs(df, column):  # bulk processing
            all_ = deque()
            for docno, text in tqdm(zip(df['docno'], self.nlp.pipe(df[column]))):
                words = deque()
                for t in text:
                    if t.is_punct:
                        continue
                    if t.pos_ == 'X':
                        if len(t) == 1 and not t.text.isalpha():
                            continue
                    words.append(t.lemma_.lower())
                all_.append({'docno': docno, 'text': ' '.join(words)})
            return all_
        
        if isinstance(df_documents, dict) or isinstance(df_documents, defaultdict):
            listi = deque()
            for x, doc in tqdm(df_documents.items()):
                listi.append({'docno': x, 'title': doc['Afsnit'], 'keywords': ' '.join(doc.get('Emneord', [])),
                              'text': ' '.join([v for k, v in doc['content'].items() if k.lower() != 'referencer'])})

            df_documents = pd.DataFrame(listi)
            del listi

        self.retriever = None
        if 'Emneord' in self.fields:
            keywords = pre_processing_docs(df_documents, 'keywords')
            indexer = pt.IterDictIndexer("./pyterrier_index_keywords", blocks=True, stemmer=None, stopwords=None,
                                         tokeniser='whitespace', verbose=True, meta={'docno':33})
            indexer_k = indexer.index(keywords)
            retr_k = pt.BatchRetrieve(pt.IndexFactory.of(indexer_k), controls={"wmodel": "BM25"})
            if self.retriever is None:
                self.retriever = self.fields['Emneord'] * retr_k
            else:
                self.retriever += self.fields['Emneord'] * retr_k

        if 'Afsnit' in self.fields:
            title = pre_processing_docs(df_documents, 'title')
            indexer = pt.IterDictIndexer("./pyterrier_index_title", blocks=True, stemmer=None, stopwords=None,
                                         tokeniser='whitespace', verbose=True, meta={'docno':33})
            indexer_t = indexer.index(title)
            retr_t = pt.BatchRetrieve(pt.IndexFactory.of(indexer_t), controls={"wmodel": "BM25"})
            self.retriever_Afsnit = self.fields['Afsnit'] * retr_t
            if self.retriever is None:
                self.retriever = self.fields['Afsnit'] * retr_t
            else:
                self.retriever += self.fields['Afsnit'] * retr_t

        if 'content' in self.fields:
            content = pre_processing_docs(df_documents, 'text')
            indexer = pt.IterDictIndexer("./pyterrier_index_content", blocks=True, stemmer=None, stopwords=None,
                                         tokeniser='whitespace', verbose=True, meta={'docno':33})
            indexer_c = indexer.index(content)
            retr_c = pt.BatchRetrieve(pt.IndexFactory.of(indexer_c), controls={"wmodel": "BM25"})
            if self.retriever is None:
                self.retriever = self.fields['content'] * retr_c
            else:
                self.retriever += self.fields['content'] * retr_c

    def search(self, query, field=None):  # relies search on the other

        retriever = self.retriever

        if field == 'Afsnit':
            retriever = self.retriever_Afsnit
        elif field is not None:
            raise Exception('Not implemented field')

        if query.startswith('"') and query.endswith('"'):
            query = ' '.join(self.pre_processing(query[1:-1]))
            query = '"' + query + '"'
        elif '+' in query:
            query = query.split('+')
            query = [' '.join(self.pre_processing(q.strip())) for q in
                     query]  # process each part of the + individually
            query = ' +'.join(query)  # combine +
        else:
            query = ' '.join(self.pre_processing(query))

        documents = retriever.search(query)
        documents = documents.sort_values('rank', ascending=True).drop_duplicates('docno', keep='first') # just because doc ids are not aligned in the indexes, could find how to avoid discarding empty documents
        doc_ids = documents['docno'].values.tolist()
        scores = documents['score'].values.tolist()
        return doc_ids, scores
    
    # Returns number of matches. There may be multiple with the same docno?
    def getOccurrences(self, query):
        query = ' '.join(self.pre_processing(query))
        documents = self.retriever.search(query)
        return len(documents['docno'])



if __name__ == "__main__":
    print('Mini test')

    import spacy

    nlp = spacy.load("da_core_news_lg")

    path = './re2dan/demo/inverted_index/pyterrier_index/pyterrier_index'
    fields = ['Emneord','Afsnit','content']

    inverted = InvertedIndexPyterrier(nlp, path=path, fields=fields)

    print(inverted.search('radiology'))
    print(inverted.search('radiology +kvinde'))
    print(inverted.search('"radiology kvinde"'))