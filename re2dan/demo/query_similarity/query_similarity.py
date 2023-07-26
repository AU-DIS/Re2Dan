import numpy as np
from collections import deque
import pandas as pd
import fasttext
import faiss #https://github.com/facebookresearch/faiss
from tqdm import tqdm


class QuerySimilarity():

    def __init__(self, path_embeddings_model, path_queries, path_index=None, k=5, max_length=4): # Model is not generated here, it takes it as a parameter, df_queries can be a list, deque
        self.k = k
        self.max_length = max_length
        self.model = fasttext.load_model(path_embeddings_model)

        self.query_index = pd.read_pickle(path_queries) # needed to match the similar index to the name of the query !

        if path_index is None: # create index
            query_embeddings = deque()
            for i in tqdm(range(0, len(self.query_index))):
                query_embeddings.append(self.model.get_sentence_vector(self.query_index[i]))

            self.indexes = deque()
            embedding_dimension = len(query_embeddings[0])

            indexFlatL2 = faiss.IndexFlatL2(embedding_dimension) # Create the index
            vectors = np.stack(query_embeddings)  # Convert the embeddings list of vectors into a 2D array
            indexFlatL2.add(vectors)  # Add the vectors to the index
            self.indexes.append(indexFlatL2)
            faiss.write_index(indexFlatL2, path_embeddings_model.replace('.model','_faiss_indexFlatL2.index'))

        else: # loading indexes
            if isinstance(path_index, str):
                self.indexes = [faiss.read_index(path_index)]
            else:
                self.indexes = deque()
                for x in path_index:
                    self.indexes.append(faiss.read_index(x))

    def get_similar_queries(self, query): # this could be simplify if we don't intend to add any other index/similarity

        query_vector = self.model.get_sentence_vector(query)   # query for which we try to find similar ones

        results = []
        for index in self.indexes:
            D, Ii = index.search(np.stack([query_vector]), 3*self.k) # check similarity values
            # Check length of the query
            results_temp = [(self.query_index[Ii[0][i]], D[0][i]) for i in range(0, len(D[0]))][1:]
            results_temp = [x for x in results_temp if len(x[0].split(" ")) <= self.max_length]
            results.extend(results_temp)

        results.sort(key = lambda x: x[1])
        return [x[0] for x in results][:self.k]

if __name__ == "__main__":
    print('Mini test')

    path_dir = "re2dan/demo/query_similarity/files/"
    
    path_embeddings_model = path_dir + 'fasttext_queries_read_documents_featuresize-300_model-skipgram_iter-100.model'
    path_index = path_dir + 'fasttext_queries_read_documents_featuresize-300_model-skipgram_iter-100__faiss_indexFlatL2.index'
    path_queries = path_dir + 'queries_indexes.pickle'
    k = 5

    qq_similarity = QuerySimilarity(path_embeddings_model,path_queries,path_index,k)

    print(qq_similarity.get_similar_queries('neurologi'))