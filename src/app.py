import argparse
import json
import logging
import os

from models import Seller, Matcher

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def load_data(folder: str) -> list[Seller]:
    """
    Loads data from the specified folder and returns a list of `Seller`s
    :param folder:
    :return:
    """
    path = f"../{folder}"
    sellers = []
    for filename in os.listdir(path):
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


def create_parser() -> argparse.ArgumentParser:
    """
    Creates the parser required to parse CLI arguments
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("request_name", type=str, help="The request name")
    parser.add_argument("request_description", type=str, help="The request description")
    parser.add_argument("path_to_folder", type=str, help="The folder from root that contains all the data")
    return parser


if __name__ == "__main__":
    # get query
    parser = create_parser()
    args = parser.parse_args()

    # load data
    sellers = load_data(args.path_to_folder)

    # find top n matches
    matcher = Matcher()
    top_matches = matcher.find_top_n_sellers_with_highest_similarity_scores(args.request_description, sellers, n=5)

    print("-------TOP MATCHES--------------")
    for score, record, seller in top_matches:
        print(score, seller.website, record)
    print("--------------------------------")
