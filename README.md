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
- Get extra metadata for Uta Frith from [ResearchRabbit](https://www.researchrabbitapp.com/) (find author on ResearchRabbit, select all "Published Work" -> "Export Papers")

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

C2) `dataset/metadata_researchrabbit.py`
Merges PARSING metadata with records extracted from ResearchRabbit (`data/raw/ResearchRabbit_Export_{ID}.csv`)
Overwrites `meta_publications_parsed.csv`

D) `dataset/concat_publications.py`
Merges PARSING and OCR files to embed them.
Also merges metadata files.

E) `dataset/quality_checks_publications.py`
Adds info about language & text descriptive stats into the metadata.

F) `features/run_embeddings.py`
Get embeddings from OpenAI


Analysis:
`notebooks/experiment_abstracts.ipynb`
`notebooks/experiment_infodynamics.ipynb`
