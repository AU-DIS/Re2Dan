"""
Class for simple search
"""

import pandas as pd

from re2dan.demo.search.searchEngine import SearchEngine
from re2dan.demo.search.simple_search.simple_search import search_by_url
from re2dan.demo.search.simple_search.simple_search import search_by_regex_id
from re2dan.demo.search.simple_search.simple_search import search_by_title

class Simple(SearchEngine):
    def __init__(self, text_path, inverted_index):
        """Load model, data, and embeddings for model."""
        # Load data and doc embeddings
        self.data = pd.read_pickle(text_path).set_index('docid')
        self.inverted_index = inverted_index

    def get_results(self, query, top_k=5, unit=None, department=None):
        """Return top-k most similar documents to query"""
        # Remove filter if All from frontend
        if unit == "All": unit = None
        
        # Query documents and output results
        results_json = {'query': query, 'unit': unit, 'department': department, 'results': []}
        # Filter data and embeddings by unit and department if provided
        data, _ = super().filter_docs(self.data, None, unit, department)
        
        query = query.lower()
        scores = []
        hits = search_by_url(query)
        if hits is None:
                hits = search_by_title(query)

                if hits is None:  # search by part of title
                    hits, scores = self.inverted_index.search('"'+query+'"', 'Afsnit')  # we do a phrase search of the title, not every possibility, but the full title

                    if len(hits) == 0:  # search by regex
                        hits, corrected_match, query = search_by_regex_id(query)

                        if hits is None:  # búsqueda de palabras, la que sea
                            # print('search_by_query____', query)
                            if ' ' not in query:
                                hits, scores = self.inverted_index.search(query)
                            else:
                                hits, scores = self.inverted_index.search(query)
                                # hits = util.semantic_search(query_embedding, embeddings, top_k=results)[0]
                        elif len(corrected_match) != len(query):  # hay que hacer otra búsqueda de palabras

                            query = query.replace(corrected_match, '')
                            hits, scores = self.inverted_index.search(query)

        if isinstance(hits, list): hits = hits[:top_k]

        rank = 1
        for i, h in enumerate(hits):
            if h not in data.index: continue
            title = data.loc[h]['title']
            docid = h
            similarity_score = scores[i] if len(scores) == len(hits) else -1
            url = data.loc[h]['url']
            results_json['results'].append({'searchIndex': rank, 'document': title, 'documentId': docid, 'url': url,'similarityScore': similarity_score})
            rank += 1
        return results_json
    

if __name__ == "__main__":
    import spacy
    from re2dan.demo.inverted_index.inverted_index_pyterrier import InvertedIndexPyterrier as InvertedIndex

    nlp = spacy.load("da_core_news_lg")
    path = './re2dan/demo/inverted_index/pyterrier_index/pyterrier_index'
    fields = ['Emneord','Afsnit','content']
    inverted_index = InvertedIndex(nlp, path=path, fields=fields)
    text_path = "re2dan/files/documents/3_extracting/edok_text_extracted.pkl"
    model = Simple(text_path, inverted_index)
    print(model.get_results("1900-01-01 02:11:04"))

