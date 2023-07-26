from abc import ABC, abstractmethod

class SearchEngine(ABC):

    @abstractmethod
    def get_results(self, query, top_k=5, unit=None, department=None):
        pass

    def filter_docs(self, data, embeddings, unit, department):
        if not unit:
            return data, embeddings
        if department != 'All':
            idx = data['filters'].apply(lambda x: department in x[unit] if unit in x.keys() else False)
        else:
            idx = data['filters'].apply(lambda x: unit in x.keys())

        data = data[idx]
        if embeddings is not None:
            embeddings = embeddings[idx]
        return data, embeddings

    # Evaluation purposes
    def get_rank(self, query, documentId, maxRank=50, unit=None, department=None):
        results = self.get_results(query, top_k=maxRank, unit=unit, department=department)
        for result in results['results']:
            if result['documentId'] == documentId:
                return result['searchIndex']
        return maxRank
    
    # Evaluation purposes
    def get_rank_from_results(self, results, documentId, maxRank=50):
        for result in results['results']:
            if result['documentId'] == documentId:
                return result['searchIndex']
        return maxRank