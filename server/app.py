'''server/app.py - main api app declaration'''
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import csv
import os

'''Main wrapper for app creation'''
app = Flask(__name__, static_folder='../build')
CORS(app)

##
# API routes
##

def get_author_data(names):
    '''Returns a list of author data in a dictionary'''
    
    # PMID,Author,author_chop,author_penn,Role,AffiliationInfo
    result = []
    with open('server/record_results/author_record.csv') as author_csv:
        csv_reader = csv.reader(author_csv, delimiter=',')
        for row in csv_reader:
            for name in names:
                if name == row[1]:
                    d = {}
                    d['id'] = row[0]            # author's PMID
                    d['name'] = row[1]          # author's name
                    d['chop'] = row[2]          # 1 if author is affiliated with CHOP, 0 otherwise
                    d['penn'] = row[3]          # 1 if author is affiliated with Penn, 0 otherwise
                    d['role'] = row[4]          # author's role (CA = Chief Author, OA = Ordinary Author, PI = Principal Investigator)
                    d['affiliation'] = row[5]   # list of author's affiliations
                    result.append(d)
                    break
    return result


def search_by_author(name):
    '''Search for publications by Author Name or substring of Name'''
    '''Returns all authors whose name contain the parameter name and all of their publications'''
    name = name.lower()
    name_split = name.split(' ')
    authors = []
    # PMID,Author,author_chop,author_penn,Role,AffiliationInfo
    with open('server/record_results/author_record.csv') as author_csv:
        csv_reader = csv.reader(author_csv, delimiter=',')
        for row in csv_reader:
            match = True
            author_name = row[1].lower()
            for part in name_split:
                match &= part in author_name
            if match:
                d = {}
                d['id'] = row[0]            # author's PMID
                d['name'] = row[1]          # author's name
                d['chop'] = row[2]          # 1 if author is affiliated with CHOP, 0 otherwise
                d['penn'] = row[3]          # 1 if author is affiliated with Penn, 0 otherwise
                d['role'] = row[4]          # author's role (CA = Chief Author, OA = Ordinary Author, PI = Principal Investigator)
                d['affiliation'] = row[5]   # list of author's affiliations
                authors.append(d)

    publications = []
    # PMID,Title,Abstract,Year,Month,author_list,subject_list,date
    with open('server/record_results/paper_record.csv') as pub_csv:
        csv_reader = csv.reader(pub_csv, delimiter=',')
        for row in csv_reader:
            author_list = row[5]
            for author in authors:
                if author['name'] in author_list:
                    d = {}
                    d['id'] = row[0]
                    d['title'] = row[1]
                    d['abstract'] = row[2]
                    d['year'] = row[3]
                    d['month'] = row[4]
                    d['author_list'] = row[5]
                    d['subject_list'] = row[6]
                    d['date'] = row[7]
                    publications.append(d)
                    break

    result = {'authors': authors, 'publications': publications}
    return jsonify(result)

def search_by_mesh(term):
    '''Search for publications by MeSH Term(s)'''
    '''Returns all publications that have a matching MeSH term and all of their authors'''
    term = term.lower()
    publication_ids = []
    # Desc,PMID,Primary_MeSH
    with open('server/record_results/medical_record.csv') as mesh_csv:
        csv_reader = csv.reader(mesh_csv, delimiter=',')
        for row in csv_reader:
            # if query matches MeSH term or ID
            if term == row[2].lower():
                publication_ids.append(row[1])
    
    publications = []
    author_names = set()
    # PMID,Title,Abstract,Year,Month,author_list,subject_list,date
    with open('server/record_results/paper_record.csv') as pub_csv:
        csv_reader = csv.reader(pub_csv, delimiter=',')
        for row in csv_reader:
            for id in publication_ids:
                if row[0] == id:
                    # create a dictionary of publication data
                    d = {}
                    d['id'] = row[0]
                    d['title'] = row[1]
                    d['abstract'] = row[2]
                    d['year'] = row[3]
                    d['month'] = row[4]
                    d['author_list'] = row[5]
                    d['subject_list'] = row[6]
                    d['date'] = row[7]
                    # add the dictionary to our list of publications
                    publications.append(d)
                    # add the author names to the author name set
                    for name in row[5].split(';'):
                        author_names.add(name)
                    break
    
    # get author data
    authors = get_author_data(author_names)

    result = {'authors': authors, 'publications': publications}
    return jsonify(result)


def search_by_title(title):
    '''Search for publications by Title'''
    '''Returns all publications whose title contains the parameter title and all their authors'''
    title = title.lower()
    publications = []
    author_names = set()
    # PMID,Title,Abstract,Year,Month,author_list,subject_list,date
    with open('server/record_results/paper_record.csv') as pub_csv:
        csv_reader = csv.reader(pub_csv, delimiter=',')
        for row in csv_reader:
            if title in row[1].lower():
                d = {}
                d['id'] = row[0]
                d['title'] = row[1]
                d['abstract'] = row[2]
                d['year'] = row[3]
                d['month'] = row[4]
                d['author_list'] = row[5]
                d['subject_list'] = row[6]
                d['date'] = row[7]
                publications.append(d)
                for name in row[5].split(';'):
                    author_names.add(name)

    authors = get_author_data(author_names)
    result = {'authors': authors, 'publications': publications}
    return jsonify(result)


@app.route('/api/publications/<query>')
def search_for_publications(query):
    '''Route to search for publication with query by either MeSH term or Title'''
    searchword = request.args.get('type', '').lower()
    if searchword == 'mesh':
        return search_by_mesh(query)
    elif searchword == 'title':
        return search_by_title(query)
    elif searchword == 'author':
        return search_by_author(query)
    return jsonify([])


##
# View route
##

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
  '''Return index.html for all non-api routes'''
  #pylint: disable=unused-argument
  return send_from_directory(app.static_folder, 'index.html')
