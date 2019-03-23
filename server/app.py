'''server/app.py - main api app declaration'''
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import csv
import os
import utils.records as records

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
    for publication in publications:
        term = publication['mesh']['term']
        if term == '':
             continue
        if term in statistics['mesh_terms']:
            statistics['mesh_terms'][term] += 1
        else:
            statistics['mesh_terms'][term] = 1
    return statistics

def get_author_data(publications):
    '''Returns a list of author data as a dictionary'''

    author_names = set()
    for publication in publications:
        for name in publication['author_list']:
            author_names.add(name)

    result = []
    for author in records.get_author_records():
        for name in author_names:
            if name == author.name:
                result.append(author.to_dict())

    return result


def search_by_author(name):
    '''Search for publications by Author Name or substring of Name'''
    '''Returns all authors whose name contain the parameter name and all of their publications'''

    name_split = name.replace(',', '').lower().split(' ')
    authors = []

    publication_records = records.get_publication_records()
    publications = []
    for author in records.get_author_records():
        match = True
        # split name so that name order does not matter for search (last, first vs first last)
        for part in name_split:
            if part not in author.name.lower():
                match = False
                break
        if match:
            authors.append(author.to_dict())
            # for pmid in author.ids:
            #     for publication in publication_records:
            #         if pmid == publication.id:
            #             if publication not in publications:
            #                 publications.append(publication)
            #             break

    # PMID,Title,Abstract,Year,Month,author_list,subject_list,date
    for publication in records.get_publication_records():
        for author in authors:
            if author['name'] in publication.author_list:
                publications.append(publication.to_dict())
                break

    publications = sorted(publications, key=lambda publication: publication['date'], reverse=True)
    authors = sorted(authors, key=lambda author: author['name'])
    statisitcs = get_statistics(authors, publications)
    result = { 'statistics': statisitcs, 'authors': authors, 'publications': publications }
    return jsonify(result)


def search_by_mesh(term):
    '''Search for publications by MeSH Term(s)'''
    '''Returns all publications that have a matching MeSH term and all of their authors'''

    term = term.lower()
    mesh_num = ''
    for mesh in records.get_mesh_tree():
        if term == mesh.term.lower():
            mesh_num = mesh.num

    if mesh_num == '':
        return jsonify([{'statistics': [], 'authors': [], 'publications': []}])

    publications = []
    for publication in records.get_publication_records():
        if mesh_num in publication.mesh.num:
            publications.append(publication.to_dict())
    
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
    for publication in records.get_publication_records():
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
    for publication in records.get_publication_records():
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

    for p in records.get_publication_records():
        if pmid == p.id:
            publication = p.to_dict() 
            authors = get_author_data([publication])
            authors = sorted(authors, key=lambda author: author['name'])
            statisitcs = get_statistics(authors, [publication])
            result = { 'statistics': statisitcs, 'authors': authors, 'publications': [publication] }
            return jsonify(result)
    return jsonify([{'statistics': [], 'authors': [], 'publications': []}])

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


##
# View route
##

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
  '''Return index.html for all non-api routes'''
  #pylint: disable=unused-argument
  return send_from_directory(app.static_folder, 'index.html')
