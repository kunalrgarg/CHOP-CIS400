'''server/app.py - main api app declaration'''
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import csv
import os
import utils.records as records
import recommendation

'''Main wrapper for app creation'''
app = Flask(__name__, static_folder='../build')
CORS(app)

##
# API routes helpers
##

def get_statistics(authors, publications):
    statistics = {}
    statistics['author_count'] = len(authors)
    statistics['publication_count'] = len(publications)
    statistics['mesh_terms'] = {}
    # mesh_record = records.get_mesh_records()
    # for publication in publications:
    #     terms = publication['mesh_terms']
    #     for term in terms:
    #         numbers = mesh_record.get_numbers(term)
    #         for number in numbers:
    #             parts = number.split('.')
    #             # get top level mesh term
    #             top_level = records.get_top_level_term(parts[0][0])
    #             try:
    #                 statistics['mesh_terms'][top_level] += 1
    #             except KeyError:
    #                 statistics['mesh_terms'][top_level] = 1
    #             for i in range(0, len(parts)):
    #                 term = mesh_record.get_term(parts[:i])
    #                 try:
    #                     statistics['mesh_terms'][term] += 1
    #                 except KeyError:
    #                     statistics['mesh_terms'][term] = 1
    return statistics

def get_author_data(publications):
    '''Returns a list of author data as a dictionary'''

    author_records = records.get_author_records()
    author_ids = set()
    authors = []
    for publication in publications:
        for uid in publication['author_ids']:
            if uid in author_records and uid not in author_ids:
                author_ids.add(uid)
                authors.append(author_records[uid].to_dict())

    return authors


def search_by_author(name):
    '''Search for publications by Author Name or substring of Name'''
    '''Returns all authors whose name contain the parameter name and all of their publications'''

    name_split = name.replace(',', '').lower().split(' ')
    authors = []

    publication_records = records.get_publication_records()
    publications = []

    for uid, author in records.get_author_records().items():
        match = True
        # split name so that name order does not matter for search (last, first vs first last)
        for part in name_split:
            if part not in author.name.lower():
                match = False
                break
        if match:
            authors.append(author.to_dict())
            for pmid in author.pmids:
                if pmid in publication_records:
                    publications.append(publication_records[pmid].to_dict())

    publications = sorted(publications, key=lambda publication: publication['date'], reverse=True)
    authors = sorted(authors, key=lambda author: author['name'])
    statisitcs = get_statistics(authors, publications)
    result = { 'statistics': statisitcs, 'authors': authors, 'publications': publications }
    return jsonify(result)


def search_by_mesh(term):
    '''Search for publications by MeSH Term(s)'''
    '''Returns all publications that have a matching MeSH term and all of their authors'''

    term = term.lower()
    numbers = []
    mesh_record = records.get_mesh_records()
    numbers = mesh_record.get_numbers(term)

    if numbers == []:
        return jsonify([{'statistics': [], 'authors': [], 'publications': []}])

    publications = []
    for pmid, publication in records.get_publication_records().items():
        for number in numbers:
            if number in publication.mesh_numbers:
                publications.append(publication.to_dict())
                break
    
    # get author data
    authors = get_author_data(publications)
    publications = sorted(publications, key=lambda publication: publication['date'], reverse=True)
    authors = sorted(authors, key=lambda author: author['name'])
    statisitcs = get_statistics(authors, publications)
    result = { 'statistics': statisitcs, 'authors': authors, 'publications': publications }
    return jsonify(result)


def search_by_title(title):
    '''Search for publications by Title'''
    '''Returns publications that contain the Keyword in their Title'''

    title = title.lower()
    publications = []
    for pmid, publication in records.get_publication_records().items():
            if title in publication.title.lower():
                publications.append(publication.to_dict())

    authors = get_author_data(publications)
    publications = sorted(publications, key=lambda publication: publication['date'], reverse=True)
    authors = sorted(authors, key=lambda author: author['name'])
    statisitcs = get_statistics(authors, publications)
    result = { 'statistics': statisitcs, 'authors': authors, 'publications': publications }
    return jsonify(result)


def search_by_keyword(keyword):
    '''Search for publications by Keyword'''
    '''Returns publications that contain the Keyword in their Title, Abstract, or Subject List'''

    keyword = keyword.lower()
    publications = []
    for pmid, publication in records.get_publication_records().items():
        if keyword in publication.title or keyword in publication.subject_list or keyword in publication.abstract:
            publications.append(publication.to_dict())

    authors = get_author_data(publications)
    publications = sorted(publications, key=lambda publication: publication['date'], reverse=True)
    authors = sorted(authors, key=lambda author: author['name'])
    statisitcs = get_statistics(authors, publications)
    result = { 'statistics': statisitcs, 'authors': authors, 'publications': publications }
    return jsonify(result)


def search_by_pmid(pmid):
    '''Search for a publication by its PMID'''
    '''Returns the publication (if found) and its authors'''

    publications = records.get_publication_records()
    if pmid in publications:
        publication = publications[pmid].to_dict() 
        authors = get_author_data([publication])
        authors = sorted(authors, key=lambda author: author['name'])
        statisitcs = get_statistics(authors, [publication])
        result = { 'statistics': statisitcs, 'authors': authors, 'publications': [publication] }
        return jsonify(result)
    return jsonify({'statistics': [], 'authors': [], 'publications': []})

##
# API Routes
##

@app.route('/api/search/<query>')
def search_for_publications(query):
    '''Route to search for publication with query by either MeSH term or Title'''
    searchword = request.args.get('type', '').lower()
    if searchword == 'mesh':
        return search_by_mesh(query)
    elif searchword == 'title':
        return search_by_title(query)
    elif searchword == 'author':
        return search_by_author(query)
    elif searchword == 'keyword':
        return search_by_keyword(query)
    elif searchword == 'pmid':
        return search_by_pmid(query)
    return jsonify([{'statistics': [], 'authors': [], 'publications': []}])


@app.route('/api/recommendations/<author_uid>')
def get_recommendations(author_uid):
    authors = records.get_author_records()
    if author_uid in authors:
        author = authors[author_uid]
        author_records = records.get_author_records()
        publication_records = records.get_publication_records()
        abstract_similarities, subject_similarities = records.get_similarities_records()
        collaborators = recommendation.recommend_collaborators(author, author_records, publication_records, abstract_similarities, subject_similarities)
        return jsonify({'collaborators': collaborators})
    else:
        return jsonify({'collaborators': []})


@app.route('/api/mesh')
def get_mesh_tree():
    return jsonify(records.read_mesh_json())
##
# View route
##

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
  '''Return index.html for all non-api routes'''
  #pylint: disable=unused-argument
  return send_from_directory(app.static_folder, 'index.html')
