"""
Concatenates article sections into a single block of text.
Extracts abstracts.
Merges all the files.
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


def concatenate_publications(parsed_publications: list[dict]) -> tuple[list[dict], list[dict]]:

    abstracts = []
    publications = []

    for line in parsed_publications:

        publication_body = concat_text(line)

        if line['abstract'] != "":
            publication_body = line["abstract"] + "\n" + publication_body

        temp_publication = {
            "id": line["id"],
            "text": publication_body
        }

        temp_abstract = {
            "id": line["id"],
            "abstract": line["abstract"] 
        }

        abstracts.append(temp_abstract)
        publications.append(temp_publication)

    return abstracts, publications


if __name__ == '__main__':

    INTERIM_PATH = 'data/interim/'


    ###
    ### CONCATENATION
    ###

    # good files
    publications_parsed = read_jsonl(os.path.join(INTERIM_PATH, 'publications_parsed.ndjson'))
    parsed_abs, parsed_pub = concatenate_publications(publications_parsed)
    write_jsonl(parsed_abs, os.path.join(INTERIM_PATH, 'abstracts_parsed.ndjson'))
    write_jsonl(parsed_pub, os.path.join(INTERIM_PATH, 'publications_parsed_concat.ndjson'))

    # bad files
    publications_ocr = read_jsonl(os.path.join(INTERIM_PATH, 'publications_ocr.ndjson'))
    ocr_abs, ocr_pub = concatenate_publications(publications_ocr)
    write_jsonl(ocr_abs, os.path.join(INTERIM_PATH, 'abstracts_ocr.ndjson'))
    write_jsonl(ocr_pub, os.path.join(INTERIM_PATH, 'publications_ocr_concat.ndjson'))

    ###
    ### MERGING
    ### 

    # merge files
    publications_merged_concat = parsed_pub + ocr_pub
    write_jsonl(publications_merged_concat, os.path.join(INTERIM_PATH, 'publications_merged_concat.ndjson'))

    # merge metadata 
    meta_parsed = pd.read_csv(os.path.join(INTERIM_PATH, 'meta_publications_parsed_augumented.csv'))
    meta_ocr = pd.read_csv(os.path.join(INTERIM_PATH, 'meta_publications_ocr.csv'))
    meta_merged = pd.concat([meta_parsed, meta_ocr], ignore_index=True)
    meta_merged.to_csv(os.path.join(INTERIM_PATH, 'meta_publications_merged.csv'), index=False)
