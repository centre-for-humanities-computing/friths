"""
"""

import os
from src.dataset.util import read_jsonl, write_jsonl


DATA_INTERIM = 'data/interim/'


def concat_text(article):
    concat_sections = []

    for section in article["sections"]:
        temp_text = "\n".join((section["heading"], section["text"]))

        concat_sections.append(temp_text)

    text = "\n".join(concat_sections)

    return text


def main(data_interim=DATA_INTERIM):
    path = os.path.join(data_interim, "publications.ndjson")

    abstracts = []
    no_abstracts = []

    full_data = []

    data = read_jsonl(path)

    for line in data:
        temp_a = {
            "id": f"{line['id']}_a",
            "pub_date": line["pub_date"],
            "text": line["abstract"],
        }
        full_data.append(temp_a)
        temp_b = {
            "id": f"{line['id']}_b",
            "pub_date": line["pub_date"],
            "text": concat_text(line),
        }
        full_data.append(temp_b)

        if line["abstract"] != "":
            abstracts.append(line["id"])

        else:
            no_abstracts.append(line["id"])

    outpath = os.path.join(data_interim, "publications_concat.ndjson")
    write_jsonl(full_data, outpath)

    print(f"Number of files with an abstract: {len(abstracts)}")
    print(f"Number of files without an abstract: {len(no_abstracts)}")
    print(f"Total number of files: {len(full_data) / 2}")


if __name__ == "__main__":
    main()
