"""
"""

import os
import json


def load_iterim_publications(interim_path='../data/interim/') -> list[dict]:
    """
    loads a newline json with extracted info from pdfs
    """
    path = os.path.join(interim_path, 'publications.ndjson')
    pub = []
    with open(path) as fin:
        for line in fin:
            json_obj = json.loads(line)
            pub.append(json_obj)

    return pub


def load_publication_paths(interim_path='../data/interim/') -> tuple[list, list, list]:
    """
    loads three sets of paths
    """

    # successfully extracted paths
    pub = load_iterim_publications(interim_path=interim_path)
    parsed_paths = [art['path'] for art in pub]

    # failed paths
    with open(os.path.join(interim_path, 'failed_pdf_paths.txt')) as fin:
        failed_paths = [line.strip() for line in fin]

    # not a pdfs
    with open(os.path.join(interim_path, 'non_pdf_paths.txt')) as fin:
        non_pdf_paths = [line.strip() for line in fin]

    return parsed_paths, failed_paths, non_pdf_paths


class IDGenerator:
    def __init__(self):
        self.counter = 0

    def generate_id(self):
        self.counter += 1
        return self.counter
