'''server/app.py - main api app declaration'''
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import csv

'''Main wrapper for app creation'''
app = Flask(__name__, static_folder='../build')
CORS(app)

##
# API routes
##

@app.route('/api/item')
def item():
    return jsonify([{'itemA': 'A'}, {'itemB': 'B'}])

@app.route('/api/search/mesh/<term>')
def search_by_mesh(term):
    '''Route to search for publications by MeSH Term(s)'''
    publication_ids = {}
    with open('record_results/medical_record.csv') as mesh_csv:
        csv_reader = csv.reader(mesh_csv, delimeter=',')
        for row in csv_reader:
            # if query matches MeSH term or ID
            if row[1] == term | row[2] == terms:
                publication_ids.add(row[0])
                break
    result = {}
    with open('record_results/paper_record.csv') as pub_csv:
        csv_reader = csv.reader(pub_csv, delimeter=',')
        for row in csv_reader:
            for id in publication_ids:
                if row[0] == id:
                    result.add(jsonify({
                        {'id': row[0]},
                        {'title': row[1]},
                        {'abstract': row[2]},
                        {'year': row[3]},
                        {'month': row[4]},
                        {'author_list': row[5]},
                        {'subject_list': row[6]},
                        {'date': row[7]}}))
    # if miss, return empty list
    return result

@app.route('/api/search/title/<title>')
def search_by_title(title):
    '''Route to search for publications by Title'''
    result = {}
    with open('record_results/paper_record.csv') as pub_csv:
        csv_reader = csv.reader(pub_csv, delimeter=',')
        for row in csv_reader:
            if title in row[1]:
                result.add(jsonify({
                    {'id': row[0]},
                    {'title': row[1]},
                    {'abstract': row[2]},
                    {'year': row[3]},
                    {'month': row[4]},
                    {'author_list': row[5]},
                    {'subject_list': row[6]},
                    {'date': row[7]}}))


##
# View route
##

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
  '''Return index.html for all non-api routes'''
  #pylint: disable=unused-argument
  return send_from_directory(app.static_folder, 'index.html')
