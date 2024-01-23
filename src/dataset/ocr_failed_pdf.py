"""
"""

import io
import json
from pathlib import Path

import numpy as np
from tqdm import tqdm
import pytesseract
from PIL import Image
import fitz  # PyMuPDF

from src.dataset.util import read_jsonl, IDGenerator


def ocr_pdf(pdf_path: str) -> str:
    """OCR a PDF file and return the plain text."""
    pdf_document = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(pdf_document)):
        # Get the page
        page = pdf_document[page_num]

        # Get the image of the page
        pix = page.get_pixmap()
        image_bytes = pix.tobytes("ppm")

        # Create an Image object from the bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Use pytesseract to do OCR on the image
        text = pytesseract.image_to_string(image)

        full_text += text + "\n"

    pdf_document.close()
    return full_text


def load_failed_paths(path: str = "data/interim/failed_pdf_paths.txt") -> list[str]:
    """ """
    with open(path) as fin:
        failed_docs = [line.strip() for line in fin.readlines()]

    return failed_docs


def find_top_current_id():
    """Continue with ID generation from the top ID in the current interim dataset"""
    pub = read_jsonl("data/interim/publications_parsed.ndjson")
    ids = [int(art["pub_id"][1:]) for art in pub]
    return max(ids)


if __name__ == "__main__":
    failed_paths = load_failed_paths()
    top_id = find_top_current_id()
    id_gen = IDGenerator(starting_position=top_id + 1)

    OUTPATH = Path("data/interim/")

    with open(OUTPATH.joinpath("publications_ocr.ndjson"), "w") as file:
        for path in tqdm(failed_paths):
            pdf_plain_text = ocr_pdf(path)
            out = {
                "pub_id": "p" + str(id_gen.generate_id()),
                "path": path,
                "title": "",
                "authors": "",
                "abstract": "",
                "pub_date": "",
                "sections": [{"heading": "", "text": pdf_plain_text}],
                "doi": "",
            }
            json_string = json.dumps(out)
            file.write(json_string + "\n")
