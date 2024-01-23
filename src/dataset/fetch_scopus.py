"""Extract Scopus data
"""

import os
import pandas as pd
from pybliometrics.scopus import ScopusSearch


def fetch_author_metadata(author_id: int) -> pd.DataFrame:
    """ """
    search_author = ScopusSearch(query=f"AU-ID({author_id})", download=True)

    df = pd.DataFrame(search_author.results)

    # sort by date
    df["sorting_date"] = pd.to_datetime(df["coverDate"])
    df = df.sort_values(by="sorting_date")
    df = df.drop(columns=["sorting_date"])

    return df


def fetch_author_abstracts():
    """ """
    # TODO
    pass


if __name__ == "__main__":
    id_uta = 56046313500
    id_chris = 36051252900

    path_uta = f"data/raw/ScopusExport_{id_uta}.csv"
    path_chris = f"data/raw/ScopusExport_{id_chris}.csv"

    if not os.path.exists(path_uta):
        df_uta = fetch_author_metadata(id_uta)
        df_uta.to_csv(f"data/raw/ScopusExport_{id_uta}.csv", index=False)

    if not os.path.exists(path_chris):
        df_chris = fetch_author_metadata(id_chris)
        df_chris.to_csv(f"data/raw/ScopusExport_{id_chris}.csv", index=False)
