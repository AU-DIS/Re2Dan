import streamlit as st
import requests
import uuid
from datetime import datetime
import streamlit.components.v1 as components

from re2dan.demo.filters import load_filters, load_units, load_departments

st.set_page_config(page_title=f"eDok Search - Midt")
st.title(f'Search of eDok documents')

BACKEND_API = "http://127.0.0.1:5000"


######################################
def init_state():
    if 'clicked' not in st.session_state:
        st.session_state['clicked'] = None
    if 'query_search' not in st.session_state:
        st.session_state['query_search'] = ''
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid.uuid4())
    if 'query_context' not in st.session_state:
        st.session_state['query_context'] = ""
    if 'context_entities' not in st.session_state:
        st.session_state['context_entities'] = None
    if 'similar_queries' not in st.session_state:
        st.session_state['similar_queries'] = None
    if 'context_update' not in st.session_state:
        st.session_state['context_update'] = None

init_state()

# Filters
filters = load_filters('frontend/department_codes.json')
units = load_units(filters)

# Context Component
def context_component(words, key):
    build_dir = "frontend/ReactComponents/Entities/build"
    _component_func = components.declare_component("context_component", path=build_dir)
    return _component_func(words=words, default='', key=key)
def clear_concepts():
    st.session_state['context_update'] = None
def obtain_entities():
    query_context = st.session_state['query_context']
    if query_context != "":
        st.session_state['context_entities'] = requests.get(f"{BACKEND_API}/api/entities/{query_context}").json()
    else:
        st.session_state['context_entities'] = None

# Update search query
def update_query(query=None):
    clear_concepts()
    if query:
        st.session_state['query_search'] = query
    get_similar_queries()

# Tracking
def tracking(links, key):
    build_dir = "frontend/ReactComponents/Tracking/build"
    _component_func = components.declare_component("tracking", path=build_dir)
    return _component_func(links=links, default='', key=key)

@st.cache_resource
def register_click(session_id, search_term, doc_id, index, time):
    tracking_json = {"session_id": session_id,
                     "search_term": search_term,
                     "doc_id": doc_id,
                     "index": index,
                     "time": time}
    requests.post(f"{BACKEND_API}/api/tracking", json = tracking_json)

# Query similarity
def get_similar_queries():
    query_search = st.session_state['query_search']
    if query_search != "":
        st.session_state['similar_queries'] = requests.get(f"{BACKEND_API}/api/querysimilarity/{query_search}").json()
    else:
        st.session_state['similar_queries'] = None


######################################

# Patient context
st.text_area('Patient info', key='query_context', on_change=obtain_entities)
placeholder_context = st.empty()

# Context
if st.session_state['context_entities']:
    with placeholder_context.container():
        if st.session_state['context_update']:
            query_concepts = st.session_state['query_search'].split(" ")
            if st.session_state['context_update'] in query_concepts:
                query_concepts.remove(st.session_state['context_update'])
            else:
                query_concepts.append(st.session_state['context_update'])
            update_query(" ".join(query_concepts))
        context_component(words=st.session_state['context_entities'], key="context_update")

######################################

# Search functionality
col21, col22 = st.columns([3, 1])
with col21:
    st.text_input('Search query', key='query_search', on_change=update_query)
with col22:
    results = st.number_input("Search results", min_value=5, max_value=30, value=5, step=5)

# Spell suggestion
query_spelling_placeholder = st.empty()

# Query similarity
query_similarity_placeholder = st.empty()

# Filter functionality
col31, col32 = st.columns([2, 2])
with col31:  # Unit filter
    unit = st.selectbox("Unit", units)
with col32:  # Department filter
    departments = load_departments(filters, unit)
    department = st.selectbox("Department", departments)



if st.session_state['query_search']:

    with query_similarity_placeholder.container():
        with st.expander("Other users also searched: "):
            for sq in st.session_state['similar_queries']:
                st.button(sq,type='primary',on_click=update_query,args=(sq,))
            st.markdown(
                """
                <style>
                button[kind="primary"] {
                    background: none!important;
                    border: none;
                    padding: 0!important;
                    color: black !important;
                    text-decoration: underline;
                    cursor: pointer;
                    border: none !important;
                }
                button[kind="primary"]:hover {
                    text-decoration: underline;
                    color: black !important;
                }
                button[kind="primary"]:focus {
                    outline: none !important;
                    box-shadow: none !important;
                    color: black !important;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

    hits = requests.get(f"{BACKEND_API}/api/search/{st.session_state['query_search']}"\
                        f"?unit={unit}&department={department}&results={results}").json()


    query_spelling = requests.get(f"{BACKEND_API}/api/spellcheck/{st.session_state['query_search']}").json()['suggestion']
    if st.session_state['query_search'] != query_spelling:
        with query_spelling_placeholder.container():
            sc1, sc2 = st.columns([2, 4])
            with sc1:
                st.write('Maybe you wanted to search: ')
            with sc2:
                click_spelling = st.button(query_spelling, type='primary', on_click=update_query,args=(query_spelling,))
                st.markdown(
                    """
                    <style>
                    button[kind="primary"] {
                        background: none!important;
                        border: none;
                        padding: 0!important;
                        color: black !important;
                        text-decoration: underline;
                        cursor: pointer;
                        border: none !important;
                    }
                    button[kind="primary"]:hover {
                        text-decoration: underline;
                        color: black !important;
                    }
                    button[kind="primary"]:focus {
                        outline: none !important;
                        box-shadow: none !important;
                        color: black !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

    
    if hits:
        links = []
        for i, h in enumerate(hits['results']):
            # Similarity score: 
            # st.write(h['similarityScore'])
            # with st.empty():
                # st.write(f"{i+1}.- [{h['document']}]({h['url']})")
            links.append([i,h['document'], h['url']])
        
        tracking(links,key='clicked')

        if 'clicked' in st.session_state:
            if st.session_state['clicked'] is not None:
                session_id = st.session_state['session_id']
                index = st.session_state['clicked']
                doc_id = hits['results'][index]['documentId']
                search_term = st.session_state['query_search']
                time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                register_click(session_id, search_term, doc_id, index+1, time)
