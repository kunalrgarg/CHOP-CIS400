import unittest
import utils.records as records
import recommendation
import os
import copy

class TestStringMethods(unittest.TestCase):

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

    def test_delete_both_authors(self):
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
        print("onePublish percent")
        #print(percentOfOnePub())
        #for publication in publications:
        #    if someAuthor.id in publication.author_ids or collab.id in publication.author_ids:
        #        del someAuthor.pmids[someAuthor.pmids.find(publication.id)]
        #        del collab.pmids[highestRecAuthor.pmids.find(publication.id)]
        #        del publication



    def test_delete_first_authors(self):
        
        publications = records.get_publication_records()
        
        skippedTests = 0
        totalTests = 0
        authors = records.get_author_records()
        testAuthor = None

        for author in authors.values():
            if len(author.pmids) >= 5:
                testAuthor = author
                break
        else:
            print('couldnt find a good author')
            return


        if len(author.pmids) <= 1:
            skippedTests += 1
            totalTests += 1
            #continue

        possibleCollabs = author.collaborators()
        print("number of collabs")
        print(len(possibleCollabs))
        
        if not possibleCollabs:
            print("collab doesnt exist")
        
        modifiedAuthor = copy.deepcopy(author)
        modifiedAuthors = copy.deepcopy(authors)
        modifiedPubs = copy.deepcopy(publications)
        modifiedPmids = copy.deepcopy(author.pmids)

        for collab in possibleCollabs:
            print("testing a collab")
            for pmid in modifiedPmids:
                if authors[collab].id in modifiedPubs[pmid].author_ids:
                    modifiedPubs[pmid].author_ids.remove(author.id)
                    modifiedAuthor.pmids.remove(pmid)
                    modifiedAuthors[author.id].pmids.remove(pmid)
            if len(modifiedAuthor.pmids) == 0:
                skippedTests += 1
                totalTests += 1
                continue

            totalTests += 1
            recs = recommendation.recommend_collaborators(modifiedAuthor, modifiedAuthors, modifiedPubs)
            for rec in recs:
                if rec["author"]['id'] == authors[collab].id:
                    print("pass")
                    break
            else:
                print("fail")
            #recs.sort(key= lambda x: x["weight"])
            modifiedAuthor = copy.deepcopy(author)
            modifiedAuthors = copy.deepcopy(authors)
            modifiedPubs = copy.deepcopy(publications)
            modifiedPmids = copy.deepcopy(author.pmids)

                

        print("total tests")
        print(totalTests)
        print("skippedTests")
        print(skippedTests)
        #print("onePublish percent")
        #print(percentOfOnePub())
        #for publication in publications:
        #    if someAuthor.id in publication.author_ids or collab.id in publication.author_ids:
        #        del someAuthor.pmids[someAuthor.pmids.find(publication.id)]
        #        del collab.pmids[highestRecAuthor.pmids.find(publication.id)]
        #        del publication

    def test_delete_collab_authors(self):
        
        publications = records.get_publication_records()
        
        skippedTests = 0
        totalTests = 0
        authors = records.get_author_records()
        testAuthor = None

        for author in authors.values():
            if len(author.pmids) >= 5:
                testAuthor = author
                break
        else:
            print('couldnt find a good author')
            return

        possibleCollabs = author.collaborators()
        print("number of collabs")
        print(len(possibleCollabs))
        
        if not possibleCollabs:
            print("collab doesnt exist")
        
       
        modifiedAuthors = copy.deepcopy(authors)
        modifiedPubs = copy.deepcopy(publications)
        modifiedPmids = copy.deepcopy(author.pmids)
        
        for collab in possibleCollabs:
            print("testing a collab")
            for pmid in modifiedPmids:
                if authors[collab].id in modifiedPubs[pmid].author_ids:
                    if len(authors[collab].pmids) > 1:  
                        modifiedPubs[pmid].author_ids.remove(authors[collab].id)
                        modifiedAuthors[collab].pmids.remove(pmid)
                    else:
                        skippedTests += 1
                        totalTests += 1

            totalTests += 1
            recs = recommendation.recommend_collaborators(author, modifiedAuthors, modifiedPubs)
            for rec in recs:
                if rec["author"]['id'] == authors[collab].id:
                    print("pass")
                    break
            else:
                print("fail")
            #recs.sort(key= lambda x: x["weight"])
            modifiedAuthor = copy.deepcopy(author)
            modifiedAuthors = copy.deepcopy(authors)
            modifiedPubs = copy.deepcopy(publications)
            modifiedPmids = copy.deepcopy(author.pmids)

                

        print("total tests")
        print(totalTests)
        print("skippedTests")
        print(skippedTests)
        #print("onePublish percent")
        #print(percentOfOnePub())
        #for publication in publications:
        #    if someAuthor.id in publication.author_ids or collab.id in publication.author_ids:
        #        del someAuthor.pmids[someAuthor.pmids.find(publication.id)]
        #        del collab.pmids[highestRecAuthor.pmids.find(publication.id)]
        #        del publication



    


if __name__ == '__main__':
    unittest.main()