"""Get features

Implemented datasets:
- publications_concat.ndjson
"""

from tqdm import tqdm
import tiktoken

from src.features.openai_emb import get_embeddings_and_warnings, log_in_to_api, get_trunc_text
from src.dataset.util import read_jsonl, write_jsonl


def main():

    client = log_in_to_api()
    model = "text-embedding-ada-002"

    path = "data/interim/publications_merged_concat.ndjson"

    texts = read_jsonl(path)

    encoding = tiktoken.encoding_for_model(model)

    for text in tqdm(texts):
        trunc_text = get_trunc_text(text['text'], encoding)
        embeds, war = get_embeddings_and_warnings(client, trunc_text, model=model)
        text["embeddings"] = embeds
        text["warning"] = war

    write_jsonl(texts, "data/processed/publications_merged_concat.ndjson")


if __name__ == "__main__":
    main()
