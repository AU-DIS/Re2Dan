import re
import pickle
import phunspell

class Spelling():
    def __init__(self, dict_words_file, mapping_accents_file):
        with open(dict_words_file,'rb') as file:
            self.dict_words = pickle.load(file)
        with open(mapping_accents_file, 'rb') as file:
            self.mapping_accents = pickle.load(file)
        self.re_words = re.compile('(((?<= )|(?<=^))[A-Za-zÀ-ÖØ-öø-ÿ-0-9]+)')
        self.pspell = phunspell.Phunspell('da_DK')

    def spell_checking(self, query):
        changes = {}
        # Split query in words (and spaces)
        query = re.sub(' +', ' ', query)  # Remove repeated whitespace
        query_split = self.re_words.split(query)
        query_split = [x for x in query_split if x != '']
        
        for i in range(0, len(query_split)):
            q = query_split[i]
            if len(q) <= 1:
                continue
            if q.isnumeric():
                continue
            if not q.isalpha():
                continue
            if q in self.dict_words:
                continue
            if q in self.mapping_accents:
                query_split[i] = self.mapping_accents[q]
                changes[i] = self.mapping_accents[q]
                continue
            if self.pspell.lookup(q):
                continue
            # Try to fix the word as last resource. Temporary choose first recommendation
            ss = next(self.pspell.suggest(q), None)  # We are taking a chance picking the first suggestion
            if ss is not None:
                changes[i] = ss

        # Generate query suggestion
        query_suggestion = query_split
        for k, v in changes.items():
            query_suggestion[k] = v
        query_suggestion = ''.join(query_suggestion)
        return query_suggestion

# Spelling test
if __name__ == "__main__":
    dict_words_file = 're2dan/demo/search/simple_search/files/dict_words.pickle'
    mapping_accents_file = 're2dan/demo/search/simple_search/files/mapping_accents.pickle'
    spelling = Spelling(dict_words_file, mapping_accents_file)
    print(spelling.spell_checking('sukkersygee  af børnn'))