from pathlib import Path
import pandas as pd
import streamlit as st
from dashboard.apple_theme import apply_theme, page_header, section
ROOT=Path(__file__).resolve().parents[2]
st.set_page_config(page_title="Global Abuse Intelligence",page_icon="🌍",layout="wide"); apply_theme(); page_header("MessageShield · Global Abuse Intelligence","Understand where abuse pressure is changing.","Market-tier and P2P-vs-RBM segmentation for prevalence, model risk, reports, click behavior, and emerging abuse vectors.")
path=ROOT/"outputs"/"scored_messages.csv"
if not path.exists(): st.warning("Run `python src/run_pipeline.py --rows 30000` first."); st.stop()
df=pd.read_csv(path); regions=pd.cut(df.country_risk,bins=[-0.01,.15,.30,.50,1.0],labels=["Low-risk markets","Moderate-risk markets","Elevated-risk markets","High-risk markets"]); df["risk_region"]=regions.astype(str); df["channel"]=df.business_sender.map({1:"RBM",0:"P2P"})
g=df.groupby(["risk_region","channel"],observed=False).agg(messages=("message_id","count"),spam_prevalence=("is_spam","mean"),avg_score=("spam_score","mean"),reports=("prior_reports","mean"),click_rate=("clicked","mean")).reset_index()
metrics=[("Messages",f"{len(df):,}"),("Highest regional prevalence",f"{g.spam_prevalence.max():.1%}"),("RBM prevalence",f"{df.loc[df.channel=='RBM','is_spam'].mean():.1%}"),("P2P prevalence",f"{df.loc[df.channel=='P2P','is_spam'].mean():.1%}"),("High-risk market share",f"{(df.risk_region=='High-risk markets').mean():.1%}"),("RBM share",f"{(df.channel=='RBM').mean():.1%}"),("P2P share",f"{(df.channel=='P2P').mean():.1%}"),("Mean country risk",f"{df.country_risk.mean():.2f}"),("Mean model score",f"{df.spam_score.mean():.3f}"),("Reported traffic",f"{(df.prior_reports>0).mean():.1%}"),("Overall click rate",f"{df.clicked.mean():.1%}"),("Market tiers",df.risk_region.nunique())]
for s in range(0,len(metrics),4):
    cols=st.columns(4)
    for c,(l,v) in zip(cols,metrics[s:s+4]): c.metric(l,v)
left,right=st.columns(2,gap="large")
with left: section("Spam prevalence by market tier","Compare P2P and RBM pressure across synthetic market-risk bands."); st.bar_chart(g.pivot(index="risk_region",columns="channel",values="spam_prevalence"))
with right: section("Average model score by market tier","Model-risk movement can be compared with observed synthetic prevalence."); st.bar_chart(g.groupby("risk_region",observed=False).avg_score.mean())
section("Emerging abuse vectors","Operational hypotheses for review, not automatic claims about real markets."); alerts=pd.DataFrame([{"severity":"CRITICAL","vector":"High-risk-market phishing","signal":"Prevalence > ecosystem baseline","recommended_action":"Tighten warning + quarantine thresholds"},{"severity":"WARNING","vector":"High fan-out P2P senders","signal":"Recipient fan-out + repeated text","recommended_action":"Rate-limit and graph-cluster"},{"severity":"WATCH","vector":"RBM complaint growth","signal":"Prior reports / sender rising","recommended_action":"Review business verification signals"}]); st.dataframe(alerts,use_container_width=True,hide_index=True)
section("Regional operating table","Synthetic market-tier statistics for analyst comparison."); st.dataframe(g.sort_values("spam_prevalence",ascending=False),use_container_width=True,hide_index=True)
