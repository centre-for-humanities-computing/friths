"""
"""

import os
import json


def read_jsonl(path: str) -> list[dict]:
    """
    """
    with open(path, "r") as jsonl_file:
        object = [json.loads(line.strip()) for line in jsonl_file]
    return object


def write_jsonl(object: list[dict], path: str) -> None:
    """
    """
    with open(path, "w") as jsonl_file:
        for data_dict in object:
            # Write each dictionary as a separate line in the jsonl file
            jsonl_file.write(json.dumps(data_dict) + "\n")


def load_publication_paths(interim_path='../data/interim/') -> tuple[list, list, list]:
    """
    loads three sets of paths
    """

    # successfully extracted paths
    pub = read_jsonl(os.path.join(interim_path, 'publications_parsed.ndjson'))
    parsed_paths = [art['path'] for art in pub]

    # failed paths
    with open(os.path.join(interim_path, 'failed_pdf_paths.txt')) as fin:
        failed_paths = [line.strip() for line in fin]

    # not a pdfs
    with open(os.path.join(interim_path, 'non_pdf_paths.txt')) as fin:
        non_pdf_paths = [line.strip() for line in fin]

    return parsed_paths, failed_paths, non_pdf_paths


class IDGenerator:
    def __init__(self, starting_position: int = 0):
        self.counter = starting_position

    def generate_id(self):
        self.counter += 1
        return self.counter
