from pathlib import Path
import pandas as pd
import networkx as nx
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
st.set_page_config(page_title="Campaign Graph", page_icon="🕸️", layout="wide")
st.title("🕸️ Coordinated Campaign Detection")
st.caption("Sender → recipient relationships, campaign clusters, and coordinated abuse risk")

path = ROOT / "outputs" / "scored_messages.csv"
if not path.exists():
    st.warning("Run `python src/run_pipeline.py --rows 30000` first.")
    st.stop()

df = pd.read_csv(path)
agg = df.groupby("sender_id").agg(
    messages=("message_id","count"),
    recipients=("receiver_id","nunique"),
    spam_rate=("is_spam","mean"),
    avg_score=("spam_score","mean"),
    reports=("prior_reports","sum"),
    repeated=("repeated_text_score","mean"),
    urls=("url_count","sum")
).reset_index()
agg["campaign_risk"] = (
    0.35*agg.avg_score + 0.25*agg.spam_rate +
    0.15*(agg.recipients.rank(pct=True)) +
    0.15*(agg.reports.rank(pct=True)) +
    0.10*(agg.repeated.rank(pct=True))
)

c1,c2,c3,c4 = st.columns(4)
c1.metric("High-risk senders", int((agg.campaign_risk>=0.75).sum()))
c2.metric("Max recipient fan-out", int(agg.recipients.max()))
c3.metric("Campaign-like senders", int(((agg.recipients>=20)&(agg.repeated>=0.45)).sum()))
c4.metric("Top campaign risk", f"{agg.campaign_risk.max():.2f}")

left,right = st.columns(2)
with left:
    st.subheader("Campaign risk vs fan-out")
    st.scatter_chart(agg, x="recipients", y="campaign_risk", size="messages")
with right:
    st.subheader("Top coordinated-abuse candidates")
    st.dataframe(agg.sort_values("campaign_risk", ascending=False).head(20), use_container_width=True, hide_index=True)

st.subheader("Graph summary")
edges = df.groupby(["sender_id","receiver_id"]).size().reset_index(name="messages")
g = nx.from_pandas_edgelist(edges.head(10000), "sender_id", "receiver_id", edge_attr="messages", create_using=nx.DiGraph())
summary = pd.DataFrame([
    {"metric":"Nodes", "value":g.number_of_nodes()},
    {"metric":"Edges", "value":g.number_of_edges()},
    {"metric":"Weakly connected components", "value":nx.number_weakly_connected_components(g)},
    {"metric":"Largest component nodes", "value":max((len(c) for c in nx.weakly_connected_components(g)), default=0)},
])
st.dataframe(summary, use_container_width=True, hide_index=True)

st.info("Production extension: connect shared URLs/domains/business IDs and use community detection to identify coordinated phishing or spam campaigns across multiple senders.")
