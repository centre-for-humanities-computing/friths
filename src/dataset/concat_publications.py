"""
Extracts individual sections to model, assigns IDs and saves them to a file.

TODO
- merge good and bad files!

"""

import os
import pandas as pd
import numpy as np

from src.dataset.util import IDGenerator, read_jsonl, write_jsonl


# def schema_publications(parsed_publications: list[dict]) -> pd.DataFrame:
#     """
#     UNUSED

#     Extracts each section of a publication as a row, assigning IDs.
#     IDs are in format p<publication_id>_<section_id>. 
#     In case of abstract, the section_id is 'a'. Other sections are numbered.
#     """
#     docs = []

#     for article in parsed_publications:
#         # initialize a new id gen for each article
#         id_gen = IDGenerator()
#         # process abstract
#         docs.append({
#             'id': str(article['id']) + '_a',
#             'text': article['abstract'],
#             'heading': np.nan,
#             'n_publication_ref': np.nan,
#             'n_figure_ref': np.nan
#         })
#         # process body
#         for section in article['sections']:
#             docs.append({
#                 'id': str(article['id']) + '_' + str(id_gen.generate_id()),
#                 'text': section['heading'] + " " + section['text'],
#                 'heading': section['heading'].lower(),
#                 'n_publication_ref': section['n_publication_ref'],
#                 'n_figure_ref': section['n_figure_ref']
#             })

#         df = pd.DataFrame(docs).replace('', np.nan)
#         return df


def concat_text(article: dict) -> str:
    concat_sections = []

    for section in article["sections"]:
        temp_text = "\n".join((section["heading"], section["text"]))

        concat_sections.append(temp_text)

    text = "\n".join(concat_sections)

    return text


def concatenate_publications(parsed_publications: list[dict], verbose: bool = False) -> list[dict]:

    abstracts = []
    no_abstracts = []
    full_data = []

    for line in parsed_publications:
        temp_a = {
            "id": f"{line['id']}_a",
            "pub_date": line["pub_date"],
            "text": line["abstract"],
        }
        full_data.append(temp_a)
        temp_b = {
            "id": f"{line['id']}_b",
            "pub_date": line["pub_date"],
            "text": concat_text(line),
        }
        full_data.append(temp_b)

        if line["abstract"] != "":
            abstracts.append(line["id"])

        else:
            no_abstracts.append(line["id"])

    if verbose:
        print(f"Number of files with an abstract: {len(abstracts)}")
        print(f"Number of files without an abstract: {len(no_abstracts)}")
        print(f"Total number of files: {len(full_data) / 2}")

    return full_data


if __name__ == '__main__':

    INTERIM_PATH = 'data/interim/'

    # good files
    publications_parsed = read_jsonl(os.path.join(INTERIM_PATH, 'publications_parsed.ndjson'))
    publications_parsed_concat = concatenate_publications(publications_parsed)
    write_jsonl(publications_parsed_concat, os.path.join(INTERIM_PATH, 'publications_parsed_concat.ndjson'))

    # bad files
    publications_ocr = read_jsonl(os.path.join(INTERIM_PATH, 'publications_ocr.ndjson'))
    publications_ocr_concat = concatenate_publications(publications_ocr)
    write_jsonl(publications_ocr_concat, os.path.join(INTERIM_PATH, 'publications_ocr_concat.ndjson'))

    # merge files
    publications_merged_concat = publications_parsed_concat + publications_ocr_concat
    write_jsonl(publications_merged_concat, os.path.join(INTERIM_PATH, 'publications_merged_concat.ndjson'))

    # merge metadata 
    meta_parsed = pd.read_csv(os.path.join(INTERIM_PATH, 'metadata_parsed.csv'))
    meta_ocr = pd.read_csv(os.path.join(INTERIM_PATH, 'metadata_ocr.csv'))
    meta_merged = pd.concat([meta_parsed, meta_ocr], ignore_index=True)
    meta_merged.to_csv(os.path.join(INTERIM_PATH, 'metadata_merged.csv'), index=False)
