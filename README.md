# Friths
Get started using `bash dev_setup.sh`

The project is structured following the [cookiecutter data science template](https://github.com/drivendata/cookiecutter-data-science/tree/master).

<br>

## Pipelines
### Publications Pipeline
Run using `make publications`

Input: publication PDFs (`data/raw/UTA publications`)

Manual work required to keep most data:
- Export scanned files (`failed_pdf_paths.txt`) with "Embed text" (Sofie)
- Manually convert or fix non-pdf files (`non_pdf_paths.txt`)

Pipeline:
A) `dataset/parse_publications.py`
We try to extract information using `scipdf`, which has a java dependency `grobid`.
If unsuccessful, the file will get added to `failed_pdf_paths.txt` & OCR'd later (no metadata avilable then).

B) `dataset/ocr_failed_pdf.py`
Runs OCR using `pytesseract`.
Outputs are saved separately from the parsed files.

C1) `dataset/metadata_publications.py`
Generates metadata & document ids separately for both file types (PARSING and OCR).
Most importatly, tries to reconstruct the publication year.
Otherwise, just takes the metadata found by `scipdf` (PARSING files only), or adds blank columns (OCR files only)/

C2) `dataset/fetch_scopus.py`
Fetches metadata from the Scopus API, given author IDs.

C3) `dataset/metadata_scopus.py`
Merges PARSING metadata with records extracted from Scopus (`data/raw/ScopusExport_{author_id}_{date}.csv`)

D) `dataset/concat_publications.py`
Concatenates article sections into a single block of text.
Creates files with the extracted abstracts.
Merges:
    - PARSING and OCR files.
    - PARSING and OCR metadata files.
    - PARSING and OCR abstract files.

E) `dataset/quality_checks_publications.py`
Adds info about language & text descriptive stats into the metadata.

F) `features/run_embeddings.py`
Get embeddings from OpenAI


Analysis:
`notebooks/experiment_abstracts.ipynb`
`notebooks/experiment_infodynamics.ipynb`
