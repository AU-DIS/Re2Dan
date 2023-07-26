from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pandas as pd
import pickle
import sys

# Load the text sections to embed
text_to_embed = pd.read_pickle('text_to_embed.pkl')

# Load make-multilingual fine-tuned model
model_path = "../../demo/search/model_search/"
model_name = "make-multilingual-en-da-2023-06-07_08-47-26"
embedder = SentenceTransformer(model_path + model_name)
doc_embs = embedder.encode(list(text_to_embed['text']), show_progress_bar = True, convert_to_tensor=True)

pickle.dump((doc_embs), open("edok_corpus_embeddings_sections_{}.pkl".format(model_name), 'wb'))

# Check the embeddings
with open("edok_corpus_embeddings_sections_{}.pkl".format(model_name), 'rb') as f:
    doc_emb = pickle.load(f)
    print(len(doc_emb), "document embeddings generated", doc_emb.shape)
