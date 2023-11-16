"""
Extracts individual sections to model, assigns IDs and saves them to a file.

TODO
- merge good and bad files!
- remove non-english
- remove duplicates
"""

import os
import pandas as pd
import numpy as np

from src.dataset.util import IDGenerator, read_jsonl, write_jsonl


def schema_publications(parsed_publications: list[dict]) -> pd.DataFrame:
    """
    Extracts each section of a publication as a row, assigning IDs.
    IDs are in format p<publication_id>_<section_id>. 
    In case of abstract, the section_id is 'a'. Other sections are numbered.
    """
    docs = []

    for article in parsed_publications:
        # initialize a new id gen for each article
        id_gen = IDGenerator()
        # process abstract
        docs.append({
            'id': str(article['id']) + '_a',
            'text': article['abstract'],
            'heading': np.nan,
            'n_publication_ref': np.nan,
            'n_figure_ref': np.nan
        })
        # process body
        for section in article['sections']:
            docs.append({
                'id': str(article['id']) + '_' + str(id_gen.generate_id()),
                'text': section['heading'] + " " + section['text'],
                'heading': section['heading'].lower(),
                'n_publication_ref': section['n_publication_ref'],
                'n_figure_ref': section['n_figure_ref']
            })

        df = pd.DataFrame(docs).replace('', np.nan)
        return df


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
    PROCESSED_PATH = 'data/processed/'

    publications_parsed = read_jsonl(os.path.join(INTERIM_PATH, 'publications_parsed.ndjson'))
    # convert to section-by-section schema & export
    schema = schema_publications(publications_parsed)
    schema.to_csv(os.path.join(INTERIM_PATH, 'publications_parsed_sections.csv'), index=False)
    # concatenate texts & export
    concat = concatenate_publications(publications_parsed)
    write_jsonl(concat, os.path.join(INTERIM_PATH, 'publications_parsed_concat.ndjson'))
