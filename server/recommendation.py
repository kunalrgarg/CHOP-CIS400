from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import csv
import os
import utils.records as records
import operator

class Collaborator:
    def __init__(self, author):
        self.author = author
        self.collab_weight = 0
        self.abstract_weight = 0
        self.subject_weight = 0

    def to_dict(self):
        d = {}
        d['author'] = self.author.to_dict()
        d['weight'] = self.collab_weight + self.abstract_weight + self.subject_weight
        return d

'''given an author, returns a list of authors who are recommended to collaborate along with a collaboration
   rating [0, 1]. Does not include previous collaborators. If you need this, use Author.get_collaborators()'''
def recommend_collaborators(author, author_records, publication_records, abstract_similarities, subject_similarities,
                            collab_weight = 0.3333, abstract_weight = 0.3333, subject_weight = 0.3333):
    # recommendation weight based off of past collaboration network
    authors = author_records
    existing_collaborators = author.collaborators()
    recommendations = {}

    collaborators = records.collaborators([authors[uid] for uid in existing_collaborators])
    for weight in [1.0, 0.5]:
        new_collaborators = set()
        for uid in collaborators:
            if uid not in recommendations and uid not in existing_collaborators:
                collaborator = authors[uid]
                recommendations[uid] = Collaborator(collaborator)
                recommendations[uid].collab_weight = weight * collab_weight
                new_collaborators.add(collaborator)
        collaborators = records.collaborators(new_collaborators)

    # recommendation weight based off of abstract similarity
    publications = publication_records
    for auth_pmid in author.pmids:
        if auth_pmid in abstract_similarities:
            similarities = abstract_similarities[auth_pmid]
            for pmid, sim in similarities[1:11]:
                if pmid in publications:
                    publication = publications[pmid]
                    for uid in publication.author_ids:
                        if uid in existing_collaborators or uid not in authors:
                            continue
                        if uid not in recommendations:
                            recommendations[uid] = Collaborator(authors[uid])
                            recommendations[uid].abstract_weight = float(sim) * abstract_weight
                        else:
                            recommendations[uid].abstract_weight = max(float(sim), recommendations[uid].abstract_weight)
        if auth_pmid in subject_similarities:
            similarities = subject_similarities[auth_pmid]
            for pmid, sim in similarities[1:11]:
                if pmid in publications:
                    publication = publications[pmid]
                    for uid in publication.author_ids:
                        if uid in existing_collaborators or uid not in authors:
                            continue
                        if uid not in recommendations:
                            recommendations[uid] = Collaborator(authors[uid])
                            recommendations[uid].abstract_weight = float(sim) * abstract_weight
                        else:
                            recommendations[uid].abstract_weight = max(float(sim), recommendations[uid].abstract_weight)

    recommended_collaborators = [collab.to_dict() for collab in recommendations.values()]
    return sorted(recommended_collaborators, key=lambda x: x['weight'], reverse=True)[:20]


