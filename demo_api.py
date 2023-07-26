from flask import Flask
from flask import request

import spacy

from re2dan.demo.search.modelTranslatedSections import ModelTranslatedSections
from re2dan.demo.search.simple import Simple
from re2dan.demo.search.combined_search import combineResults
from re2dan.demo.inverted_index.inverted_index_pyterrier import InvertedIndexPyterrier as InvertedIndex
from re2dan.demo.spelling import Spelling
from re2dan.demo.context import Context
from re2dan.demo.query_similarity.query_similarity import QuerySimilarity

app = Flask(__name__)

# Model
model_name = 'make-multilingual-en-da-2023-06-07_08-47-26'
model_path = f"re2dan/demo/search/model_search/{model_name}"
embedded_text_path = f"re2dan/files/embeddings/text_to_embed.pkl"
embedding_path = f"re2dan/files/embeddings/edok_corpus_embeddings_sections_{model_name}.pkl"
text_path = "re2dan/files/documents/3_extracting/edok_text_extracted.pkl"
print("Loading model")
model = ModelTranslatedSections(model_path, text_path, embedded_text_path, embedding_path)
print("Model loaded")

# Spacy NLP
nlp = spacy.load("da_core_news_lg")

# Inverted Index
path = './re2dan/demo/inverted_index/pyterrier_index/pyterrier_index'
fields = ['Emneord','Afsnit','content']
inverted_index = InvertedIndex(nlp, path=path, fields=fields)

# Simple search
text_path = "re2dan/files/documents/3_extracting/edok_text_extracted.pkl"
simplemodel = Simple(text_path, inverted_index)
print("Simple search loaded")

# Spelling
dict_words_file = 're2dan/demo/search/simple_search/files/dict_words.pickle'
mapping_accents_file = 're2dan/demo/search/simple_search/files/mapping_accents.pickle'
spelling = Spelling(dict_words_file, mapping_accents_file)
print("Spelling loaded")

# Context
context = Context(inverted_index, nlp)
print("Context loaded")

# Query similarity
path_dir = "re2dan/demo/query_similarity/files/"
path_embeddings_model = path_dir + 'fasttext_queries_read_documents_featuresize-300_model-skipgram_iter-100.model'
path_index = path_dir + 'fasttext_queries_read_documents_featuresize-300_model-skipgram_iter-100__faiss_indexFlatL2.index'
path_queries = path_dir + 'queries_indexes.pickle'
k = 5
query_similarity = QuerySimilarity(path_embeddings_model, path_queries, path_index, k)
print("Query similarity loaded")

# Return results
@app.get('/api/search/<query>')
def get_results(query):
    results = request.args.get('results', default=5, type=int)
    unit = request.args.get('unit', default='All', type=str)
    department = request.args.get('department', default='All', type=str)
    modelResults = model.get_results(query, top_k=results, unit=unit, department=department)
    simpleResults = simplemodel.get_results(query, top_k=results, unit=unit, department=department)
    hits = combineResults(modelResults, simpleResults, results)
    return hits

@app.get('/api/modelsearch/<query>')
def get_model_results(query):
    results = request.args.get('results', default=5, type=int)
    unit = request.args.get('unit', default='All', type=str)
    department = request.args.get('department', default='All', type=str)
    hits = model.get_results(query, top_k=results, unit=unit, department=department)
    return hits

@app.get('/api/simplesearch/<query>')
def get_simple_results(query):
    results = request.args.get('results', default=5, type=int)
    unit = request.args.get('unit', default='All', type=str)
    department = request.args.get('department', default='All', type=str)
    hits = simplemodel.get_results(query, top_k=results, unit=unit, department=department)
    return hits

# Return spelling check
@app.get('/api/spellcheck/<query>')
def get_spell_check(query):
    query_suggestion = spelling.spell_checking(query)
    return {'suggestion': query_suggestion}

# Return spelling check
@app.get('/api/entities/<patient_context>')
def get_context_entities(patient_context):
    context_entities = context.obtain_entities(patient_context)
    return context_entities

# Return spelling check
@app.get('/api/querysimilarity/<query>')
def get_similar_queries(query):
    similar_queries = query_similarity.get_similar_queries(query)
    return similar_queries

# Record click
@app.post('/api/tracking')
def track_clicks():
    r_json = request.json
    session_id = r_json['session_id']
    search_term = r_json['search_term']
    doc_id = r_json['doc_id']
    index = r_json['index']
    time = r_json['time']
    print("Tracking", session_id, search_term, doc_id, index, time) 
    return "Clicked recorded"

if __name__ == "__main__":
    print("Running API on 5000")
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)