from Bio import Entrez
import csv
import logging
from utils.logger import logger_initialization
from utils.parse import parse
import argparse
import pandas as pd
import pandas.io.formats.excel
import utils.records as records
from pathlib import Path
import os
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.tokenize import word_tokenize 
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import gensim
import string


class Author:
    def __init__(self, name, pmid, role, penn, chop, affiliations, uid, mesh_terms):
        self.name = name
        self.pmids = [pmid]
        self.roles = [role]
        self.penn = penn
        self.chop = chop
        self.uid = uid
        self.mesh_terms = {}
        for mesh in mesh_terms:
            self.mesh_terms[mesh] = 1
        if affiliations is None:
            self.affiliations = []
        elif affiliations is list:
            self.affiliations = affiliations
        else:
            self.affiliations = [affiliations]
    
    # use name and affiliation to determine equality
    def equals(self, other):
        return self.name == other.name
        # if (self.name != other.name):
        #     return False
        # if (self.penn != other.penn):
        #     return False
        # if (self.chop != other.chop):
        #     return False
        # return True


    def combine(self, other):
        self.pmids.extend(other.pmids)
        self.roles.extend(other.roles)
        self.affiliations.extend(other.affiliations)
        self.penn = self.penn or other.penn
        self.chop = self.chop or other.chop
        for mesh in other.mesh_terms:
            try:
                self.mesh_terms[mesh] += 1
            except KeyError:
                self.mesh_terms[mesh] = 1


def assign_roles(author_list):
    """
    assign the chief author, ordinary author or principal investigator role to each author
    :param author_list: a list of all the authors in the paper
    :return: role_list: the authors' respective roles
    """

    role_list = list()

    for author_index in range(len(author_list)):
        # Assign the author's rle
        # if less than 2 authors then they are considered "Chief Authors"
        if author_index <= 1 and author_index != len(author_list) - 1:
            role_list.append('CA')
        # If a person is after the first two authors and it'snt the last author its considered
        # "Ordinary Author"
        elif author_index > 1 and author_index != len(author_list) - 1:
            role_list.append('OA')
        # else "Principal Investigator)
        elif author_index == len(author_list) - 1:
            role_list.append('PI')

    return role_list


def assign_organization(affiliation_list):
    """
    check and assign whether the authors belong to the CHOP or PENN organization.
    :param affiliation_list: a list of all the affiliations of the authors
    :return: chop_list, penn_list: lists with whether the author belong to the CHOP or PENN organization
    """
    if affiliation_list is None:
        return [], []
    # initialize CHOP and PENN authors' organization to None = 0
    chop_list = [0] * len(affiliation_list)
    penn_list = [0] * len(affiliation_list)

    for affiliation_index, affiliation in enumerate(affiliation_list):

        sub_affiliation = affiliation.split(';')

        for sa in sub_affiliation:
            # Assign the author organization
            if 'children' in sa.lower():
                chop_list[affiliation_index] = 1
                break
            elif 'perelman' in sa.lower() or 'school of medicine' in sa.lower() or \
                 'pennsylvania' in affiliation.lower():
                penn_list[affiliation_index] = 1
                break

    return chop_list, penn_list


def convert_mesh_description(mesh_records, mesh_terms):
    """
    returns all valid mesh_terms and numbers from mesh_terms
    """
    matching_terms = []
    matching_numbers = []
    for mesh in mesh_terms:
        term = mesh
        if '/' in term:
            term = term.split('/')[0]
        if '*' in term:
            term = term.replace('*', '')
        if term == '':
            continue
        numbers = mesh_records.get_numbers(term)
        if len(numbers) > 0:
            matching_terms.append(mesh_records.get_term(numbers[0])) # get the correctly capitalized term
            matching_numbers.extend(numbers)

    return matching_terms, matching_numbers


def get_mesh_from_text(mesh_records, abstract):
    if abstract is None or abstract == '':
        return []

    terms = set()
    text = abstract.translate(str.maketrans('', '', string.punctuation))
    tokens = [w.lower() for w in word_tokenize(text)]
    if '' in tokens:
        token.remove('')
    for i in range(len(tokens)):
        try:
            numbers = mesh_records.get_numbers('{0} {1} {2}'.format(tokens[i], tokens[i+1], tokens[i+2]))
            if numbers != []:
                terms.add(mesh_records.get_term(numbers[0]))
            numbers = mesh_records.get_numbers('{0} {1}'.format(tokens[i], tokens[i+1]))
            if numbers != []:
                terms.add(mesh_records.get_term(numbers[0]))
            numbers = mesh_records.get_numbers(tokens[i])
            if numbers != []:
                terms.add(mesh_records.get_term(numbers[0]))
        except IndexError:
            numbers = mesh_records.get_numbers(tokens[i])
            if numbers != []:
                terms.add(mesh_records.get_term(numbers[0]))
                continue

    return list(terms)


def main():
    """
    starts running the script
    :return: None.
    """

    # get the the path for the input file argument
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--retrieve', help='arg use to pull data from PubMed', action='store_true')
    parser.add_argument('-p', '--process', help='arg use to process the info into paper, author, medical and '
                                                'title_abstracts records', action='store_true')
    parser.add_argument('-a', '--analyze', help='run topic modeling on the file', action='store_true')
    parser.add_argument('-f', '--file', help='file to process. Depending on whether the retrieve, process or analysis '
                                             'options were selected, there is a different default file')
    parser.add_argument('-l', '--log', dest='logLevel', choices=['DEBUG', 'INFO', 'ERROR'], type=str.upper,
                        help='Set the logging level')

    args = parser.parse_args()
    logger_initialization(log_level=args.logLevel)
    logging.getLogger('line.regular.time.line').info('Running SCOSY')

    if args.retrieve:

        logging.getLogger('regular').info('retrieving data from PudMed')

        # databases such as PubMed, GenBank, GEO, and many others
        # Use the mandatory email parameter so the NCBI can contact you if there is a proble
        Entrez.email = "guerramarj@email.chop.edu"     # Always tell NCBI who you are
        logging.getLogger('regular').info('searching PubMed for CHOP and UPENN authors')
        handle = Entrez.esearch(db="pubmed", retmax=50000, idtype="esearch", mindate="2014/01/01", maxdate="2020/08/21",
                                term="Perelman School of Medicine[Affiliation] OR Children's Hospital of "
                                     "Philadelphia[Affiliation] OR University of Pennsylvania School of "
                                     "Medicine[Affiliation] OR School of Medicine University of "
                                     "Pennsylvania[Affiliation]",
                                usehistory="y")
        search_results = Entrez.read(handle)
        handle.close()
        # obtaining the list of relevant PMIDs
        id_list = search_results["IdList"]

        # get all the record based on the PMIDs
        logging.getLogger('regular.time').info('getting relevant authors\' records based on PMIDs')
        fetch_records_handle = Entrez.efetch(db="pubmed", id=id_list, retmode="text", rettype="medline")
        # need to read all the data from the handle and store in a file because if we just read line by line from the
        # generator and the internet connection is not strong, then we run into http errors:
        # http.client.IncompleteRead: IncompleteRead(0 bytes read)
        with open("results.xml", "w") as out_handle:
            out_handle.write(fetch_records_handle.read())
        logging.getLogger('regular.time').info('saved authors\' records on local file')
        # the results are now in the results.xml file and the original handle has had all of its data extracted
        # (so we close it)
        fetch_records_handle.close()

    if args.process:

        # import data from file
        logging.getLogger('regular').info('reading data from result file')

        file_name = args.file
        if not file_name:
            file_name = 'results.xml'

        records_handle = open(file_name)
        fetch_records = parse(handle=records_handle)

        # initializing variables
        mesh_records = records.get_mesh_records('template/2019MeshFull.csv')

        # contains all the metadata elements on the author level: PubMed unique Identifier number(PMID), AuthorID (as a
        # (CA) Ordinary Author (OA) or Principal Author (PA) and the author's affiliation
        author_record_df = pd.DataFrame(columns=['PMID', 'Author', 'author_chop', 'author_penn', 'Role',
                                                 'AffiliationInfo', 'UID', 'mesh_terms'])
        # contains all the metadata elements on the paper level: PubMed unique Identifier number(PMID), Title, Abstract,
        # Year, Month, AuthorList, SubjectList, date
        paper_record_df = pd.DataFrame(columns=['PMID', 'Title', 'Abstract', 'Year', 'Month', 'author_list',
                                                'MeSH Terms', 'subject_list', 'date', 'author_ids'])
        # contains all the metadata of the medical information: PubMed unique Identifier number(PMID), Primary Medical
        # Subject Header (MESH) and the description ID
        medical_record_df = pd.DataFrame(columns=['PMID', 'Terms', 'Numbers'])

        author_list = list()
        title_list = list()
        abstract_list = list()

        uid = 1
        # get the relevant information for each record
        for record_index, record in enumerate(fetch_records):

            logging.getLogger('regular').debug('record index = {0}'.format(record_index))

            try:
                pmid = record.get('PMID')
                title = record.get('TI')
                abstract = record.get('AB')
                authors = record.get('FAU')
                affiliations = record.get('AD')
                publication_type = record.get('PT')
                mesh_terms = record.get('MH')#.split(';'
                other_terms = record.get('OT')
                if other_terms is not None:
                    other_terms = other_terms.split(';')
                date_created = record.get('EDAT')
                year, month = date_created.split('/')[:2]
                date = year + '/' + month

                logging.getLogger('regular').debug('pmid = {0}'.format(pmid))
                logging.getLogger('regular').debug('title = {0}'.format(title))
                logging.getLogger('regular').debug('abstract = {0}'.format(abstract))
                logging.getLogger('regular').debug('authors = {0}'.format(authors))
                logging.getLogger('regular').debug('affiliations = {0}'.format(affiliations))
                logging.getLogger('regular').debug('publication type = {0}'.format(publication_type))
                logging.getLogger('regular').debug('mesh term = {0}'.format(mesh_terms))
                logging.getLogger('regular').debug('other terms = {0}'.format(other_terms))
                logging.getLogger('regular').debug('data created = {0}'.format(date_created))

                # assign the chief author, ordinary author or principal investigator role to each author
                roles = assign_roles(authors)
                # check and assign whether the authors belong to the CHOP or PENN organization
                chop_organization, penn_organization = assign_organization(affiliations)

                # get mesh information from mesh terms and other terms
                all_terms = mesh_terms if mesh_terms is not None else []
                all_terms.extend(other_terms if other_terms is not None else [])

                mesh_terms, mesh_numbers = convert_mesh_description(mesh_records, all_terms)

                all_terms.extend(mesh_terms)
                all_terms.extend(get_mesh_from_text(mesh_records, abstract))

                all_terms = set(all_terms) # remove duplicates
                mesh_terms = ';'.join(mesh_terms)
                mesh_numbers = ';'.join(mesh_numbers)

                # mesh information
                row = pd.DataFrame([[pmid, mesh_terms, mesh_numbers]], columns=['PMID', 'Terms', 'Numbers'])
                medical_record_df = medical_record_df.append(row, ignore_index=True)

                # author information
                author_ids = []
                for author_index, organizations in enumerate(zip(chop_organization, penn_organization)):
                    # check if the author belongs to either CHOP or PENN
                    if 1 in organizations:
                        author = Author(authors[author_index], pmid, roles[author_index], organizations[1], organizations[0], affiliations[author_index], uid, mesh_terms.split(';'))
                        exists = False
                        for a in author_list:
                            if a.equals(author):
                                exists = True
                                a.combine(author)
                                author_ids.append(str(a.uid))
                                break
                        if not exists:
                            author_list.append(author)
                            author_ids.append(str(author.uid))
                            # increment the uid if this is a new author, otherwise reuse it
                            uid += 1

                authors = ';'.join(authors)
                author_ids = ';'.join(author_ids)

                # publication information
                row = pd.DataFrame([[pmid, title, abstract, year, month, authors, mesh_terms, ';'.join(all_terms), date, author_ids]],
                    columns=['PMID', 'Title', 'Abstract', 'Year', 'Month', 'author_list', 'MeSH Terms', 'subject_list',
                            'date', 'author_ids'])
                paper_record_df = paper_record_df.append(row)

                title_list.append(title)
                abstract_list.append(abstract)

            except Exception as e:
                msg = 'Error while processing PMID={0}'.format(pmid)
                # logging.getLogger('regular').debug(msg)
                logging.getLogger('regular').info(msg)
                msg = 'Exception message = {0}'.format(e)
                # logging.getLogger('regular').debug(msg)
                logging.getLogger('regular').info(msg)

        # authors to pd.dataFrame
        for author in author_list:
            mesh = []
            for term, count in author.mesh_terms.items():
                mesh.append('{0}:{1}'.format(term, count))
            mesh = ';'.join(mesh)
            row = pd.DataFrame([[author.pmids, author.name, author.chop, author.penn,
                                author.roles, author.affiliations, author.uid, mesh]],
                            columns=['PMID', 'Author', 'author_chop', 'author_penn', 'Role',
                                        'AffiliationInfo', 'UID', 'mesh_terms'])
            author_record_df = author_record_df.append(row, ignore_index=True)

        pandas.io.formats.excel.header_style = None
        # contains all the metadata elements on the author level: Pubmed unique Identifier number(PMID), AuthorID (as a
        # (CA) Ordinary Author (OA) or Principal Author (PA) and the author's affiliation
        author_record_df.to_excel('record_results/author_record.xlsx', sheet_name='author_record', index=False)
        author_record_df.to_csv('record_results/author_record.csv', index=False)
        # contains all the metadata elements on the paper level: Pubmed unique Identifier number(PMID), Title, Abstract,
        # Year, Month, AuthorList, SubjectList, date
        paper_record_df.to_excel('record_results/paper_record.xlsx', sheet_name='paper_record', index=False)
        paper_record_df.to_csv('record_results/paper_record.csv', index=False)
        # contains all the metadata of the medical information: Pubmed unique Identifier number(PMID), Primary Medical
        # Subject Header (MESH) and the description ID
        medical_record_df.to_excel('record_results/medical_record.xlsx', sheet_name='medical_record', index=False)
        medical_record_df.to_csv('record_results/medical_record.csv', index=False)


    if args.analyze:
        # analyze similarity of publications based on their subject list
        project_path = Path(os.getcwd())
        template_path = Path(project_path, 'template')
        data_path = Path(project_path, 'record_results')
        similarities_path = Path(data_path, 'similarities')

        publications = pd.read_csv(Path(data_path, 'paper_record.csv'))
        publications.head()

        # create a dict of enntry to pmid
        pmids = {}
        for idx, pmid in enumerate(publications.PMID):
            pmids[idx] = pmid

        # preprocessing: remove stop words, set to lower case, lemmatize
        subject_lists = []
        subject_lists_pmids = []

        stop_words = set(stopwords.words('english'))
        stop_words.add('')
        stop_words.add('nan')
        lemmatizer = WordNetLemmatizer()
        print('getting subjects')
        for idx, subject in enumerate(publications.subject_list):
            # we don't want to include publications with no subject info in our analysis
            if subject is None or str(subject) == '':
                continue
            text_tmp = str(subject).replace(';', ' ').translate(str.maketrans('', '', string.punctuation))
            tokens = [w.lower() for w in word_tokenize(text_tmp)]
            words = [w for w in tokens if not w in stop_words]
            if len(words) == 0:
                continue
            subject_lists_pmids.append(pmids[idx])
            subject_lists.append(words)


        abstract_list = []
        abstract_list_pmids = []
        stop_words = set(stopwords.words('english'))
        stop_words = stop_words.union(['abstract', 'aim', 'aims', 'background', 'context', 'hypothesis', 
                                       'introduction', 'importance', 'method', 'methods', 'motivation', 'motivations', 
                                       'objective', 'objectives', 'study', 'problem', 'purpose', 'results', 'review', 'nan'])
        for idx, abstract in enumerate(publications.Abstract):
            tokens = [w.lower() for w in word_tokenize(str(abstract))]
            table = str.maketrans('', '', string.punctuation)
            stripped = [w.translate(table) for w in tokens]
            words = [word for word in stripped if word.isalpha()]
            words = [w for w in words if not w in stop_words]
            # some 'abstracts' are not actually abstracts
            if len(tokens) < 20:
                continue
            doc = []
            # remove numbers from abstracts
            for w in words:
                try:
                    int(w)
                except:
                    doc.append(lemmatizer.lemmatize(w))
            if len(doc) > 0:
                abstract_list_pmids.append(pmids[idx])
                abstract_list.append(doc)

        # create a dictionary to match tokens to integers
        subject_dictionary = gensim.corpora.Dictionary(subject_lists)
        subject_dictionary.filter_extremes(no_above=0.85)
        abstract_dictionary = gensim.corpora.Dictionary(abstract_list)
        abstract_dictionary.filter_extremes(no_above=0.5)

        # lists the number of times each word occurs in the document
        # list of tuples
            # first = index of the word
            # second = number of time that appears in that document
        subject_corpus = [subject_dictionary.doc2bow(subject_list) for subject_list in subject_lists]
        abstract_corpus = [abstract_dictionary.doc2bow(abstract) for abstract in abstract_list]

        subject_tf_idf = gensim.models.TfidfModel(subject_corpus)
        abstract_tf_idf = gensim.models.TfidfModel(abstract_corpus)

        subject_index = gensim.similarities.Similarity(str(similarities_path),
                                            subject_tf_idf[subject_corpus], 
                                            num_features=len(subject_dictionary))

        # yield similarities of the indexed documents
        subject_similarities_df = pd.DataFrame()

        for doc_sim_ix, doc_sim in enumerate(subject_index):
            pmid = subject_lists_pmids[doc_sim_ix]

            sorted_sim = sorted(list(enumerate(doc_sim)), key=lambda x:x[1], reverse=True)

            sims_with_pmids = []
            for idx, sim in sorted_sim[:100]:
                sim_pmid = subject_lists_pmids[idx]
                sims_with_pmids.append('{0},{1}'.format(sim_pmid, sim))

            sims_with_pmids = ";".join(sims_with_pmids)
            data = [pmid]
            data.append(sims_with_pmids)

            row = pd.DataFrame([data])
            subject_similarities_df = subject_similarities_df.append(row, ignore_index=True)

        subject_similarities_df.to_csv(Path(similarities_path, 'document_subject_similarities.csv'),index=False)


        abstract_index = gensim.similarities.Similarity(str(similarities_path),
                                        abstract_tf_idf[abstract_corpus],
                                        num_features=len(abstract_dictionary))
        abstract_similarities_df = pd.DataFrame()

        for doc_sim_ix, doc_sim in enumerate(abstract_index):
            pmid = abstract_list_pmids[doc_sim_ix]

            sorted_sim = sorted(list(enumerate(doc_sim)), key=lambda x:x[1], reverse=True)

            sims_with_pmids = []
            for idx, sim in sorted_sim[:100]:
                sim_pmid = abstract_list_pmids[idx]
                sims_with_pmids.append('{0},{1}'.format(sim_pmid, sim))

            sims_with_pmids = ";".join(sims_with_pmids)
            data = [pmid]
            data.append(sims_with_pmids)

            row = pd.DataFrame([data])
            abstract_similarities_df = abstract_similarities_df.append(row, ignore_index=True)

        abstract_similarities_df.to_csv(Path(similarities_path, 'document_abstract_similarities.csv'),index=False)

    logging.getLogger('line.regular.time.line').info('SCOSY finished running successfully.')


    # measure the similarities between the two similarity measurements
    abstract_similarities = {}
    with open('record_results/similarities/document_abstract_similarities.csv') as similarities_csv:
        csv_reader = csv.reader(similarities_csv, delimiter=',')
        for row in csv_reader:
            try:
                sims = {}
                for entry in row[1].split(';'):
                    sims[entry.split(',')[0]] = entry.split(',')[1]
                abstract_similarities[row[0]] = sims
            except Exception as ex:
                print('abstract sims: {0}'.format(ex))
                continue
    subject_similarities = {}
    with open('record_results/similarities/document_subject_similarities.csv') as similarities_csv:
        csv_reader = csv.reader(similarities_csv, delimiter=',')
        for row in csv_reader:
            try:
                sims = {}
                for entry in row[1].split(';'):
                    sims[entry.split(',')[0]] = entry.split(',')[1]
                subject_similarities[row[0]] = sims
            except Exception as ex:
                print('subject sims: {0}'.format(ex))
                continue

    overlap = 0
    total = 0
    for pmid, subject_sims in subject_similarities.items():
        if pmid in abstract_similarities:
            abstract_sims = abstract_similarities[pmid]
            total += 1
            for key in list(subject_sims.keys())[1:11]:
                if key in list(abstract_sims.keys())[1:11]:
                    overlap += 1
                    break
        print('{0}/{1} = {2}'.format(overlap, total, overlap/total))


if __name__ == '__main__':
    main()
