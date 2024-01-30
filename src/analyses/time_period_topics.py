"""Finds 'topics' in time segments in the full-text corpus with c-TF-IDF.
You may manually change the boundaries manually by hard-coding them in this file.
The script prints every topic in a new line, where the terms are separated by ', '.
To get a .txt file of the results you can pipe the result to that file:
    python3 src/time_period_topics.py > "topics.txt"
"""
import datetime
from typing import Iterable

import numpy as np
import pandas as pd
import scipy.sparse as spr
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import label_binarize


def soft_ctf_idf(
    doc_topic_matrix: np.ndarray, doc_term_matrix: spr.csr_matrix
) -> np.ndarray:
    eps = np.finfo(float).eps
    term_importance = doc_topic_matrix.T @ doc_term_matrix
    overall_in_topic = np.abs(term_importance).sum(axis=1)
    n_docs = len(doc_topic_matrix)
    tf = (term_importance.T / (overall_in_topic + eps)).T
    idf = np.log(n_docs / (np.abs(term_importance).sum(axis=0) + eps))
    ctf_idf = tf * idf
    return ctf_idf


def get_topics(
    components: np.ndarray, vocab: np.ndarray, top_k: int = 10
) -> list[list[str]]:
    highest = np.argpartition(-components, top_k)[:, :top_k]
    top = []
    score = []
    for component, high in zip(components, highest):
        importance = component[high]
        high = high[np.argsort(-importance)]
        score.append(component[high])
        top.append(list(vocab[high]))
    return top


def label_dates(
    dates: Iterable[datetime.date], boundaries: list[datetime.date]
) -> list[int]:
    labels = []
    for date in dates:
        i_segment = 0
        while (i_segment < len(boundaries)) and (boundaries[i_segment] < date):
            i_segment += 1
        labels.append(i_segment)
    return labels


boundaries = [(1980, 8), (1998, 3), (2001, 4), (2002, 5)]
boundaries = [datetime.date(year, month, 1) for year, month in boundaries]

texts = pd.read_json(
    "data/processed/publications_merged_concat.ndjson", lines=True, orient="records"
)
meta = pd.read_csv("data/processed/meta_publications_months.csv", sep=";")
data = texts.merge(meta, on="pub_id", how="inner")
data = data.dropna(subset=["year", "month"])
data["year"] = data["year"].astype(int)
data["month"] = data["month"].astype(int)
data["date"] = [
    datetime.date(year, month, 1) for year, month in zip(data["year"], data["month"])
]
data["segment"] = label_dates(data["date"], boundaries)

document_topic_matrix = label_binarize(
    data["segment"], classes=np.sort(np.unique(data["segment"]))
)
vectorizer = CountVectorizer(stop_words="english", min_df=10)
doc_term_matrix = vectorizer.fit_transform(data["text"])
vocab = vectorizer.get_feature_names_out()

components = soft_ctf_idf(document_topic_matrix, doc_term_matrix)  # type: ignore
topics = get_topics(components, vocab)

for topic in topics:
    print(", ".join(topic))
