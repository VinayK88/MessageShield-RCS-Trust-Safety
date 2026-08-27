from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
st.set_page_config(page_title="Abuse Network", page_icon="🕸️", layout="wide")
st.title("🕸️ Abuse Network & Sender Behavior")
st.caption("Explore high-fanout senders, repeated-message behavior, reports, and campaign-like activity.")

try:
    df = pd.read_csv(OUT / "scored_messages.csv")
except FileNotFoundError:
    st.warning("Run the pipeline first: `python src/run_pipeline.py --rows 30000`")
    st.stop()

sender = df.groupby("sender_id").agg(
    messages=("message_id","count"),
    unique_recipients=("receiver_id","nunique"),
    mean_spam_score=("spam_score","mean"),
    max_spam_score=("spam_score","max"),
    prior_reports=("prior_reports","max"),
    repeated_text_score=("repeated_text_score","mean"),
    url_count=("url_count","sum"),
    spam_rate=("is_spam","mean"),
).reset_index()

c1,c2,c3,c4=st.columns(4)
c1.metric("Observed senders", f"{len(sender):,}")
c2.metric("High-risk senders", f"{(sender.mean_spam_score>.7).sum():,}")
c3.metric("Median recipients/sender", f"{sender.unique_recipients.median():.0f}")
c4.metric("Reported senders", f"{(sender.prior_reports>0).sum():,}")

st.subheader("Risk vs recipient fan-out")
st.scatter_chart(sender, x="unique_recipients", y="mean_spam_score", size="messages")

st.subheader("Campaign investigation queue")
risk = sender.assign(
    campaign_risk=(sender.mean_spam_score*.45 + sender.spam_rate*.25 + (sender.prior_reports.clip(0,5)/5)*.15 + sender.repeated_text_score*.15)
).sort_values("campaign_risk", ascending=False)
st.dataframe(risk.head(50), use_container_width=True, hide_index=True)

st.subheader("Top sender activity")
metric = st.selectbox("Rank senders by", ["campaign_risk","mean_spam_score","unique_recipients","messages","prior_reports"])
st.bar_chart(risk.nlargest(20, metric).set_index("sender_id")[[metric]])
