from tqdm import tqdm
import pandas as pd

# Load the edok documents
df = pd.read_pickle('../documents/3_extracting/edok_text_extracted.pkl')

def concatenate_text(title, description, keywords, text):
    return str(title + " \n " + description + " \n " + (". ").join(keywords) + " \n" + ". ".join(text.values()))

df["combined"] = df.apply(lambda row: concatenate_text(row["title"], row["description"], row["keywords"], row["text"]), axis = 1)

text_to_embed = []
for i, row in tqdm(df.iterrows(), total=len(df)):
    text_to_embed.extend([
        {
            'docid': row.docid,
            'text': row.title,
            'type':  'title',
            'filters': row.filters
        },
        {
            'docid': row.docid,
            'text': row.combined,
            'type':  'combined',
            'filters': row.filters
        }])
    if row.description:
        text_to_embed.append(
        {
            'docid': row.docid,
            'text': row.description,
            'type':  'description',
            'filters': row.filters
        })
    if row.keywords:
        text_to_embed.append(
        {
            'docid': row.docid,
            'text': ". ".join(row.keywords),
            'type':  'keywords',
            'filters': row.filters
        })
    for k, v in row.text.items():
        text_to_embed.append(
        {
            'docid': row.docid,
            'text': v,
            'type':  f'section - {k}',
            'filters': row.filters
        })

text_to_embed = pd.DataFrame(text_to_embed)
text_to_embed.to_pickle('text_to_embed.pkl')


