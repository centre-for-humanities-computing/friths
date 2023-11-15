"""Get features

Implemented datasets:
- publications_concat.ndjson
"""

from tqdm import tqdm

from src.features.openai_emb import get_embeddings_and_warnings, log_in_to_api
from src.dataset.util import read_jsonl, write_jsonl


def main():

    client = log_in_to_api()
    model = "text-embedding-ada-002"

    path = "data/interim/publications_concat.ndjson"

    texts = read_jsonl(path)

    for text in tqdm(texts):
        embeds, war = get_embeddings_and_warnings(client, text["text"], model=model)
        text["embeddings"] = embeds
        text["warning"] = war

    write_jsonl(texts, "data/processed/publications_concat.ndjson")


if __name__ == "__main__":
    main()
