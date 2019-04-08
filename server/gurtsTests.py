import unittest
import utils.records as records
import recommendation
import threading
import os
import copy
from random import shuffle

#def test_records(self):
#    print("stuff")
#    print(os.path.dirname(os.path.realpath(__file__)))
#    authors = records.get_author_records()
#    publications = records.get_publication_records()
#    someAuthor = next(iter(authors.values()))
#    recs = recommendation.recommend_collaborators(someAuthor, authors, publications)
#    recs.sort(key= lambda x: x["weight"])
#    for rec in recs:
#
#    #        print(rec["author"]['name'])
#    #        print(rec["author"]['id'])
#        print(rec["weight"])
    #self.assertEqual('foo'.upper(), 'FOO')

# def test_delete_both_authors(self):
    #authors = records.get_author_records()
    #publications = records.get_publication_records()
    #someAuthor = authors["16148"]
    #possibleCollabs = iter(someAuthor.collaborators())
    #collab = authors[next(possibleCollabs)]
    #
    #if not collab:
    #    print("collab doesnt exist")
    #
    #print("collabs name is " + collab.name)
    #print(collab.id)
    #
    #pmids = someAuthor.pmids
#
#        #toRemove = []
#        #print("someAuthors pmids")
#
#        #for pmid in pmids:
#        #    if collab.id in publications[pmid].author_ids:
#
#        #        if len(collab.pmids) == 1:
#        #            someAuthor.pmids.remove(pmid)
#        #            publications[pmid].author_ids.remove(someAuthor.id)
#        #        else:
#        #            collab.pmids.remove(pmid)
#        #            try:
#        #                someAuthor.pmids.remove(pmid)
#        #            except ValueError:
#        #                print('could not remove {0} from {1}'.format(pmid, someAuthor.pmids))
#        #            del publications[pmid]
#
#        #recs = recommendation.recommend_collaborators(someAuthor, authors, publications)
#        ##recs.sort(key= lambda x: x["weight"])
#        #for rec in recs:
#        #    print(rec["author"]['name'])
#        #    print(rec["author"]['id'])
#        #    print(rec["weight"])
#        #
#        #def percentOfOnePub():
#        #    authors = records.get_author_records()
#        #    total = len(authors)
#        #    onePublish = 0
#        #    if len(authors) == 0:
#        #        return 0
#        #    for author in authors.values():
#        #        if len(author.pmids) == 1:
#        #            onePublish += 1
#
#        #    return onePublish / total
#
#
    # print("onePublish percent")
    #print(percentOfOnePub())
    #for publication in publications:
    #    if someAuthor.id in publication.author_ids or collab.id in publication.author_ids:
    #        del someAuthor.pmids[someAuthor.pmids.find(publication.id)]
    #        del collab.pmids[highestRecAuthor.pmids.find(publication.id)]
    #        del publication


def test_delete_first_authors():
    record_filepath = 'record_results'
    publications = records.get_publication_records(record_filepath)
    abstract_similarities, subject_similarities = records.get_similarities_records('record_results/similarities')
    
    passedTests = [0, 0]
    totalTests = [0, 0]
    case1_results = []
    case2_results = []
    authors = records.get_author_records(record_filepath)
    testAuthor = None
    all_authors = list(authors.values())
    shuffle(all_authors)
    for author in all_authors:
        if 20 >= len(author.pmids) >= 2:
            testAuthor = author
        else:
            continue

        possibleCollabs = author.collaborators(publications)
        print("number of collabs")
        print(len(possibleCollabs))
        
        if not possibleCollabs:
            print("collab doesnt exist")
    
        modifiedAuthor = copy.deepcopy(author)
        for collab in possibleCollabs:
            modifiedAuthors = copy.deepcopy(authors)
            modifiedPubs = copy.deepcopy(publications)
            modifiedPmids = copy.deepcopy(author.pmids)
            modifiedAuthor.pmids = modifiedPmids
            try:
                for pmid in modifiedPmids:
                    if authors[collab].id in modifiedPubs[pmid].author_ids:
                        # remove the target author from the publication
                        modifiedPubs[pmid].author_ids.remove(author.id)
                        # remove the publication from the target author
                        modifiedAuthor.pmids.remove(pmid)
                        modifiedAuthors[author.id].pmids.remove(pmid)
                if len(modifiedAuthor.pmids) == 0:
                    continue
                totalTests[0] += 1
                recs = recommendation.recommend_collaborators(modifiedAuthor, modifiedAuthors, modifiedPubs, abstract_similarities, subject_similarities)
                for rec in recs:
                    if rec["author"]['id'] == authors[collab].id:
                        passedTests[0] += 1
                        break
                
                #recs.sort(key= lambda x: x["weight"])
            except Exception as ex:
                print('Exception: {0}'.format(ex))
                continue
        
        for collab in possibleCollabs:
            modifiedAuthors = copy.deepcopy(authors)
            modifiedPubs = copy.deepcopy(publications)

            try:
                for pmid in author.pmids:
                    if authors[collab].id in modifiedPubs[pmid].author_ids:
                        # remove the collaborator from the publication
                        modifiedPubs[pmid].author_ids.remove(authors[collab].id)
                        # remove the publication from the collaborator
                        modifiedAuthors[collab].pmids.remove(pmid)
                if len(authors[collab].pmids) == 0:
                    continue
                totalTests[1] += 1
                recs = recommendation.recommend_collaborators(author, modifiedAuthors, modifiedPubs, abstract_similarities, subject_similarities)
                for rec in recs:
                    if rec["author"]['id'] == authors[collab].id:
                        passedTests[1] += 1
                        break
                
                #recs.sort(key= lambda x: x["weight"])
            except Exception as ex:
                print('Exception: {0}'.format(ex))
                continue
        
        for i in range(0, 2):
            print('Case {0}: {1}/{2} = {3}'.format(i, passedTests[i], totalTests[i], passedTests[i]/totalTests[i]))

    #print("onePublish percent")
    #print(percentOfOnePub())
    #for publication in publications:
    #    if someAuthor.id in publication.author_ids or collab.id in publication.author_ids:
    #        del someAuthor.pmids[someAuthor.pmids.find(publication.id)]
    #        del collab.pmids[highestRecAuthor.pmids.find(publication.id)]
    #        del publication

# def test_delete_collab_authors(self):
#     record_filepath = 'record_results'
#     publications = records.get_publication_records(record_filepath)
#     abstract_similarities, subject_similarities = records.get_similarities_records('record_results/similarities')
    
#     passedTests = 0
#     totalTests = 0
#     authors = records.get_author_records(record_filepath)
#     testAuthor = None

#     all_authors = list(authors.values())
#     shuffle(all_authors)
#     for author in all_authors:
#         if 20 >= len(author.pmids) >= 3:
#             testAuthor = author
#         else:
#             continue

#         possibleCollabs = author.collaborators(publications)
#         print("number of collabs")
#         print(len(possibleCollabs))
        
#         if not possibleCollabs:
#             print("collab doesnt exist")
        
        
#         for collab in possibleCollabs:
#             modifiedAuthors = copy.deepcopy(authors)
#             modifiedPubs = copy.deepcopy(publications)
#             modifiedPmids = copy.deepcopy(author.pmids)

#             print("testing a collab")
#             for pmid in modifiedPmids:
#                 if authors[collab].id in modifiedPubs[pmid].author_ids:
#                     if len(authors[collab].pmids) >= 2:  
#                         modifiedPubs[pmid].author_ids.remove(authors[collab].id)
#                         modifiedAuthors[collab].pmids.remove(pmid)

#             totalTests += 1
#             recs = recommendation.recommend_collaborators(author, modifiedAuthors, modifiedPubs, abstract_similarities, subject_similarities)
#             for rec in recs:
#                 if rec["author"]['id'] == authors[collab].id:
#                     passedTests += 1
#                     break
#             #recs.sort(key= lambda x: x["weight"])
#             modifiedAuthor = copy.deepcopy(author)
#             modifiedAuthors = copy.deepcopy(authors)
#             modifiedPubs = copy.deepcopy(publications)
#             modifiedPmids = copy.deepcopy(author.pmids)

                

#         print("total tests")
#         print(totalTests)
#     #print("onePublish percent")
#     #print(percentOfOnePub())
#     #for publication in publications:
#     #    if someAuthor.id in publication.author_ids or collab.id in publication.author_ids:
#     #        del someAuthor.pmids[someAuthor.pmids.find(publication.id)]
#     #        del collab.pmids[highestRecAuthor.pmids.find(publication.id)]
#     #        del publication



    


if __name__ == '__main__':
    test_delete_first_authors()