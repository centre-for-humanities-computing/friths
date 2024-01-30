import json
from urllib.parse import urlencode

import pandas as pd
import requests

df = pd.concat((pd.read_csv("raw/chris.csv"), pd.read_csv("raw/uta.csv")))
df = df.drop_duplicates("eid")

df.title

chris_id = "36051252900"
uta_id = "56046313500"

citations = {}
api_url = "https://api.elsevier.com/content/search/scopus"
subset = df.head(35)
for eid, title in zip(subset["eid"], subset["title"]):
    query = {
        "apiKey": "edaad4bd80e4ef26b35477dbaa151eb5",
        "query": f"REFTITLE({title}) AND (AU-ID({chris_id}) OR AU-ID({uta_id}))",
    }
    query_url = f"{api_url}?{urlencode(query)}"
    response = requests.get(query_url)
    cited_by = []
    try:
        for entry in response.json()["search-results"]["entry"]:
            cited_by.append(entry["eid"])
        citations[eid] = cited_by
    except KeyError:
        continue

with open("citation_connections.json", "w") as in_file:
    in_file.write(json.dumps(citations))

edges: set[tuple[str, str]] = set()
for to_id, from_ids in citations.items():
    for from_id in from_ids:
        edges.add((from_id, to_id))

citation_graph = pd.DataFrame(edges, columns=["from_eid", "to_eid"])
citation_graph.to_csv("citation_graph.csv")
