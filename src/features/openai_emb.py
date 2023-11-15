"""Generalized functions for interacting with the Opean AI embedding API
"""

import json
import warnings

from openai import OpenAI, BadRequestError
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


def get_embeddings_and_warnings(
    client: OpenAI, text: str, model: str
) -> tuple[list[float], str]:
    """
    Make openAI embeddings API requests and catch errors/warnings.

    Parameters
    ----------
    clinet : OpenAI
        instantiated openai client (after logging ins)

    text : str
        single string to process
    
    model : str
        name of open-ai model to use

    Returns
    -------
    emb : list[float]
        list of floats representing the embedding
    warning : str
        caught warning or "ok :)" if no warning
    """
    
    # don't attempt with empty text
    if text == "":
        warning = "empty"
        emb = []

    # non empty text
    else:
        text = text.replace("\n", " ")

        # try to get embeddings & catch warnings
        try:
            with warnings.catch_warnings(record=True) as w:
                emb_interface = client.embeddings.create(input=[text], model=model)
                emb = emb_interface.data[0].embedding
                if w:
                    warning = str(w)
                else:
                    warning = "ok :)"

        # if api request fails, catch the error
        except BadRequestError as e:
            emb = []
            warning = str(e)

    return emb, warning


if __name__ == "__main__":
    pass
