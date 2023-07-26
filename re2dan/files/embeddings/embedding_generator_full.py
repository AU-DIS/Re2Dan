from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pandas as pd
import pickle
import sys

# Load the edok documents
df = pd.read_pickle('../documents/3_extracting/edok_text_extracted.pkl')

# Create text for encoder
def concatenate_text(title, description, keywords, text):
    return str(title + " \n " + description + " \n " + (". ").join(keywords) + " \n" + ". ".join(text.values()))

df["combined"] = df.apply(lambda row: concatenate_text(row["title"], row["description"], row["keywords"], row["text"]), axis = 1)

# Load make-multilingual fine-tuned model
model_path = "../../demo/search/model_search/"
model_name = "make-multilingual-en-da-2023-06-07_08-47-26"
embedder = SentenceTransformer(model_path + model_name)
doc_embs = embedder.encode(list(df['combined']), show_progress_bar = True, convert_to_tensor=True)

pickle.dump((doc_embs), open("edok_corpus_embeddings_{}.pkl".format(model_name), 'wb'))

# Check the embeddings
with open("edok_corpus_embeddings_{}.pkl".format(model_name), 'rb') as f:
    doc_emb = pickle.load(f)
    print(len(doc_emb), "document embeddings generated", doc_emb.shape)
