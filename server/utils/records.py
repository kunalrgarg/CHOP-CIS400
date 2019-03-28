import csv

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
        self.subject_list = []
        self.author_ids = []
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
        d['author_ids'] = self.author_ids
        d['date'] = self.date
        d['mesh'] = self.mesh.to_dict()
        return d


class Mesh:
    def __init__(self):
        self.num = ''
        self.desc = ''
        self.term = ''


    def distance(self, other):
        if self.num == '' or other.num == '':
            return -1
        this_mesh = self.num.split('.')
        that_mesh = other.num.split('.')
        if (len(this_mesh) == 0 or len(that_mesh) == 0):
            return -1
        if (this_mesh[0] != that_mesh[0]):  # different branches
            return -1
        for i in range(min(len(this_mesh), len(that_mesh))):
            if this_mesh[i] != that_mesh[i]:
                return len(this_mesh) - i
        if len(this_mesh) > len(that_mesh):
            return len(this_mesh) - len(that_mesh)
        else:
            return 0


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
    publication.author_ids = entry[8].split(';')
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

    publications = {}
    with open('server/record_results/paper_record.csv') as pub_csv:
        csv_reader = csv.reader(pub_csv, delimiter=',')
        for row in csv_reader:
            publication = get_publication(row)
            publication.mesh = mesh_data[publication.id] if publication.id in mesh_data else Mesh()
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
    mesh.num = row[0]
    mesh.term = row[1]
    return mesh


def get_mesh_tree():
    mesh_tree = []
    with open('server/template/2019MeshTree.csv') as mesh_tree_csv:
        csv_reader = csv.reader(mesh_tree_csv, delimiter=',')
        for row in csv_reader:
            mesh = get_mesh(row)
            mesh_tree.append(mesh)
    return mesh_tree


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