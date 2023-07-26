import re
import phunspell
import pickle
from unidecode import unidecode
import os

with open('re2dan/demo/search/simple_search/files/all_titles.pickle','rb') as file:
    all_titles = pickle.load(file)
with open('re2dan/demo/search/simple_search/files/all_titles_unicode.pickle','rb') as file:
    all_titles_unicode = pickle.load(file)
with open('re2dan/demo/search/simple_search/files/all_titles_ids.pickle','rb') as file:
    all_titles_ids = pickle.load(file)

with open('re2dan/demo/search/simple_search/files/dict_words.pickle','rb') as file:
    dict_words = pickle.load(file)

with open('re2dan/demo/search/simple_search/files/mapping_accents.pickle', 'rb') as file:
    mapping_accents = pickle.load(file)

re_id_query = re.compile('(?:(?<= )|(?<=^)|(?<=\t)|(?<=\()|(?<=-))\d{1,}([\.:, -]\d{1,})+[\.:,-]*(?= |\t|\)|$|[A-Za-zÀ-ÖØ-öø-ÿ]{2,})')
re_not_number = re.compile('\D')
re_words = re.compile('(((?<= )|(?<=^))[A-Za-zÀ-ÖØ-öø-ÿ-0-9]+)') # Everything matching is words with some dash

pspell = phunspell.Phunspell('da_DK')

# Edge case for only one word
def search_by_url(query):  # return set(ids) to be consistent with the others
    # print('search_by_url____',query)
    if not query.startswith('http'):
        return None
    if ' ' in query:
        return None
    if 'penDocument' not in query:
        return None
    return set([query.split('?')[0].split('/')[-1]])


# Query is lower case
def search_by_title(query):  # Either returns set(ids) or None
    # print('search_by_title____',query)
    if query in all_titles:
        return all_titles[query]
    if unidecode(query) in all_titles_unicode:  # no debería hacer falta
        return all_titles_unicode[unidecode(query)]
    return None


def search_by_regex_id(query):  # return set(ids), matching_part, edited_query, || None, None, None
    # print('search_by_id____',query)
    match = re_id_query.search(query)
    if match is None:
        return None, None, query

    corrected_match = re_not_number.sub('.', match.group())
    corrected_match = corrected_match[0:-1] if corrected_match[-1] == '.' else corrected_match
    if corrected_match in all_titles_ids:
        return all_titles_ids[corrected_match], corrected_match, query.replace(match.group(), corrected_match)

    return None, corrected_match, query
