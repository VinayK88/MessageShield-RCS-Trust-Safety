from pathlib import Path
import sys
import pandas as pd
import streamlit as st
from dashboard.apple_theme import apply_theme, page_header, section
ROOT=Path(__file__).resolve().parents[2]; sys.path.append(str(ROOT/"src"))
from abuse_intelligence import enrich_messages
from enforcement import apply_enforcement
st.set_page_config(page_title="AI Abuse Intelligence",page_icon="🤖",layout="wide"); apply_theme(); page_header("MessageShield · AI Abuse Intelligence","Turn model risk into explainable abuse context.","An abuse taxonomy, confidence, evidence strings, and proportional enforcement recommendations make every high-risk item easier to inspect.")
path=ROOT/"outputs"/"scored_messages.csv"
if not path.exists(): st.warning("Run `python src/run_pipeline.py --rows 30000` first."); st.stop()
df=apply_enforcement(enrich_messages(pd.read_csv(path)))
labels=df.abuse_label.value_counts(); actions=df.recommended_action.value_counts(); high_conf=(df.ai_confidence>=.8); high_risk=(df.spam_score>=.9)
metrics=[("Messages",f"{len(df):,}"),("Phishing",f"{(df.abuse_label=='phishing').mean():.1%}"),("Scam",f"{(df.abuse_label=='scam').mean():.1%}"),("Impersonation",f"{(df.abuse_label=='impersonation').mean():.1%}"),("Malware",f"{(df.abuse_label=='malware').mean():.1%}"),("Spam",f"{(df.abuse_label=='spam').mean():.1%}"),("High-confidence labels",f"{high_conf.mean():.1%}"),("Mean AI confidence",f"{df.ai_confidence.mean():.2f}"),("High-risk messages",f"{high_risk.sum():,}"),("Block",f"{actions.get('BLOCK',0):,}"),("Quarantine",f"{actions.get('QUARANTINE',0):,}"),("Block / quarantine",f"{df.recommended_action.isin(['BLOCK','QUARANTINE']).mean():.1%}")]
for s in range(0,len(metrics),4):
    cols=st.columns(4)
    for c,(l,v) in zip(cols,metrics[s:s+4]): c.metric(l,v)
left,right=st.columns(2,gap="large")
with left: section("Abuse taxonomy","Distribution of explainable synthetic abuse labels."); st.bar_chart(labels)
with right: section("Enforcement recommendations","Prediction remains separate from the proportional product action."); st.bar_chart(actions)
section("Analyst review queue","Highest-risk messages with model score, taxonomy, confidence, explanation, reports, reach, and recommended action."); cols=["message_id","sender_id","text","spam_score","abuse_label","ai_confidence","ai_explanation","prior_reports","unique_recipients_24h","recommended_action"]; st.dataframe(df.sort_values(["spam_score","ai_confidence"],ascending=False)[cols].head(100),use_container_width=True,hide_index=True)
