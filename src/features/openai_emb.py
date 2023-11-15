"""
"""

import json
import warnings

from openai import OpenAI
import numpy as np


def log_in_to_api(secrets_path: str = "secrets.json") -> OpenAI:
    with open(secrets_path, "r") as f:
        secrets = json.load(f)

    return OpenAI(api_key=secrets["OPENAI_API_KEY"])


def generate_embeddings(client: OpenAI, texts: list[str]) -> np.ndarray:
    """ """
    if isinstance(texts, str):
        texts = [texts]

    embedding_interface = client.embeddings.create(
        input=texts, model="text-embedding-ada-002"
    )

    embeddings = [emb.embedding for emb in embedding_interface.data]
    embeddings = np.array(embeddings)

    return embeddings


def get_embeddings_and_warnings(client: OpenAI, text: str, model: str) -> tuple[np.ndarray, str]:
    if text == "":
        warning = "empty"
        emb = ""
    else:
        text = text.replace("\n", " ")

        with warnings.catch_warnings(record=True) as w:
            emb_interface = client.embeddings.create(input=[text], model=model)
            emb = emb_interface.data[0].embedding

        if w:
            warning = w
        else:
            warning = "ok :)"

    return emb, warning


if __name__ == "__main__":
    pass
