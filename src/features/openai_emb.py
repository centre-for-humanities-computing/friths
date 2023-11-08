"""
"""

import json
import openai
import numpy as np


def log_in_to_api() -> None:
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)

    openai.api_key = secrets['OPENAI_API_KEY']


def generate_embeddings(texts: list[str]):
    """
    """
    embedding_interface = openai.Embedding.create(
        input=texts,
        model="text-embedding-ada-002")

    embeddings = [obj['embedding'] for obj in embedding_interface['data']]
    embeddings = np.array(embeddings)

    return embeddings


if __name__ == "__main__":
    pass