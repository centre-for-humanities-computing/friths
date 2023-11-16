"""
Assign IDs, reconstruct publication years of publications.
Second step.
"""

import os
import re
from warnings import warn
import pandas as pd
import numpy as np

from src.dataset.util import load_iterim_publications, read_jsonl


def parse_metadata(parsed_publications: list[dict]) -> pd.DataFrame:
    """Extracts found metadata from parsed pdfs
    """

    df = pd.DataFrame({
        'id': [article['id'] for article in parsed_publications],
        'title': [article['title'] for article in parsed_publications],
        'date': [article['pub_date'] for article in parsed_publications],
        'doi': [article['doi'] for article in parsed_publications],
        'path': [article['path'] for article in parsed_publications],
        'source': 'parsing'
    }).replace('', np.nan)

    return df


def parse_metadata_ocr_files(ocr_publications: list[dict]) -> pd.DataFrame:
    """Extracts metata from the OCR files, to follow the same schema as the regular files
    """

    df = pd.DataFrame({
        'id': [article['id'] for article in ocr_publications],
        'title': np.nan,
        'date': np.nan,
        'doi': np.nan,
        'path': [article['path'] for article in ocr_publications],
        'source': 'ocr',
    }).replace('', np.nan)

    return df


def _extract_publication_year(parsed_metadata: pd.DataFrame) -> list:
    """
    """
    # iterate over rows trying to catch the main info
    reconstructed_date = []

    for i, row in parsed_metadata.iterrows():
        filepath = row['path']
        pdf_name = filepath.split('/')[-1]
        pdf_name_match = re.search(r'\d{4}', pdf_name)

        # case when date is missing
        if pd.isnull(row['date']):
            # case when file comes from a yearly folder
            if "UF papers 1969-2004 copy" in filepath:
                # take date from the folder name
                date = filepath.split('/')[-2]
                reconstructed_date.append(date)
                continue  # skip to next iteration
            # case when pdf name contains the year
            elif pdf_name_match:
                date = pdf_name_match.group()
                reconstructed_date.append(date)
                continue
            # DANGER: if there are multiple years in the path, only the first 
            # will be used
            elif "UF papers 1969-2004 copy" not in filepath:
                parent_dir_name = filepath.split('/')[-2]
                parent_dir_match = re.search(r'\d{4}', parent_dir_name)
                if parent_dir_match:
                    date = parent_dir_match.group()
                    reconstructed_date.append(date)
                    continue
                else:
                    reconstructed_date.append(np.nan)
                    continue

        else:
            reconstructed_date.append(row['date'])
        
    return reconstructed_date


def reconstruct_publication_year(parsed_metadata: pd.DataFrame, hot_fixes: dict[str, str]) -> pd.DataFrame:
    """
    """
    reconstructed_date = _extract_publication_year(parsed_metadata)

    # validate dates
    for date in reconstructed_date:
        try:
            pd.to_datetime(date)
        except:
            warn(date)

    parsed_metadata['reconstructed_date'] = reconstructed_date
    # Apply hot fixes (known errors)
    parsed_metadata['reconstructed_date'] = parsed_metadata['reconstructed_date'].replace(hot_fixes)

    return parsed_metadata


if __name__ == "__main__":

    OUTDIR = 'data/interim'

    ### parse good files
    publications_parsed = load_iterim_publications(OUTDIR)
    meta_parsed = parse_metadata(publications_parsed)

    hot_fixes = {
        "19991651-06-03": "1999",
        "207813": "2005"
        }
    
    meta_parsed = reconstruct_publication_year(meta_parsed, hot_fixes=hot_fixes)
    meta_parsed.to_csv(os.path.join(OUTDIR, 'publications_meta.csv'), index=False)
    
    ### parse bad files
    publications_ocr = read_jsonl(os.path.join(OUTDIR, 'publications_failed.ndjson'))
    meta_ocr = parse_metadata_ocr_files(publications_ocr)
    meta_ocr = reconstruct_publication_year(meta_ocr, hot_fixes={})
    meta_parsed.to_csv(os.path.join(OUTDIR, 'publications_failed_meta.csv'), index=False)
