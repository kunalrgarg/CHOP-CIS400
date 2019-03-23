import csv

class Author:
    def __init__(self):
        self.ids = []
        self.name = ''
        self.chop = False
        self.penn = False
        self.roles = []
        self.affiliations = []
    
    def to_dict(self):
        d = {}
        d['ids'] = self.ids
        d['name'] = self.name
        d['chop'] = self.chop
        d['penn'] = self.penn
        d['roles'] = self.roles
        d['affiliations'] = self.affiliations
        return d


class Publication:
    def __init__(self):
        self.id = ''
        self.title = ''
        self.abstract = ''
        self.year = 0
        self.month = 0
        self.author_list = []
        self.subject_list = []
        self.date = ''
        self.mesh = Mesh()

    def to_dict(self):
        d = {}
        d['id'] = self.id
        d['title'] = self.title
        d['abstract'] = self.abstract
        d['year'] = self.year
        d['month'] = self.month
        d['author_list'] = self.author_list
        d['date'] = self.date
        d['mesh'] = self.mesh.to_dict()
        return d


class Mesh:
    def __init__(self):
        self.num = ''
        self.desc = ''
        self.term = ''

    def to_dict(self):
        d = {}
        d['num'] = self.num
        d['desc'] = self.desc
        d['term'] = self.term
        return d


# returns a Publication from a given entry in the paper_record.csv
# PMID, Title, Abstract, Year, Month, author_list, subject_list, date
def get_publication(entry):
    publication = Publication()
    publication.id = entry[0]
    publication.title = entry[1]
    publication.abstract = entry[2]
    publication.year = entry[3]
    publication.month = entry[4]
    publication.author_list = entry[5].split(';')
    publication.subject_list = entry[6].split(';')
    publication.date = entry[7]
    return publication


# returns all the publications from paper_record.csv with their MeSH data
def get_publication_records():
    # { publciation id : Mesh }
    mesh_data = {}
    # Desc, Num, PMID, Primary_MeSH
    with open('server/record_results/medical_record.csv') as mesh_csv:
        csv_reader = csv.reader(mesh_csv, delimiter=',')
        for row in csv_reader:
            mesh = Mesh()
            mesh.desc = row[0]
            mesh.num = row[1]
            mesh.term = row[3]
            mesh_data[row[2]] = mesh

    publications = []
    with open('server/record_results/paper_record.csv') as pub_csv:
        csv_reader = csv.reader(pub_csv, delimiter=',')
        for row in csv_reader:
            publication = get_publication(row)
            publication.mesh = mesh_data[publication.id] if publication.id in mesh_data else Mesh()
            publications.append(publication)

    return publications


# returns an Author from a given entry in the author_record.csv
# PMID, Author, author_chop, author_penn, Role, AffiliationInfo
def get_author(entry):
    author = Author()
    author.ids = entry[0]
    author.name = entry[1]
    author.chop = True if entry[2] == '1' else False
    author.penn = True if entry[3] == '1' else False
    author.roles = entry[4]
    author.affiliations = entry[5].split(';')
    return author


# returns all Authors from the author_record.csv
def get_author_records():
    authors = []
    with open('server/record_results/author_record.csv') as author_csv:
        csv_reader = csv.reader(author_csv, delimiter=',')
        for row in csv_reader:
            author = get_author(row)
            authors.append(author)
    return authors


def get_mesh(row):
    mesh = Mesh()
    mesh.num = row[0]
    mesh.desc = row[1]
    mesh.term = row[2]
    return mesh


def get_mesh_tree():
    mesh_tree = []
    with open('server/template/2017MeshTree.csv') as mesh_tree_csv:
        csv_reader = csv.reader(mesh_tree_csv, delimiter=',')
        for row in csv_reader:
            mesh = get_mesh(row)
            mesh_tree.append(mesh)
    return mesh_tree
