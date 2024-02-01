"""Get features

Implemented datasets:
- publications_concat.ndjson
"""

import pandas as pd
from tqdm import tqdm
import tiktoken

from src.features.openai_emb import (
    get_embeddings_and_warnings,
    log_in_to_api,
    get_trunc_text,
)
from src.dataset.util import read_jsonl, write_jsonl


def main(path):
    client = log_in_to_api()
    model = "text-embedding-ada-002"
    encoding = tiktoken.encoding_for_model(model)

    df = pd.read_csv(path).fillna("")

    processed = []
    for i, row in tqdm(df.iterrows()):
        out = {
            "eid": row["eid"],
            "text": row["abstract"],
        }

        trunc_text = get_trunc_text(out["text"], encoding)
        embeds, war = get_embeddings_and_warnings(client, trunc_text, model=model)
        out["embeddings"] = embeds
        out["warning"] = war
        processed.append(out)

    return processed


if __name__ == "__main__":
    # chris
    emb_chris = main(path="data/raw/scopus_abstracts/abstracts_chris_simple.csv")
    write_jsonl(emb_chris, "data/processed/chris_abstracts.ndjson")

    # uta
    emb_uta = main(path="data/raw/scopus_abstracts/abstracts_uta_simple.csv")
    write_jsonl(emb_uta, "data/processed/uta_abstracts.ndjson")
