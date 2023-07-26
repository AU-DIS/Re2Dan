from collections import deque
import re
import spacy
import seaborn as sns
from collections import defaultdict

class Context():
    def __init__(self, inverted_index, nlp):
        self.nlp = nlp
        self.inverted_index = inverted_index
        self.re_sy = re.compile('^\W|\W$') # Remove trailing, starting symbols


    def _get_spacy_entities(self, text):
        entities = defaultdict(set) # {lemma : set(mapping)} to search only once for each lemma
        doc = self.nlp(text)
        for t in doc:
            if t.is_stop:
                continue
            if t.pos_ == 'NOUN' or t.pos_ == 'ADJ' or t.pos_ == 'ADV' or t.pos_ == 'PROPN':
                entities[self.re_sy.sub('',t.lemma_).lower().strip()].add(t.text)

        return entities


    def _restrict_entities(self, entities, k=10):  # we could filter outliers or very common words
        cants = deque()
        print('entities: ',entities)
        for lemma, ents in entities.items():
            # cc = 0 if lemma not in self.inverted_index.index['content'] else sum(
            #     x[0] for x in self.inverted_index.index['content'][lemma].values())
            cc = self.inverted_index.getOccurrences(lemma)
            cants.extend([(x, cc) for x in ents])

        cants = list(cants)
        cants.sort(key=lambda tup: -tup[1])
        print('_____________',cants)
        frq = set()  # we only take k with different frequencies
        for i in range(0, len(cants)):
            if len(frq) >= k:
                break
            frq.add(cants[i][1])
        for j in range(i, len(cants)):
            cants[j] = (cants[j][0], 0)  # we set the other quantities to 0, to set color as transparent and be clickable
        return cants


    def _get_annotated_entities(self, entities_f, text): # add color to each word, they are all buttons when colored
        print('get_annotated_entities:',entities_f)
        entities_fs = {x[0] for x in entities_f}
        entities_fd = {x[0]:x[1] for x in entities_f}
        freqs = [x[1] for x in entities_f]

        # Count number of non-zero entities and create color palette
        k = sum(value != 0 for value in entities_fd.values())
        colors = sns.color_palette("light:b", k).as_hex()
        colors.reverse()

        doc = self.nlp(text)
        annot_text = []
        for t in doc:

            if t.text not in entities_fs:
                annot_text.append([t.text])
            else:
                if entities_fd[t.text] == 0:
                    annot_text.append([t.text, "#FFFFFF"]) # set to white, but still clickable
                else:
                    annot_text.append([t.text,colors[freqs.index(entities_fd[t.text])]])

        return annot_text


    def obtain_entities(self, context):
        context = context.strip()
        entities = self._get_spacy_entities(context)
        print('get_spacy_entities',entities)
        entities = self._restrict_entities(entities)
        print('restrict_entities',entities)
        annot_text = self._get_annotated_entities(entities, context)
        print('------------',annot_text)
        return annot_text

if __name__ == "__main__":
    import spacy
    from re2dan.demo.inverted_index.inverted_index_pyterrier import InvertedIndexPyterrier as InvertedIndex

    nlp = spacy.load("da_core_news_lg")

    path = './re2dan/demo/inverted_index/pyterrier_index/pyterrier_index'
    fields = ['Emneord','Afsnit','content']

    inverted_index = InvertedIndex(nlp, path=path, fields=fields)
    
    context = Context(inverted_index, nlp)
    print("Context loaded")
    print(context.obtain_entities("""
    Som nævnt tidligere bør du altid konsultere en læge eller sundhedsperson for at få en korrekt diagnose og behandlingsplan baseret på din specifikke situation.
    """
    ))