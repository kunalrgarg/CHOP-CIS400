import unittest
import utils.records as records
import recommendation
import os

class TestStringMethods(unittest.TestCase):

    def test_records(self):
        print("stuff")
        print(os.path.dirname(os.path.realpath(__file__)))
        authors = records.get_author_records()
        someAuthor = next(iter(authors.values()))
        recs, tmp = recommendation.recommend_collaborators(someAuthor)
        recs.sort(key= lambda x: x["weight"])
        for rec in recs:

            print(rec["author"]['name'])
            print(rec["author"]['id'])
            print(rec["weight"])
        #self.assertEqual('foo'.upper(), 'FOO')

    
if __name__ == '__main__':
    unittest.main()