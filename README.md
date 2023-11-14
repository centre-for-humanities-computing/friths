# Friths
Get started using `bash dev_setup.sh`

The project is structured following the [cookiecutter data science template](https://github.com/drivendata/cookiecutter-data-science/tree/master).

<br>

## Pipelines
### Publications Pipeline
Run using `make publications`

- uses pdfs with articles (`data/raw/UTA publications`),
- extracts information using `scipdf`, which has a java dependency `grobid`
- generates metadata & document ids
- generates a `ndjson` file with the article sections
