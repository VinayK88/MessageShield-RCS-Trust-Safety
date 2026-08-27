from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "src"))
from abuse_intelligence import enrich_messages
from enforcement import apply_enforcement

st.set_page_config(page_title="AI Abuse Intelligence", page_icon="🤖", layout="wide")
st.title("🤖 AI Abuse Intelligence")
st.caption("Explainable abuse taxonomy + confidence + recommended enforcement")

path = ROOT / "outputs" / "scored_messages.csv"
if not path.exists():
    st.warning("Run `python src/run_pipeline.py --rows 30000` first.")
    st.stop()

df = pd.read_csv(path)
df = apply_enforcement(enrich_messages(df))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Phishing", f"{(df.abuse_label=='phishing').mean():.1%}")
c2.metric("Scam", f"{(df.abuse_label=='scam').mean():.1%}")
c3.metric("High-confidence AI labels", f"{(df.ai_confidence>=0.8).mean():.1%}")
c4.metric("Block / quarantine", f"{df.recommended_action.isin(['BLOCK','QUARANTINE']).mean():.1%}")

left, right = st.columns([1, 1])
with left:
    st.subheader("Abuse taxonomy")
    st.bar_chart(df.abuse_label.value_counts())
with right:
    st.subheader("Enforcement recommendations")
    st.bar_chart(df.recommended_action.value_counts())

st.subheader("Analyst review queue")
cols = ["message_id","sender_id","text","spam_score","abuse_label","ai_confidence","ai_explanation","prior_reports","unique_recipients_24h","recommended_action"]
st.dataframe(df.sort_values(["spam_score","ai_confidence"], ascending=False)[cols].head(100), use_container_width=True, hide_index=True)
