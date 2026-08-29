from pathlib import Path
import pandas as pd
import streamlit as st
from dashboard.apple_theme import apply_theme, page_header, section

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
st.set_page_config(page_title="Abuse Network", page_icon="🕸️", layout="wide")
apply_theme(); page_header("MessageShield · Abuse Network","See coordinated behavior, not just individual messages.","High-fanout senders, repeated-message behavior, reports, recipient reach, URLs, and campaign-like activity in one analyst surface.")
try: df = pd.read_csv(OUT / "scored_messages.csv")
except FileNotFoundError: st.warning("Run the pipeline first: `python src/run_pipeline.py --rows 30000`"); st.stop()

sender = df.groupby("sender_id").agg(messages=("message_id","count"),unique_recipients=("receiver_id","nunique"),mean_spam_score=("spam_score","mean"),max_spam_score=("spam_score","max"),prior_reports=("prior_reports","max"),repeated_text_score=("repeated_text_score","mean"),url_count=("url_count","sum"),spam_rate=("is_spam","mean")).reset_index()
risk=sender.assign(campaign_risk=(sender.mean_spam_score*.45+sender.spam_rate*.25+(sender.prior_reports.clip(0,5)/5)*.15+sender.repeated_text_score*.15)).sort_values("campaign_risk",ascending=False)
metrics=[("Observed senders",f"{len(sender):,}"),("High-risk senders",f"{(sender.mean_spam_score>.7).sum():,}"),("Reported senders",f"{(sender.prior_reports>0).sum():,}"),("URL senders",f"{(sender.url_count>0).sum():,}"),("Median recipients",f"{sender.unique_recipients.median():.0f}"),("P95 recipients",f"{sender.unique_recipients.quantile(.95):.0f}"),("Median messages",f"{sender.messages.median():.0f}"),("P95 messages",f"{sender.messages.quantile(.95):.0f}"),("Mean sender risk",f"{sender.mean_spam_score.mean():.3f}"),("Max sender risk",f"{sender.max_spam_score.max():.3f}"),("Campaign candidates",f"{(risk.campaign_risk>=.70).sum():,}"),("Mean repeat score",f"{sender.repeated_text_score.mean():.2f}")]
for start in range(0,len(metrics),4):
    cols=st.columns(4)
    for col,(label,value) in zip(cols,metrics[start:start+4]): col.metric(label,value)
section("Risk vs recipient fan-out","Large reach is useful context only when combined with model risk and other abuse evidence."); st.scatter_chart(sender,x="unique_recipients",y="mean_spam_score",size="messages")
section("Campaign investigation queue","Sender-level risk combines score, spam rate, reports, and repeated content."); st.dataframe(risk.head(50),use_container_width=True,hide_index=True)
section("Top sender activity","Rank the synthetic sender population by the signal most useful for the current investigation."); metric=st.selectbox("Rank senders by",["campaign_risk","mean_spam_score","unique_recipients","messages","prior_reports"]); st.bar_chart(risk.nlargest(20,metric).set_index("sender_id")[[metric]])
