"""
Parses PDF files containing the articles. 
First step.
"""

import os
import pathlib
import json
import scipdf
from tqdm import tqdm

from src.dataset.util import IDGenerator


def get_file_paths(folder_path: str) -> tuple[list, list]:
    """
    """

    pdf_paths = []
    other_paths = []
    for root, directories, files in os.walk(folder_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filename.endswith('.pdf'):
                pdf_paths.append(filepath)
            else:
                other_paths.append(filepath)

    return pdf_paths, other_paths


def is_empty(parsed_article: dict) -> bool:
    return all(value in ("", []) for value in parsed_article.values())


if __name__ == "__main__":

    ROOTPATH = pathlib.Path("data/raw/")
    OUTPATH = pathlib.Path("data/interim/")
    pdf_paths, other_paths = get_file_paths(ROOTPATH)
    empty_paths = []
    id_generator = IDGenerator()

    # keep track of unparsed paths
    with open(OUTPATH.joinpath('non_pdf_paths.txt'), 'w') as file:
        for path in other_paths:
            file.write(path + "\n")

    with open(OUTPATH.joinpath('publications.ndjson'), "w") as file:
        for path in tqdm(pdf_paths):
            try:
                parsed = scipdf.parse_pdf_to_dict(path)
                empty = is_empty(parsed)
            except AttributeError:
                parsed = None
                empty = True                

            # files where something was extracted
            if parsed and not empty:
                parsed['path'] = path
                parsed['id'] = "p" + str(id_generator.generate_id())
                # Use the json.dumps method to serialize the dictionary to a JSON string
                json_string = json.dumps(parsed)
                # Write the JSON string with a newline character to separate objects
                file.write(json_string + "\n")

            # empty files
            else:
                empty_paths.append(path)

        with open(OUTPATH.joinpath('failed_pdf_paths.txt'), 'w') as f:
            for path in empty_paths:
                f.write(path + "\n")
