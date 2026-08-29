from pathlib import Path
import sys
import pandas as pd
import streamlit as st
from dashboard.apple_theme import apply_theme, page_header, section
ROOT=Path(__file__).resolve().parents[2]; sys.path.append(str(ROOT/"src"))
from abuse_intelligence import enrich_messages
from enforcement import apply_enforcement
st.set_page_config(page_title="Policy Decision Simulator",page_icon="🎯",layout="wide"); apply_theme(); page_header("MessageShield · Policy Decisioning","Prediction is evidence. Policy decides the intervention.","A proportional action ladder turns synthetic messaging risk into allow, review, rate-limit, warn, quarantine, or block decisions while keeping user friction visible.")
path=ROOT/"outputs"/"scored_messages.csv"
if not path.exists(): st.warning("Run `python src/run_pipeline.py --rows 30000` first."); st.stop()
df=apply_enforcement(enrich_messages(pd.read_csv(path))); order=["ALLOW","HUMAN_REVIEW","RATE_LIMIT","WARN","QUARANTINE","BLOCK"]; counts=df.recommended_action.value_counts().reindex(order,fill_value=0)
metrics=[(a.replace('_',' ').title(),f"{counts[a]:,}") for a in order]+[("Messages",f"{len(df):,}"),("Intervention rate",f"{1-counts['ALLOW']/max(len(df),1):.1%}"),("Hard action rate",f"{(counts['QUARANTINE']+counts['BLOCK'])/max(len(df),1):.1%}"),("Human review rate",f"{counts['HUMAN_REVIEW']/max(len(df),1):.1%}"),("Mean risk",f"{df.spam_score.mean():.3f}"),("Mean AI confidence",f"{df.ai_confidence.mean():.2f}")]
for s in range(0,len(metrics),6):
    cols=st.columns(6)
    for c,(l,v) in zip(cols,metrics[s:s+6]): c.metric(l,v)
section("Policy ladder","Each action has a different user-friction and safety objective; the model score alone does not choose policy."); policy=pd.DataFrame([{"action":"ALLOW","goal":"Preserve legitimate communication","example condition":"Low model risk"},{"action":"HUMAN_REVIEW","goal":"Resolve uncertainty","example condition":"Borderline score / ambiguous evidence"},{"action":"RATE_LIMIT","goal":"Reduce potential blast radius","example condition":"Moderate risk + high fan-out"},{"action":"WARN","goal":"Add user friction","example condition":"High-confidence unwanted traffic"},{"action":"QUARANTINE","goal":"Hold delivery for review","example condition":"Very high model risk"},{"action":"BLOCK","goal":"Stop severe abuse","example condition":"Extreme risk + reports/fan-out/phishing"}]); st.dataframe(policy,use_container_width=True,hide_index=True)
left,right=st.columns(2,gap="large")
with left: section("Decision mix","How the synthetic population is distributed across proportional interventions."); st.bar_chart(counts)
with right: section("Average risk by action","Higher-friction actions should generally correspond to stronger combined evidence."); st.bar_chart(df.groupby("recommended_action").spam_score.mean().reindex(order))
section("Decision review queue","Highest-risk items with taxonomy, confidence, reports, reach, action, and explanation."); show=["message_id","sender_id","abuse_label","spam_score","ai_confidence","prior_reports","unique_recipients_24h","recommended_action","ai_explanation"]; st.dataframe(df.sort_values("spam_score",ascending=False)[show].head(100),use_container_width=True,hide_index=True)
st.caption("Portfolio simulation only. Production policy would include calibrated segment thresholds, human review, appeals, policy/legal constraints, and continuous feedback.")
