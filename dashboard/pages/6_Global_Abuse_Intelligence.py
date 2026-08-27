from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
st.set_page_config(page_title="Global Abuse Intelligence", page_icon="🌍", layout="wide")
st.title("🌍 Global Abuse Intelligence")
st.caption("Regional abuse prevalence, intervention efficacy, and emerging vectors")

path = ROOT / "outputs" / "scored_messages.csv"
if not path.exists():
    st.warning("Run `python src/run_pipeline.py --rows 30000` first.")
    st.stop()

df = pd.read_csv(path)
regions = pd.cut(df.country_risk, bins=[-0.01,.15,.30,.50,1.0], labels=["Low-risk markets","Moderate-risk markets","Elevated-risk markets","High-risk markets"])
df["risk_region"] = regions.astype(str)
df["channel"] = df.business_sender.map({1:"RBM",0:"P2P"})

g = df.groupby(["risk_region","channel"], observed=False).agg(
    messages=("message_id","count"),
    spam_prevalence=("is_spam","mean"),
    avg_score=("spam_score","mean"),
    reports=("prior_reports","mean"),
    click_rate=("clicked","mean")
).reset_index()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Highest regional prevalence", f"{g.spam_prevalence.max():.1%}")
c2.metric("RBM spam prevalence", f"{df.loc[df.channel=='RBM','is_spam'].mean():.1%}")
c3.metric("P2P spam prevalence", f"{df.loc[df.channel=='P2P','is_spam'].mean():.1%}")
c4.metric("High-risk market share", f"{(df.risk_region=='High-risk markets').mean():.1%}")

left,right = st.columns(2)
with left:
    st.subheader("Spam prevalence by market tier")
    pivot = g.pivot(index="risk_region", columns="channel", values="spam_prevalence")
    st.bar_chart(pivot)
with right:
    st.subheader("Average model score by market tier")
    st.bar_chart(g.groupby("risk_region", observed=False).avg_score.mean())

st.subheader("Emerging abuse vectors")
alerts = pd.DataFrame([
    {"severity":"CRITICAL","vector":"High-risk-market phishing","signal":"Prevalence > ecosystem baseline","recommended_action":"Tighten warning + quarantine thresholds"},
    {"severity":"WARNING","vector":"High fan-out P2P senders","signal":"Recipient fan-out + repeated text","recommended_action":"Rate-limit and graph-cluster"},
    {"severity":"WATCH","vector":"RBM complaint growth","signal":"Prior reports / sender rising","recommended_action":"Review business verification signals"},
])
st.dataframe(alerts, use_container_width=True, hide_index=True)

st.subheader("Regional operating table")
st.dataframe(g.sort_values("spam_prevalence", ascending=False), use_container_width=True, hide_index=True)
