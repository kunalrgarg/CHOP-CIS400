from Bio import Entrez
import csv
import logging
from utils.logger import logger_initialization
from utils.parse import parse
import argparse
import pandas as pd
import pandas.io.formats.excel
import utils.records as records

class Author:
    def __init__(self, name, pmid, role, penn, chop, affiliations, uid):
        self.name = name
        self.pmids = [pmid]
        self.roles = [role]
        self.penn = penn
        self.chop = chop
        self.uid = uid
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
        numbers = mesh_records.get_numbers(term)
        if len(numbers) > 0:
            matching_terms.append(mesh_records.get_term(numbers[0])) # get the correctly capitalized term
            matching_numbers.extend(numbers)
            
    return matching_terms, matching_numbers


def print_str(*args):
    n_string = ''
    for element in args:
        n_string += '"{0}",'.format(element)
    n_string = n_string[:-1]
    n_string += '\n'
    return n_string


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
        mesh_records = records.get_mesh_records()

        # contains all the metadata elements on the author level: PubMed unique Identifier number(PMID), AuthorID (as a
        # (CA) Ordinary Author (OA) or Principal Author (PA) and the author's affiliation
        author_record_df = pd.DataFrame(columns=['PMID', 'Author', 'author_chop', 'author_penn', 'Role',
                                                 'AffiliationInfo', 'UID'])
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
                        author = Author(authors[author_index], pmid, roles[author_index], organizations[1], organizations[0], affiliations[author_index], uid)
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
            row = pd.DataFrame([[author.pmids, author.name, author.chop, author.penn,
                                author.roles, author.affiliations, author.uid]],
                            columns=['PMID', 'Author', 'author_chop', 'author_penn', 'Role',
                                        'AffiliationInfo', 'UID'])
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

        # store the record in a file for processing
        dataset = dict()
        dataset['title'] = title_list
        dataset['abstracts'] = abstract_list
        dataset = pd.DataFrame(dataset)
        dataset.to_csv(path_or_buf='record_results/titles_abstracts.csv', index=False)

    logging.getLogger('line.regular.time.line').info('SCOSY finished running successfully.')


if __name__ == '__main__':
    main()
