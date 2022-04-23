import argparse
import json
import os
from txtai.pipeline import Similarity
from txtai.embeddings import Embeddings
from datetime import datetime
import logging
import numpy as np
from dataclasses import dataclass
from urllib.parse import urlparse


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


@dataclass
class Seller:
    """
    A data class to hold all the data corresponding to a seller
    """
    mongo_id: str
    website: str
    pages: list
    records: list

    def find_record_with_best_match(self, similarity, query):
        results = similarity(query, [record["text"] for record in self.records])
        similarity_scores = [score for _, score in results]
        best_match = np.argmax(similarity_scores)
        return self.records[best_match]

    def __hash__(self):
        return hash(self.mongo_id)

    def __eq__(self, other):
        return self.mongo_id == other.mongo_id


def load_data(folder):
    """
    Loads data from the specified folder and returns a list of dictionaries
    :param folder:
    :return:
    """
    path = f"../{folder}"
    sellers = []
    counter = 0
    for filename in os.listdir(path):
        if counter > 0:
            break
        counter += 1
        records = []
        with open(f"{path}/{filename}", "r") as f:
            dataset = json.load(f)
            records.extend(dataset)

        pages = [element["subPage"] for element in records]

        sellers.append(
            # assumption here is that the data is not erroneous, i.e. that there is a single website and mongo ID
            Seller(records[0]["mongoID"], records[0]["website"], pages , records)
        )
    return sellers


def create_parser():
    """
    Creates the parser required to parse CLI arguments
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("request_name", type=str, help="The request name")
    parser.add_argument("request_description", type=str, help="The request description")
    parser.add_argument("path_to_folder", type=str, help="The folder from root that contains all the data")
    return parser


def find_top_n_sellers_with_highest_similarity_scores(query, sellers, n=5):
    """
    Finds the top n sellers with the highest similarity scores.
    The similarity score is defined as the mean score per website across all its pages.
    """
    logging.info("Loading similarity model")
    similarity = Similarity()
    logging.info("Finished loading similarity model")
    best_matches = [(seller.find_record_with_best_match(similarity, query), seller) for seller in sellers]
    best_matches.sort(key=lambda element: element[0])
    return best_matches[:n]


if __name__ == "__main__":
    # get query
    parser = create_parser()
    args = parser.parse_args()

    # load data
    sellers = load_data(args.path_to_folder)

    # find top n matches
    top_matches = find_top_n_sellers_with_highest_similarity_scores(args.request_description, sellers, n=5)

    print("-------TOP MATCHES--------------")
    for score, seller in top_matches:
        print(score, seller)
    print("--------------------------------")
