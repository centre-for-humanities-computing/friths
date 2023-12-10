"""
TODO
loads publications_merged_concat

- remove non-english
- remove duplicates

save it as a new file & update the path in features/run_embeddings.py
"""
import os
import pandas as pd
import pathlib
import math
import textdescriptives as td
from langdetect import detect_langs

from util import *



def check_empty_reference(article: dict):
    pass

def check_authors_not_empty(article: dict):
    pass

def check_sections_not_empty(article: dict):
    pass

def get_textdescriptives(df: pd.DataFrame) -> pd.DataFrame:
    metrics = td.extract_metrics(
        text=df["text"],
        lang="en",
    )

    metrics_df = df[['pub_id']].join(metrics, rsuffix='met_')
    return metrics_df

def lang_detector(text):
    result = detect_langs(text)

    if result[0].prob < 0.5:
        return "low prob"

    else: 
        return result[0].lang

def main():
    DATA_INTERIM = pathlib.Path('data/interim')
    DATA_PROCESSED = pathlib.Path('data/processed')

    meta = pd.read_csv(DATA_INTERIM.joinpath('meta_publications_merged.csv'))
    meta = meta.rename(columns = {'id':'pub_id'})

    texts = pd.DataFrame(read_jsonl(DATA_PROCESSED.joinpath('publications_merged_concat.ndjson')))
    texts['pub_id'] = texts['id'].str.split('_').str[0]

    subset = texts.loc[texts['text'] != ""]

    subset['lang'] = subset['text'].apply(lang_detector)


    for id in subset['pub_id'].unique():
        # getting rows that match the id
        id_df = subset.loc[subset['pub_id'] == id]

        # if there is both an abstract and body
        if len(id_df) > 1:
            # check if they mismatch
            if len(id_df['lang'].unique()) > 1:
                meta.loc[meta['pub_id'] == id, 'lang'] = 'mismatch'
            # otherwise set the unique value
            else:
                meta.loc[meta['pub_id'] == id, 'lang'] = id_df['lang'].unique()[0]
        # if there is only a body, just return the lang of that
        else:
            meta.loc[meta['pub_id'] == id, 'lang'] = id_df['lang'].unique()[0]

    metrics = get_textdescriptives(texts)
    metrics = metrics.drop(columns=['text'])

    meta = meta.merge(metrics, on = 'pub_id')

    meta.to_csv(DATA_PROCESSED.joinpath('meta_publications_quality.csv'))

if __name__ == '__main__':
    main()