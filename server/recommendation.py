from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import csv
import os
import utils.records as records
import operator

class Collaborator:
    def __init__(self, author, weight):
        self.author = author
        self.weight = weight

    def to_dict(self):
        d = {}
        d['author'] = self.author.to_dict()
        d['weight'] = self.weight
        return d

'''given an author, returns a list of authors who are recommended to collaborate along with a collaboration
   rating [0, 1]. Does not include previous collaborators. If you need this, use Author.get_collaborators()'''
def recommend_collaborators(author, author_records, publication_records):
    # recommendation weight based off of past collaboration network
    authors = author_records
    existing_collaborators = author.collaborators()

    collaborators = records.collaborators([authors[uid] for uid in existing_collaborators])
    total_weight = {}
    for weight in [1.0, 0.5, 0.25]:        
        new_collaborators = set()
        for uid in collaborators:
            if uid not in total_weight and uid not in existing_collaborators:
                collaborator = authors[uid]
                total_weight[uid] = Collaborator(collaborator, weight * 0.25)
                new_collaborators.add(collaborator)
        collaborators = records.collaborators(new_collaborators)

    # recommendation weight based off of publication similarity
    publications = publication_records
    similarities_record = records.get_similarities_records()
    publication_weight = {} # uid -> collaborator
    for auth_pmids in author.pmids:
        if auth_pmids in similarities_record:
            similarities = similarities_record[auth_pmids]
            for pmid, sim in similarities[:10]:
                if pmid in publications:
                    publication = publications[pmid]
                    for uid in publication.author_ids:
                        if uid in existing_collaborators or uid not in authors:
                            continue
                        if uid not in publication_weight:
                            publication_weight[uid] = Collaborator(authors[uid], float(sim))
                        else:
                            publication_weight[uid].weight = max(float(sim), publication_weight[uid].weight)

    
    # # combine the two recommendations
    for uid in publication_weight:
        publication_weight[uid].weight *= 0.75
        if uid in total_weight:
            total_weight[uid].weight = total_weight[uid].weight + publication_weight[uid].weight
        else:
            total_weight[uid] = publication_weight[uid]

    recommendations = [collab.to_dict() for collab in total_weight.values()][:20]

    return sorted(recommendations, key=lambda x: x['weight'], reverse=True)


