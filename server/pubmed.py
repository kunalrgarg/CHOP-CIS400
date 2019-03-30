
# coding: utf-8

# In[1]:


import os
import sys
from pathlib import Path


# In[34]:


project_name = 'scosy'
# notebook meant to be under ../scosy/notebookts/pubmed.ipynb
project_path = Path(os.getcwd())
template_path = Path(project_path, 'template')
data_path = Path(project_path, 'record_results')
similarities_path = Path(data_path, 'similarities')

# including the project folder and the utils folder
if str(project_path) not in ''.join(sys.path):
    sys.path.extend([str(project_path)])

print('project path = {0}'.format(project_path))
print('data path = {0}'.format(data_path))
print('sys.path = {0}'.format(sys.path))


# In[58]:


# utils
import argparse
import pandas as pd
import numpy as np
import csv
import string
# pubmed
from utils.parse import parse
from Bio import Entrez
# processing mesh treee hierarchy
import re
# flatten list
from functools import reduce
from operator import iconcat
# nlp
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.tokenize import word_tokenize 
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import gensim


# In[4]:

filename = Path(template_path, '2019MeshTree.txt')
mesh_description_dict = dict()
with filename.open('r') as tree_file:
    header = ''
    for line_ix, line in enumerate(tree_file):
        if line_ix == 0:
            header = line
        # '\n' -> empty line
        # 'TREE_NUMBER    DESCRIPTOR' -> header line
        # '-------------------------' -> visual line
        if line != '\n' and line != header and '----' not in line:
            # subtitute 2 or more spaces by a comma and
            # remove last comma if it appears
            line = re.sub('[\s]{2,}', ',', line).rstrip(',')
            tree_num_desc = line.split(',')
            # this is done for keys with len > 50 (special cases)
            value = tree_num_desc[0]
            key = ' '.join(tree_num_desc[1:])
            key.replace('  ', '')
            mesh_description_dict[key.lower()] = value
            print('number = {0}, term = {1}'.format(value, key))

# mesh_df = pd.DataFrame(columns=['number', 'term'])
# with open(filename) as mesh_tree:  
#    line = mesh_tree.readline()
#    while line:
#         line = re.sub('[\s]{2,}', ',', line).rstrip(',')
#         tree_num_desc = line.split(',')
#         # this is done for keys with len > 50 (special cases)
#         value = tree_num_desc[0]
#         key = ' '.join(tree_num_desc[1:])
#         key.replace('  ', '')
#         mesh_description_dict[key.lower()] = value
#         print('number = {0}, term = {1}'.format(value, key))
#         row = pd.DataFrame([[value, key]], columns=['number', 'term'])
#         mesh_df = mesh_df.append(row, ignore_index=True)
#         line = mesh_tree.readline()
# mesh_df.to_csv(Path(template_path, '2019MeshTree.csv'), index=False)

# # In[47]:


# data_file = Path(project_path, 'results.xml')
# records_handle = data_file.open()
# fetch_records = parse(handle=records_handle)


# # In[48]:


# # contains all the metadata elements on the paper level: PubMed unique Identifier number(PMID), Title, Abstract,
# # Year, Month, AuthorList, SubjectList, date
# paper_df = pd.DataFrame(columns=['pmid', 'title', 'abstract', 'mesh'])

# for record in fetch_records:

#     pmid = record.get('PMID')
#     title = record.get('TI')
#     abstract = record.get('AB')
#     mesh_term = record.get('MH')
    
#     if pmid and abstract:
        
#         if mesh_term and len(mesh_term) > 1:
#             # divide all the mesh with multiple term
#             mesh_term = [x.replace('*', '').lower().split('/')for x in mesh_term]
#             # flatten the list
#             mesh_term = reduce(iconcat, mesh_term, [])

#         row = pd.DataFrame([[pmid, title, abstract, mesh_term]],
#                            columns=['pmid', 'title', 'abstract', 'mesh'])
#         paper_df = paper_df.append(row, ignore_index=True)


# # In[50]:


# paper_df.to_csv(Path(data_path, 'pmid_title_abstract_mesh.csv'),index=False)


# # In[51]:


# paper_df.head()


# # In[63]:


# text = paper_df['title'].astype(str) + paper_df['abstract'].astype(str) + paper_df['mesh'].astype(str)
# text = [x.replace('None', '') for x in text]
# text = pd.DataFrame({'pmid': paper_df.pmid, 'text':text})


# # In[65]:


# text.to_csv(Path(data_path, 'pmid_text.csv'), index=False)


# # In[8]:


# raw_documents = pd.read_csv(Path(data_path, 'pmid_text.csv'))
# raw_documents.head()


# # In[10]:

# # preprocessing: remove stop words, set to lower case, lemmatize
# gen_docs = []
# stop_words = set(stopwords.words('english'))
# lemmatizer = WordNetLemmatizer()
# for text in raw_documents.text:
#     text_tmp = text.translate(str.maketrans('', '', string.punctuation))
#     tokens = [w.lower() for w in word_tokenize(text_tmp)]
#     doc = [lemmatizer.lemmatize(i) for i in tokens if not i in stop_words]
#     gen_docs.append(doc)

# # gen_docs = [[w.lower() for w in word_tokenize(text)] 
# #             for text in raw_documents.text]
# print(gen_docs[:5])

# # create a dict of enntry to pmid
# pmids = {}
# for idx, pmid in enumerate(raw_documents.pmid):
#     pmids[idx] = pmid

# # In[21]:


# # create a dictionary to match tokens to integers
# dictionary = gensim.corpora.Dictionary(gen_docs)
# print(dictionary[5])
# print(dictionary.token2id['road'])
# print("Number of words in dictionary:",len(dictionary))


# # In[22]:


# # lists the number of times each word occurs in the document
# # list of tuples
#     # first = index of the word
#     # second = number of time that appears in that document
# corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]


# # In[31]:


# # number of unique tokens in the first document
# len(corpus[0])


# # <pre>
# # term frequency inverse term frequency (tf-idf):
# #     term frequency = how often a word shows up in a document
# #     inverse document frequency = scale that value by how rare the word is in the corpus
# #     

# # In[33]:


# tf_idf = gensim.models.TfidfModel(corpus)
# print(tf_idf)
# s = 0
# for i in corpus:
#     s += len(i)
# print(s)
# # num_nnz = number of tokens


# # In[52]:


# index = gensim.similarities.Similarity(str(similarities_path),
#                                        tf_idf[corpus], 
#                                        num_features=len(dictionary)) 
# query = next(iter(corpus))
# result = index[query]  # search similar to `query` in index


# # In[66]:


# # yield similarities of the indexed documents
# similarities_df = pd.DataFrame()

# # with Path(similarities_path, 'document_similarities.csv').open(mode='w+') as out_file:
# #     writer = csv.writer(out_file, delimiter=',')
# for doc_sim_ix, doc_sim in enumerate(index):
#         pmid = pmids[doc_sim_ix]#raw_documents.loc[doc_sim_ix]['pmid']
#         c_doc = 'document = {0}, pmid = {1}'.format(doc_sim_ix, pmid)
#         print(c_doc)

#         sorted_sim = sorted(list(enumerate(doc_sim)), key=lambda x:x[1], reverse=True)

#         sims_with_pmids = []
#         for idx, sim in sorted_sim[:100]:
#             sim_pmid = pmids[idx]
#             sims_with_pmids.append('{0},{1}'.format(sim_pmid, sim))

#         sims_with_pmids = ";".join(sims_with_pmids)
#         data = [pmid]
#         data.append(sims_with_pmids)

#         row = pd.DataFrame([data])
#         similarities_df = similarities_df.append(row, ignore_index=True)

# similarities_df.to_csv(Path(similarities_path, 'document_similarities.csv'),index=False)