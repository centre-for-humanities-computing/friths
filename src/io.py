"""
"""

import os
import json
import scipdf
from tqdm import tqdm


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


if __name__ == "__main__":

    ROOTPATH = "data/raw/UTA publications/"
    OUTPATH = "data/parsed/publications.json"
    pdf_paths, other_paths = get_file_paths(ROOTPATH)

    # keep track of unparsed paths
    with open('data/parsed/unparsed_paths.txt', 'w') as file:
        for path in other_paths:
            file.write(path + "\n")

    with open(OUTPATH, "w") as file:
        for path in tqdm(pdf_paths):
            parsed = scipdf.parse_pdf_to_dict(path)
            parsed['path'] = path
            # Use the json.dumps method to serialize the dictionary to a JSON string
            json_string = json.dumps(parsed)
            # Write the JSON string with a newline character to separate objects
            file.write(json_string + "\n")
