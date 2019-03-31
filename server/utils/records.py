import csv
import os

class Author:
    def __init__(self):
        self.id = ''
        self.pmids = [] 
        self.name = ''
        self.chop = False
        self.penn = False
        self.roles = []
        self.affiliations = []

    def collaborators(self):
        collabs = set()
        publications = get_publication_records()
        for pmid in self.pmids:
            if pmid in publications:
                publication = publications[pmid]
                for uid in publication.author_ids:
                    collabs.add(uid)
        return collabs
    
    def to_dict(self):
        d = {}
        d['pmids'] = self.pmids
        d['name'] = self.name
        d['chop'] = self.chop
        d['penn'] = self.penn
        d['roles'] = self.roles
        d['affiliations'] = self.affiliations
        d['id'] = self.id
        return d


def collaborators(author_list):
    publications = get_publication_records()
    collabs = set()
    pmids = set()
    for author in author_list:
        pmids = pmids.union(author.pmids)
    for pmid in pmids:
        if pmid in publications:
            publication = publications[pmid]
            for uid in publication.author_ids:
                collabs.add(uid)
    return collabs


class Publication:
    def __init__(self):
        self.id = ''
        self.title = ''
        self.abstract = ''
        self.year = 0
        self.month = 0
        self.author_list = []
        self.mesh_terms = []
        self.subject_list = []
        self.author_ids = []
        self.date = ''
        self.mesh_numbers = []

    def to_dict(self):
        d = {}
        d['id'] = self.id
        d['title'] = self.title
        d['abstract'] = self.abstract
        d['year'] = self.year
        d['month'] = self.month
        d['author_list'] = self.author_list
        d['author_ids'] = self.author_ids
        d['date'] = self.date
        d['mesh_terms'] = self.mesh_terms
        return d

class Mesh:
    def __init__(self):
        self.term = ''      # main meash term
        self.numbers = []    # list of mesh descriptor numbers (the same term could have multiple hiearchy locations)
        self.entries = []   # list of other acceptable terms for this one (synonymous)


class MeshRecords:
    def __init__(self, mesh_terms):
        term_to_num_dict = {}
        num_to_term_dict = {}
        for mesh in mesh_terms:
            for number in mesh.numbers:
                num_to_term_dict[number] = mesh.term
            for entry in mesh.entries:
                term_to_num_dict[entry.lower()] = mesh.numbers
            term_to_num_dict[mesh.term.lower()] = mesh.numbers
        
        self.term_to_num_dict = term_to_num_dict
        self.num_to_term_dict = num_to_term_dict
        self.values = mesh_terms


    def get_term(self, number):
        try:
            return self.num_to_term_dict[number]
        except KeyError:
            return ''


    def get_numbers(self, term):
        try:
            return self.term_to_num_dict[term.lower()]
        except KeyError:
            return []


    def to_dict(self):
        d = {}
        d['numbers'] = self.numbers
        d['entries'] = self.entries
        d['term'] = self.term
        return d


# returns a Publication from a given entry in the paper_record.csv
# PMID, Title, Abstract, Year, Month, author_list, MeSH terms, subject_list, date
def get_publication(entry):
    publication = Publication()
    publication.id = entry[0]
    publication.title = entry[1]
    publication.abstract = entry[2]
    publication.year = entry[3]
    publication.month = entry[4]
    publication.author_list = entry[5].split(';')
    publication.mesh_terms = entry[6].split(';')
    publication.subject_list = entry[7].split(';')
    publication.date = entry[8]
    publication.author_ids = entry[9].split(';')
    return publication


# returns all the publications from paper_record.csv with their MeSH data
def get_publication_records():
    # { publciation id : Mesh }
    mesh_data = {}
    # PMID, [terms], [numbers]
    with open('server/record_results/medical_record.csv') as mesh_csv:
        csv_reader = csv.reader(mesh_csv, delimiter=',')
        for row in csv_reader:
            mesh_data[row[0]] = row[2].split(';')

    publications = {}
    with open('server/record_results/paper_record.csv') as pub_csv:
        csv_reader = csv.reader(pub_csv, delimiter=',')
        for row in csv_reader:
            publication = get_publication(row)
            if '' in publication.mesh_terms:
                publication.mesh_terms.remove('')
            publication.mesh_numbers = mesh_data[publication.id] if publication.id in mesh_data else []
            publications[publication.id] = publication

    return publications


# returns an Author from a given entry in the author_record.csv
# PMID, Author, author_chop, author_penn, Role, AffiliationInfo
def get_author(entry):
    author = Author()
    author.pmids = entry[0].replace('[','').replace(']','').replace(' ','').replace("'",'').split(',')
    author.name = entry[1]
    author.chop = True if entry[2] == '1' else False
    author.penn = True if entry[3] == '1' else False
    author.roles = entry[4]
    author.affiliations = entry[5].split(';')
    author.id = entry[6]
    return author


# returns all Authors from the author_record.csv
def get_author_records():
    authors = {}
    with open('server/record_results/author_record.csv') as author_csv:
        csv_reader = csv.reader(author_csv, delimiter=',')
        for row in csv_reader:
            author = get_author(row)
            authors[author.id] = author
    return authors


def get_mesh(row):
    mesh = Mesh()
    mesh.numbers = row[0].split(';')
    mesh.term = row[1]
    mesh.entries = row[2].split(';')
    return mesh


def get_mesh_records(filepath = 'server/template/2019MeshFull.csv'):
    mesh_tree = []
    print(os.getcwd())
    with open(filepath) as mesh_tree_csv:
        csv_reader = csv.reader(mesh_tree_csv, delimiter=',')
        for row in csv_reader:
            mesh = get_mesh(row)
            mesh_tree.append(mesh)
    return MeshRecords(mesh_tree)


def get_mesh_tree():
    root = {'name': 'Mesh Tree', 'number': '', 'children': []}
    with open('server/template/2019MeshTree.csv') as mesh_tree_csv:
        csv_reader = csv.reader(mesh_tree_csv, delimiter=',')
        for row in csv_reader:
            mesh = get_mesh(row)
            parent = root
            numbers = mesh.num.split('.')
            for number in numbers:
                found = False
                for child in parent['children']:
                    if number == child['number']:
                        parent = child
                        found = True
                        break
                if not found:
                    child = {'name': mesh.term, 'number': number, 'children': []}
                    parent['children'].append(child)
                    break

    return root


class PublicationSimilarities:
    def __init__(self):
        self.pmid = ''
        self.similar_publications = []


def get_publication_similarity(row):
    publication = PublicationSimilarities()
    publication.pmid = row[0]
    for entry in row[1:]:
        d = {}
        d['pmid'] = entry.split(',')[0]
        d['sim'] = entry.split(',')[1]
        publication.similar_publications.append(d)


def get_similarities_records():
    with open('server/record_results/similarities/document_similarities.csv') as similarities_csv:
        csv_reader = csv.reader(similarities_csv, delimiter=',')
        similarities = {}
        for row in csv_reader:
            try:
                sims = []
                for entry in row[1].split(';'):
                    sims.append((entry.split(',')[0], entry.split(',')[1]))
                similarities[row[0]] = sims
            except:
                continue
                # power through!
    return similarities