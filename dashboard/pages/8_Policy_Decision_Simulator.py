from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "src"))
from abuse_intelligence import enrich_messages
from enforcement import apply_enforcement

st.set_page_config(page_title="Policy Decision Simulator", page_icon="🎯", layout="wide")
st.title("🎯 Trust & Safety Policy Decision Simulator")
st.caption("Map model risk into proportional product actions for a synthetic messaging ecosystem")

path = ROOT / "outputs" / "scored_messages.csv"
if not path.exists():
    st.warning("Run `python src/run_pipeline.py --rows 30000` first.")
    st.stop()

df = apply_enforcement(enrich_messages(pd.read_csv(path)))
order = ["ALLOW","HUMAN_REVIEW","RATE_LIMIT","WARN","QUARANTINE","BLOCK"]
counts = df.recommended_action.value_counts().reindex(order, fill_value=0)

cols = st.columns(6)
for col, action in zip(cols, order):
    col.metric(action.replace("_"," ").title(), f"{counts[action]:,}")

st.subheader("Policy ladder")
policy = pd.DataFrame([
    {"action":"ALLOW","goal":"Preserve legitimate communication","example condition":"Low model risk"},
    {"action":"HUMAN_REVIEW","goal":"Resolve uncertainty","example condition":"Borderline score / ambiguous evidence"},
    {"action":"RATE_LIMIT","goal":"Reduce potential blast radius","example condition":"Moderate risk + high fan-out"},
    {"action":"WARN","goal":"Add user friction","example condition":"High-confidence unwanted traffic"},
    {"action":"QUARANTINE","goal":"Hold delivery for review","example condition":"Very high model risk"},
    {"action":"BLOCK","goal":"Stop severe abuse","example condition":"Extreme risk + reports/fan-out/phishing"},
])
st.dataframe(policy, use_container_width=True, hide_index=True)

left,right = st.columns(2)
with left:
    st.subheader("Decision mix")
    st.bar_chart(counts)
with right:
    st.subheader("Average risk score by action")
    st.bar_chart(df.groupby("recommended_action").spam_score.mean().reindex(order))

st.subheader("Decision review queue")
show = ["message_id","sender_id","abuse_label","spam_score","ai_confidence","prior_reports","unique_recipients_24h","recommended_action","ai_explanation"]
st.dataframe(df.sort_values("spam_score", ascending=False)[show].head(100), use_container_width=True, hide_index=True)

st.caption("Portfolio simulation only. A production policy system would include calibrated segment thresholds, human review, appeals, legal/policy constraints, and continuous feedback.")
