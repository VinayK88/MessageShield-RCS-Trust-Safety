from pathlib import Path
import pandas as pd
import networkx as nx
import streamlit as st
from dashboard.apple_theme import apply_theme, page_header, section
ROOT=Path(__file__).resolve().parents[2]
st.set_page_config(page_title="Campaign Graph",page_icon="🕸️",layout="wide"); apply_theme(); page_header("MessageShield · Campaign Graph","Find the structure behind coordinated abuse.","Sender-to-recipient relationships, fan-out, repeated behavior, campaign risk, and graph connectivity for synthetic coordinated-abuse review.")
path=ROOT/"outputs"/"scored_messages.csv"
if not path.exists(): st.warning("Run `python src/run_pipeline.py --rows 30000` first."); st.stop()
df=pd.read_csv(path)
agg=df.groupby("sender_id").agg(messages=("message_id","count"),recipients=("receiver_id","nunique"),spam_rate=("is_spam","mean"),avg_score=("spam_score","mean"),reports=("prior_reports","sum"),repeated=("repeated_text_score","mean"),urls=("url_count","sum")).reset_index(); agg["campaign_risk"]=0.35*agg.avg_score+0.25*agg.spam_rate+0.15*agg.recipients.rank(pct=True)+0.15*agg.reports.rank(pct=True)+0.10*agg.repeated.rank(pct=True)
edges=df.groupby(["sender_id","receiver_id"]).size().reset_index(name="messages"); g=nx.from_pandas_edgelist(edges.head(10000),"sender_id","receiver_id",edge_attr="messages",create_using=nx.DiGraph()); comps=list(nx.weakly_connected_components(g))
metrics=[("Senders",f"{len(agg):,}"),("High-risk senders",f"{(agg.campaign_risk>=.75).sum():,}"),("Campaign-like",f"{((agg.recipients>=20)&(agg.repeated>=.45)).sum():,}"),("Top campaign risk",f"{agg.campaign_risk.max():.2f}"),("Max fan-out",f"{agg.recipients.max():.0f}"),("Mean fan-out",f"{agg.recipients.mean():.1f}"),("Graph nodes",f"{g.number_of_nodes():,}"),("Graph edges",f"{g.number_of_edges():,}"),("Components",len(comps)),("Largest component",max((len(c) for c in comps),default=0)),("URL-bearing senders",f"{(agg.urls>0).sum():,}"),("Reported senders",f"{(agg.reports>0).sum():,}")]
for s in range(0,len(metrics),4):
    cols=st.columns(4)
    for c,(l,v) in zip(cols,metrics[s:s+4]): c.metric(l,v)
left,right=st.columns(2,gap="large")
with left: section("Campaign risk vs fan-out","High reach becomes more meaningful when paired with repeated content, reports, and model risk."); st.scatter_chart(agg,x="recipients",y="campaign_risk",size="messages")
with right: section("Top coordinated-abuse candidates","Highest synthetic sender-level campaign risk for analyst review."); st.dataframe(agg.sort_values("campaign_risk",ascending=False).head(20),use_container_width=True,hide_index=True)
section("Graph summary","Connectivity provides campaign context without claiming actor identity or intent."); summary=pd.DataFrame([{"metric":"Nodes","value":g.number_of_nodes()},{"metric":"Edges","value":g.number_of_edges()},{"metric":"Weakly connected components","value":len(comps)},{"metric":"Largest component nodes","value":max((len(c) for c in comps),default=0)}]); st.dataframe(summary,use_container_width=True,hide_index=True)
st.info("Production extension: connect shared URLs/domains/business IDs and use governed community detection for multi-sender campaign review.")
