# this import is needed as per https://stackoverflow.com/a/33533514/5682512
# as otherwise you can't do a type hint for the enclossing class
from __future__ import annotations
from dataclasses import dataclass
from txtai.pipeline import Similarity
import numpy as np


@dataclass
class Seller:
    """
    A data class to hold all the data corresponding to a seller
    """
    mongo_id: str
    website: str
    pages: list
    records: list

    def find_record_with_best_match(self, similarity: Similarity, query: str) -> (float, dict, Seller):
        """
        Finds the record with the highest similarity score
        :param similarity:
        :param query:
        :return: A tuple of float, dict, Seller
        """
        results = similarity(query, [record["text"] for record in self.records])
        similarity_scores = [score for _, score in results]
        index_of_best_match = np.argmax(similarity_scores)
        best_score = similarity_scores[index_of_best_match]
        return best_score, self.records[index_of_best_match], self

    def __hash__(self):
        return hash(self.mongo_id)

    def __eq__(self, other):
        return self.mongo_id == other.mongo_id


class Matcher:
    def __init__(self, similarity: Similarity = None):
        if similarity is None:
            self.similarity = Similarity()

    def find_top_n_sellers_with_highest_similarity_scores(self, query: str, sellers: list[Seller], n: int = 5) -> \
            list[(float, dict, Seller)]:
        """
        Finds the top n sellers with the highest similarity scores.
        The similarity score is defined as the mean score per website across all its pages.
        """
        best_matches = [
            seller.find_record_with_best_match(self.similarity, query) for seller in sellers
        ]
        best_matches.sort(key=lambda element: element[0], reverse=True)
        return best_matches[:n]
