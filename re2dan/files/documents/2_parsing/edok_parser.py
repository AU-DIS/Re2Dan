# Parse eDocuments  
# Load documents
# Check sections
import pandas as pd
from tqdm.notebook import tqdm
import os
import json
import re
import sys
from bs4 import BeautifulSoup, NavigableString
from collections import deque
import pickle
import numpy as np

path_dir = '../1_scrapping/'  # Dir with the scrapped documents

def parse_links(soup):

    links = deque()
    linked_documents = deque()

    for x in soup:
        if isinstance(x,NavigableString):
            continue
                  
        if x.a is not None:
            for aa in x.find_all('a'): # missing extraction of TOP
                if aa.get('href') is None:
                    continue
                ref = aa.get('href') 
                if ref.startswith('#'):
                        continue
                ref = f'https://e-dok.rm.dk{ref}' + ref if not ref.startswith('http') else ref
                links.append(ref)
                if 'opendocument' in ref.lower():
                    linked_documents.append(ref.split('?')[0].split('/')[-1])
 

    return links, linked_documents

re_ = re.compile(r'\s+')
s = ''.join(chr(c) for c in range(sys.maxunicode+1))
ws = '|'.join(re.findall(r'\s', s))
ws = ws + '|\u200b'
re_ = re.compile(f'[{ws}]+')
re2_ = re.compile(f'\ufeff')
re3_ = re.compile('\s+')

re_sym = re.compile('(\+{3,}|-{3,}|\?{3,}|\/{3,}|_{3,}|:\\.\.\.\.\\\)')

def parse_document(soup):
    
    dict_document = {}
    title = None
    body = None
    
    links = deque() # Must save individually
    linked_documents = deque()

    for x in soup.find_all('div'):
        if x is None:
            continue
#         print(x)
#         print('----------------------')
        if x.get('class') is None:
            continue
        if x.get('class')[0] == 'collapsible-item-title':
            title = re_.sub(' ',x.text.replace('\n',' '))
            title = re2_.sub('',title)
            title = re3_.sub(' ',title).strip()

        elif x.get('class')[0] == 'collapsible-item-body':
            body = deque()
            for xx in x.children:
                if isinstance(xx,NavigableString):
                    continue
                if xx.a is None:
                    t = re_.sub(' ',xx.text.replace('\n',' '))
                    t = re2_.sub('',t)
                    t = re_sym.sub(' ',t)
                    t = re3_.sub(' ',t).strip()
                    if len(t) > 1:
                        body.append(t)    
                else:
                    if xx.a.get('href') is None: # there is a sub-document structure, but there is no difference according to the sections list
#                         inner = parse_document(xx)
#                         body.append(inner[0])
#                         links.extend(inner[1])
#                         linked_documents.extend(inner[2])
                        pass
                    elif not xx.a.get('href').startswith('#'):
                        ref = xx.a.get('href') 
                        ref = f'https://e-dok.rm.dk{ref}' + ref if not ref.startswith('http') else ref
                        links.append(ref)
                        if 'opendocument' in ref.lower():
                            linked_documents.append(ref.split('?')[0].split('/')[-1])
                        t = re_.sub(' ',xx.text.replace('\n',' '))
                        t = re2_.sub('',t)
                        t = re_sym.sub(' ',t)
                        t = re3_.sub(' ',t).strip()
                        if len(t) > 1:
                            body.append(t)            

        if title is not None and body is not None:
            t = ' '.join(body)
            t = re2_.sub('',t)
            t = re3_.sub(' ',t).strip()
            if len(t) > 1:
                dict_document[title] = t
                
            title = None
            body = None
    
    # post-processing for removing the top level titles that should not be there
    
    return dict_document, links, linked_documents

def parse_simple_document(soup):
    dict_document = {}
    title = None
    body = None

    links = deque()
    linked_documents = deque()

    for x in soup:
        if isinstance(x,NavigableString):
            continue
                
        if x.name.startswith('h'):
            if title is not None:
                if len(body) > 0:
                    t = ' '.join(body)
                    t = re2_.sub('',t)
                    t = re_sym.sub(' ',t)
                    t = re3_.sub(' ',t).strip()
                    if len(t) > 1:
                        dict_document[title] = t
                                    
            title = re_.sub(' ',x.text.replace('\n',' '))
            title = re2_.sub('',title)
            title = re3_.sub(' ',title).strip()
            
            if len(title) == 0:
                if x.a is not None:
                    title = re_.sub(' ',x.a.get('name').replace('\n',' '))
                    title = re2_.sub('',title)
                    title = re3_.sub(' ',title).strip()
        
            body = deque()
        else:
            
            if x.a is not None:
                for aa in x.find_all('a'):
                    if aa.get('href') is None:
                        continue
                    if aa.get('href').startswith('#'):
                        continue
                    ref = aa.get('href') 
                    ref = f'https://e-dok.rm.dk{ref}' + ref if not ref.startswith('http') else ref
                    links.append(ref)
                    if 'opendocument' in ref.lower():
                        linked_documents.append(ref.split('?')[0].split('/')[-1])
            
            if body is not None:
                t = re_.sub(' ',x.text.replace('\n',' '))
                t = re2_.sub('',t)
                t = re_sym.sub(' ',t)
                t = re3_.sub(' ',t).strip()
                if len(t) > 1 and t.lower() != 'tilbage til top':
                    body.append(t)    

    return dict_document, links, linked_documents

fields = ['id', 'Afsnit', 'PlejeLaegelig', 'Versionsnr', 'Status', 
          'Emneord', 'TargetGroup', 'Godkender2', 'StartDato', 'RevisionsDato', 
          'EksternReferenceID', 'EksternReference', 'AttachmentID', 'ShowLocal', 
          'ShowLocalHistory', 'LocalEditID', 'LocalEditText', 'LocalEditName', 'LocalEditStyle', 
          'LocalEditLevel', 'DspStatus', 'PublisherDisplay', 'Profession', 'SenesteRettelse', 'RevisionSendTil', 
          'Publiceres', 'TemplateID', 'LevelName', 'PDFLandScape', 'LevelCode', 'DistributionCode', 'DistributionName', 
          'ShowDistribution', 'ShowPdfPrint', 'NoSearch', 'ShowLocalStartDate', 'ShowLocalUnit', 'LevelDisplay', 
          'PaperCopyLocation', 'PaperCopy', 'GodkenderEkstra', 'WorkflowId', 'DocNumber', 'EditorList', 
          'Description', 'ShowReassessLocalAddition', 'ReferenceDocument', 'SpecialNotificationGroups', 'VisForfatter', 
          'Godkender1', 'ForfatterListe', 'ShowReadReceipt', 'ShowConsent', 'ShowSubscription', 'ShowFavorite', 
          'ShowComment', 'ShowCollection', 'approvallevel', 'OpenMakevalid', 'ShowArchive', 'IsLocalApprover', 
          'BgImage', 'DSPLevelDisplayMakeValid', 'DocIsNotAcceptedMsg',
          'collection_metadata','document_metadata']

all_documents = {}

for ff in tqdm(os.listdir(path_dir + 'documents/')):
    
    if not ff.endswith('json'):
        continue
                
    print(ff)
    
    with open(path_dir + 'documents/'+ ff,'r',encoding='utf8') as file:
        doc = json.load(file)
 
    document = {}
    dict_content = {}
    
    for x in fields:
        if len(doc.get(x,'')) > 0:            
            document[x] = doc[x]

    if 'Emneord' in document:
        document['Emneord'] = doc['Emneord'].split('¤')
    
    if 'Afsnit' in document:
        t = re_.sub(' ',doc['Afsnit'].replace('\n',' '))
        t = re2_.sub('',t)
        t = re3_.sub(' ',t).strip()
        doc['Afsnit'] = t
    
    if len(doc['PrivateNotes']) > 0:
        document['PrivateNotes'] = doc['PrivateNotes']
    
    sections_ = deque()
    for i in range(0,len(doc['Sections'])): # to fix a problem with html code in sectionname and empty sectionname
        tp = BeautifulSoup(doc['Sections'][i]['sectionname']).contents
        if len(tp) > 0:
            tp = re_.sub(' ',tp[0].text).replace('\n','').replace('\r','')
            tp = re2_.sub('',tp)
            t = re_sym.sub(' ',t)
            tp = re3_.sub(' ',tp).strip()
            if len(tp) > 0 and len(tp.split(' ')) >= len(doc['Sections'][i]['sectionid'].split(' ')):
                sections_.append(tp)
            else:
                sections_.append(doc['Sections'][i]['sectionid'])
        else:
            sections_.append(doc['Sections'][i]['sectionid'])
            
    document['sections'] = sections_
    
    if len(document['sections']) > 0:
        soup = BeautifulSoup(doc.get('BodyWeb',''), "html.parser")
        dict_content, links, linked_documents = parse_document(soup)

        if len(dict_content) == 0:
            print('Simple document')
            dict_content, links, linked_documents = parse_simple_document(soup)    
    
    if len(dict_content) == 0:
        soup = BeautifulSoup(doc.get('BodyWeb',''), "html.parser")
        t = re_.sub(' ',doc['body'].replace('\n',' '))
        t = re2_.sub('',t)
        t = re_sym.sub(' ',t)
        t = re3_.sub(' ',t).strip()
        if len(t) > 1:
            dict_content = {document['Afsnit'] : t}
        links, linked_documents = parse_links(soup)
        
    document['content'] = dict_content
    document['links'] = links
    document['linked_documents'] = linked_documents

    all_documents[document['id']] = document

len(all_documents)

with open('edok_parsed_docs.pkl','wb') as file:
    pickle.dump(all_documents,file)


