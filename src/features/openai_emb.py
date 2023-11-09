"""
"""

import json
from openai import OpenAI
import numpy as np


def log_in_to_api(secrets_path: str = 'secrets.json') -> OpenAI:
    with open(secrets_path, 'r') as f:
        secrets = json.load(f)

    return OpenAI(api_key=secrets['OPENAI_API_KEY'])


def generate_embeddings(client: OpenAI, texts: list[str]) -> np.ndarray:
    """
    """
    if isinstance(texts, str):
        texts = [texts]

    embedding_interface = client.embeddings.create(
        input=texts,
        model="text-embedding-ada-002")

    embeddings = [emb.embedding for emb in embedding_interface.data]
    embeddings = np.array(embeddings)

    return embeddings


if __name__ == "__main__":
    pass
