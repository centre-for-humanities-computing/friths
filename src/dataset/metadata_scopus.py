"""Merge local metadata with a metadata dump from Scopus
"""

import os
import difflib
import pandas as pd


def augument_on_title_lookup(
    df_parsing: pd.DataFrame, df_sc: pd.DataFrame, verbose=True
) -> pd.DataFrame:
    """enrich local metadata by merging on article title.

    Parameters
    ----------
    df_parsing : pd.DataFrame
        metadata extracted from scipdf parsed files.
        is generated in dataset/metadata_publications.py

    df_sc : pd.DataFrame
        metadata dump from Scopus.
        Make sure that it is ordered by date for deduplication to work.

    verbose : bool
        print tables here and there?

    Returns
    -------
    m_augumented_title : pd.DataFrame
        subset of df_parsing, augumented with title lookup
    """
    # standardize to lowercase
    df_parsing["title_in_prs"] = df_parsing["title"].str.lower()
    df_sc["title_in_sc"] = df_sc["title"].str.lower()

    # get articles WITHOUT doi & WITH title
    df_parsing_no_doi = df_parsing[df_parsing["doi"].isna()]
    df_parsing_no_doi_yes_tit = df_parsing_no_doi[
        ~df_parsing_no_doi["title_in_prs"].isna()
    ]

    # fuzzy search for title pairs
    found_pairs = []
    for i, row in df_parsing_no_doi_yes_tit.iterrows():
        close_match = difflib.get_close_matches(
            row["title_in_prs"],
            df_sc["title_in_sc"].to_list(),
            # high cutoff to minimize false positives
            cutoff=0.8,
        )

        if close_match == []:
            n_matches = 0
            selected_title = None
            close_match = None
        else:
            n_matches = len(close_match)
            selected_title = close_match[0]

        found_pairs.append(
            {
                "title_in_prs": row["title_in_prs"],
                "title_in_sc": selected_title,
                "matches": close_match,
                "pub_id": row["pub_id"],
                "n_matches": n_matches,
            }
        )

    found_pairs = pd.DataFrame(found_pairs)
    useful_found_pairs = found_pairs.query("n_matches > 0")

    if verbose:
        print("Title merging: useful found pairs \n")
        print(useful_found_pairs.info())

    # add found title pairs
    m_augumented_title = pd.merge(
        df_parsing_no_doi_yes_tit.drop(columns=["doi"]),
        useful_found_pairs.drop(columns=["title_in_prs"]),
        on="pub_id",
        how="left",
    )

    # merge in research rabbit metadata based on title pairs
    m_augumented_title = pd.merge(
        m_augumented_title,
        df_sc,
        on="title_in_sc",
        how="left",
        suffixes=("_prs", "_sc"),
    )

    if verbose:
        print("\n\nTitle merging: merged dataset \n")
        print(m_augumented_title.info())

    return m_augumented_title


def augument_on_doi(
    df_parsing: pd.DataFrame, df_sc: pd.DataFrame, verbose: bool = True
):
    """enrich local metadata by merging on doi.

    Parameters
    ----------
    df_parsing : pd.DataFrame
        metadata extracted from scipdf parsed files.
        is generated in dataset/metadata_publications.py


    df_sc : pd.DataFrame
        metadata dump from Scopus.
        Make sure that it is ordered by date for deduplication to work.

    verbose : bool
        print tables here and there?

    Returns
    -------
    m_augumented_doi : pd.DataFrame
        subset of df_parsing, augumented with DOI lookup
    """
    # subset: only records with DOI
    df_parsing_yes_doi = df_parsing[~df_parsing["doi"].isna()]
    # merge on doi
    m_augumented_doi = pd.merge(
        df_parsing_yes_doi, df_sc, on="doi", how="left", suffixes=("_prs", "_sc")
    )

    if verbose:
        print("\n\nDOI merging: merged dataset \n")
        print(m_augumented_doi.info())

    return m_augumented_doi


def merge_augumented_datasets(
    df_parsing: pd.DataFrame,
    m_augumented_title: pd.DataFrame,
    m_augumented_doi: pd.DataFrame,
    verbose: bool = True,
) -> pd.DataFrame:
    """Merge in all the augumented tables with the original metadata.
    Keep rows that were not augumented.

    Parameters
    ----------
    df_parsing : pd.DataFrame
        metadata extracted from scipdf parsed files.
        is generated in dataset/metadata_publications.py

    m_augumented_title : pd.DataFrame
        output of `augument_on_title_lookup()`

    m_augumented_doi : pd.DataFrame
        output of `augument_on_doi()`

    verbose : bool
        print tables here and there?


    Returns
    -------
    m_augumented_doi : pd.DataFrame
        subset of df_parsing, augumented with DOI lookup
    """
    # join the partially augumented dfs
    m_parsing_aug_complete = pd.concat(
        [m_augumented_title, m_augumented_doi], ignore_index=True
    )
    # drop garbage columns
    m_parsing_aug_complete = m_parsing_aug_complete.drop(
        columns=["matches", "n_matches"]
    )

    # handle duplicates
    if verbose:
        print("\n\nDuplicated IDs")
        duplicatesd_ids = m_parsing_aug_complete[
            m_parsing_aug_complete["pub_id"].duplicated()
        ]
        if len(duplicatesd_ids) > 0:
            print(duplicatesd_ids)
            print("\nREMOVING DUPLICATES")
            print("\nMAKE SURE THAT YOUR SCOPUS DUMP IS ORDERED BY DATE")
        else:
            print("\nNO DUPLICATES FOUND")

    m_parsing_aug_complete = m_parsing_aug_complete.drop_duplicates(subset="pub_id")
    assert m_parsing_aug_complete["pub_id"].nunique() == len(m_parsing_aug_complete)

    # find document ids that were not possible to augument
    non_overlap = set(df_parsing["pub_id"].tolist()) - set(
        m_parsing_aug_complete["pub_id"].tolist()
    )
    assert len(df_parsing) - len(m_parsing_aug_complete) == len(non_overlap)

    # subset of documents that were not augumented
    m_parsing_missing = df_parsing[df_parsing["pub_id"].isin(non_overlap)]
    m_parsing_missing = m_parsing_missing.drop(
        columns=["title", "doi", "title_in_prs"]
    ).rename(  # they are empty
        columns={"year": "year_prs"}
    )

    if verbose:
        print("\n\nAugumenting: non-augumented articles \n")
        print(m_parsing_missing.info())

    # merge non-augumented articles back into parsing
    # create an output object
    df_parsing_ = pd.concat(
        [m_parsing_aug_complete, m_parsing_missing], ignore_index=True
    )  # adds missing to the end
    df_parsing_ = df_parsing_.reset_index(drop=True)

    # at this point, we have two records for title and date
    # one local and one from Scopus
    # if Scopus data is available, pick that as the representative data
    # if not, take local metadata
    df_parsing_["date"] = None
    df_parsing_["title"] = None
    for i, row in df_parsing_.iterrows():
        # year
        if pd.isna(row["coverDate"]):
            df_parsing_.loc[i, "date"] = row["reconstructed_date"]
        else:
            df_parsing_.loc[i, "date"] = row["coverDate"]

        # title
        if pd.isna(row["title_sc"]):
            df_parsing_.loc[i, "title"] = row["title_prs"]
        else:
            df_parsing_.loc[i, "title"] = row["title_sc"]

    # drop garbage columns
    df_parsing_ = df_parsing_.drop(
        columns=["title_in_sc", "title_in_prs", "title_prs", "title_sc"]
    ).drop(columns=["reconstructed_date"])

    return df_parsing_


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--scopus_file")
    args = ap.parse_args()

    # TODO make legit
    args.scopus_file = "ScopusExport_56046313500.csv"

    RAW_PATH = os.path.join("data", "raw")
    INTERIM_PATH = os.path.join("data", "interim")

    # load input datasets
    df_parsed = pd.read_csv(os.path.join(INTERIM_PATH, "meta_publications_parsed.csv"))
    df_sc = pd.read_csv(os.path.join(RAW_PATH, args.scopus_file))

    ###
    ### augumentation
    ###
    m_augumented_title = augument_on_title_lookup(
        df_parsing=df_parsed, df_sc=df_sc, verbose=True
    )
    m_augumented_doi = augument_on_doi(df_parsing=df_parsed, df_sc=df_sc, verbose=True)
    df_parsed_augumented = merge_augumented_datasets(
        df_parsing=df_parsed,
        m_augumented_title=m_augumented_title,
        m_augumented_doi=m_augumented_doi,
        verbose=True,
    )

    # export final df
    df_parsed_augumented.to_csv(
        os.path.join(INTERIM_PATH, "meta_publications_parsed_augumented.csv"),
        index=False,
    )
