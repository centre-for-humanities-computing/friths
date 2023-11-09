"""
Extracts individual sections to model, assigns IDs and saves them to a file.

TODO
- remove non-english
- remove duplicates
"""

import os
import datasets
import pandas as pd
import numpy as np

from src.dataset.util import load_iterim_publications, IDGenerator


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


if __name__ == '__main__':

    INTERIM_PATH = 'data/interim/'
    PROCESSED_PATH = 'data/processed/'

    publications = load_iterim_publications(INTERIM_PATH)
    schema = schema_publications(publications)
    schema.to_csv(os.path.join(PROCESSED_PATH, 'publications.csv'), index=False)
