"""
Class for models for semantic search using make_multilingual script and embeddings by sections.
"""

from sentence_transformers import SentenceTransformer, util
import pickle
import torch
import io
import pandas as pd

from re2dan.demo.search.searchEngine import SearchEngine

class CPU_Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'torch.storage' and name == '_load_from_bytes':
            return lambda b: torch.load(io.BytesIO(b), map_location='cpu')
        else: return super().find_class(module, name)


class ModelTranslatedSections(SearchEngine):
    def __init__(self, model_path, text_path, embedded_text_path, embedding_path):
        """Load model, data, and embeddings for model."""
        # Load model
        self.model = SentenceTransformer(model_path)

        # Load data and doc embeddings
        self.data = pd.read_pickle(text_path)
        with open(embedded_text_path, 'rb') as f:
            self.embedded_text = pickle.load(f)
        with open(embedding_path, 'rb') as f:
            if not torch.cuda.is_available():
                self.embeddings = CPU_Unpickler(f).load()
            else:
                self.embeddings = pickle.load(f)

    def get_results(self, query, top_k=5, unit=None, department=None):
        """Return top-k most similar documents to query based on model encodings."""
        # Remove filter if All from frontend
        if unit == "All": unit = None

        # Encode query
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        # Query documents and output results
        results_json = {'query': query, 'unit': unit, 'department': department, 'results': []}
        # Filter data and embeddings by unit and department if provided
        embedded_text, embeddings = super().filter_docs(self.embedded_text, self.embeddings, unit, department)
        data = self.data

        hits = util.semantic_search(query_embedding, embeddings, top_k=top_k)[0]
        for i, h in enumerate(hits):
            rank = i+1
            similarity_score = h['score']
            docid = embedded_text.iloc[h['corpus_id']]['docid']
            document = data[data.docid == docid].iloc[0]
            title = document['title']
            url = document['url']
            results_json['results'].append({'searchIndex': rank, 'document': title, 'documentId': docid, 'url': url,'similarityScore': similarity_score})
        return results_json


if __name__ == "__main__":
    model_name = 'make-multilingual-en-da-2023-06-07_08-47-26'
    model_path = f"re2dan/demo/search/model_search/{model_name}"
    embedded_text_path = f"re2dan/files/embeddings/text_to_embed.pkl"
    embedding_path = f"re2dan/files/embeddings/edok_corpus_embeddings_sections_{model_name}.pkl"
    text_path = "re2dan/files/documents/3_extracting/edok_text_extracted.pkl"
    model = ModelTranslatedSections(model_path, text_path, embedded_text_path, embedding_path)
    print(model.get_results('sukkersyge'))