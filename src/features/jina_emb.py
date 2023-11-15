"""generate Jina embeddingss
"""

import os
import datasets
from sentence_transformers import SentenceTransformer


def load_mddel() -> SentenceTransformer:
    return SentenceTransformer("jinaai/jina-embeddings-v2-base-en")
