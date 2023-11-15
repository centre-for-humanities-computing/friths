import json
from openai import OpenAI

from src.features.openai_emb import get_embeddings_and_warnings
from src.dataset.util import read_jsonl, write_jsonl


def main():
    with open("secrets.json") as f:
        api_key = json.load(f)

    client = OpenAI(api_key=api_key['OPENAI_API_KEY'])
    model = "text-embedding-ada-002"

    path = "data/interim/publications_concat.ndjson"

    texts = read_jsonl(path)

    for text in texts:
        embeds, war = get_embeddings_and_warnings(client, text["text"], model=model)
        text["embeddings"] = embeds
        text["warning"] = war

    write_jsonl(texts, "data/processed/publications.ndjson")


if __name__ == "__main__":
    main()
