from itertools import islice

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scipy.sparse as spr
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import label_binarize


def batched(iterable, n):
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def soft_ctf_idf(
    doc_topic_matrix: np.ndarray, doc_term_matrix: spr.csr_matrix
) -> np.ndarray:
    eps = np.finfo(float).eps
    term_importance = doc_topic_matrix.T @ doc_term_matrix
    overall_in_topic = np.abs(term_importance).sum(axis=1)
    n_docs = len(doc_topic_matrix)
    tf = (term_importance.T / (overall_in_topic + eps)).T
    idf = np.log(n_docs / (np.abs(term_importance).sum(axis=0) + eps))
    ctf_idf = tf * idf
    return ctf_idf


def get_topics(
    components: np.ndarray, vocab: np.ndarray, top_k: int = 10
) -> list[list[str]]:
    highest = np.argpartition(-components, top_k)[:, :top_k]
    top = []
    score = []
    for component, high in zip(components, highest):
        importance = component[high]
        high = high[np.argsort(-importance)]
        score.append(component[high])
        top.append(list(vocab[high]))
    return top


def position_labels(cluster_labels: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    centroids = []
    unique_labels = np.unique(cluster_labels)
    unique_labels = np.sort(unique_labels)
    centroid_graph = nx.Graph()
    centroid_graph.add_nodes_from(unique_labels)
    initial_positions = {}
    for label in unique_labels:
        cluster_embeddings = embeddings[cluster_labels == label]
        x, y = np.median(cluster_embeddings, axis=0)
        initial_positions[label] = (x, y)
    centroids = np.stack([list(initial_positions[label]) for label in unique_labels])
    return centroids


def format_topic(topic: list[str]) -> str:
    res = ""
    topic = [f"<b>{word}</b>" for word in topic]
    batches = batched(topic, 4)
    for batch in batches:
        res += ", ".join(batch) + "<br>"
    return res


edges = pd.read_csv("citation_graph.csv", index_col=0)
abstracts = pd.read_csv("abstracts.csv")
node_to_abstract = dict(zip(abstracts["eid"], abstracts["abstract"]))

all_papers = pd.concat([pd.read_csv("raw/uta.csv"), pd.read_csv("raw/chris.csv")])
node_to_title = dict(zip(all_papers.eid, all_papers.title))

G = nx.DiGraph()
G.add_edges_from(edges.values.tolist())

communities = nx.community.louvain_communities(G)
node_to_community = []
for i_community, community in enumerate(communities):
    for elem in community:
        node_to_community.append((elem, i_community))
communities_df = pd.DataFrame(node_to_community, columns=["eid", "community_id"])
data = communities_df.merge(abstracts, on="eid", how="inner")
data = data.dropna(subset=["abstract"])
labels = data["community_id"]
document_topic_matrix = label_binarize(labels, classes=np.sort(np.unique(labels)))
vectorizer = CountVectorizer(stop_words="english")
doc_term_matrix = vectorizer.fit_transform(data["abstract"])
vocab = vectorizer.get_feature_names_out()

components = soft_ctf_idf(document_topic_matrix, doc_term_matrix)  # type: ignore
topics = get_topics(components, vocab)

optimal_distance = 1.5 * (1 / np.sqrt(len(G.nodes)))
positions = nx.spring_layout(G, seed=42, k=optimal_distance)
community_pos = np.stack([positions[node] for node in data["eid"]])
centroids = position_labels(np.array(labels), community_pos)

connecting_nodes = {}
for u, v in G.edges:
    if u not in connecting_nodes:
        connecting_nodes[u] = set()
    connecting_nodes[u].add(dict(node_to_community)[v])
important_nodes = [
    node for node, communities in connecting_nodes.items() if len(communities) > 1
]

color_sequence = px.colors.qualitative.Safe
community_to_color = dict(zip(range(len(communities)), color_sequence))

fig = go.Figure()
for nfrom, nto in G.edges:
    x0, y0 = positions[nfrom]
    x1, y1 = positions[nto]
    fig.add_shape(type="line", x0=x0, x1=x1, y0=y0, y1=y1, layer="below", opacity=0.3)
done_nodes = set()
for node in important_nodes:
    x, y = positions[node]
    title = node_to_title[node]
    if len(title) > 60:
        title = title[:50] + "..."
    fig.add_annotation(
        x=x,
        y=y,
        ay=40 if np.random.binomial(1, 0.5) == 0 else -40,
        text=title,
        showarrow=True,
        arrowhead=2,
        arrowwidth=2.5,
    )
for i_community, (community, (centroid_x, centroid_y), topic) in enumerate(
    zip(communities, centroids, topics)
):
    community_x = []
    community_y = []
    for node in community:
        community_x.append(positions[node][0])
        community_y.append(positions[node][1])
        done_nodes.add(node)
    node_trace = go.Scatter(
        text=[node_to_title[node] for node in community],
        name=format_topic(topic),
        x=community_x,
        y=community_y,
        mode="markers",
        marker=dict(
            line=dict(color="black", width=3),
            size=16,
            color=community_to_color[i_community],
        ),
        hovertemplate="<b>%{text}</b>",
    )
    fig.add_trace(node_trace)
    fig.add_annotation(
        x=centroid_x,
        y=centroid_y,
        text=format_topic(topic),
        bgcolor="white",
        font=dict(size=14),
        opacity=0.85,
        ax=0,
        ay=0,
        showarrow=False,
    )
outliers = [node for node in G.nodes if node not in done_nodes]
outlier_x = []
outlier_y = []
for node in outliers:
    outlier_x.append(positions[node][0])
    outlier_x.append(positions[node][1])
    done_nodes.add(node)
node_trace = go.Scatter(
    name="Outliers",
    x=outlier_x,
    y=outlier_y,
    mode="markers",
    marker=dict(color="black"),
)
fig = fig.add_trace(node_trace)
fig = fig.update_layout(template="plotly_white")
fig = fig.update_traces(showlegend=False)
fig.show()

fig.write_html("citation_graph.html")
