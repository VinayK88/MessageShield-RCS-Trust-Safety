from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

st.set_page_config(page_title="MessageShield", page_icon="🛡️", layout="wide")
st.title("🛡️ MessageShield — RCS Trust & Safety Command Center")
st.caption("Executive view of abuse prevalence, enforcement quality, user impact, and model health.")

@st.cache_data
def load_data():
    scored = pd.read_csv(OUT / "scored_messages.csv")
    metrics = pd.read_csv(OUT / "ecosystem_metrics.csv")
    summary = json.loads((OUT / "summary.json").read_text())
    return scored, metrics, summary

try:
    scored, metrics, summary = load_data()
except FileNotFoundError:
    st.warning("Run `python src/run_pipeline.py --rows 30000` first to generate dashboard data.")
    st.stop()

ev = summary["model_evaluation"]
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Spam prevalence", f"{ev['spam_prevalence']:.1%}")
col2.metric("Recall", f"{ev['recall']:.1%}")
col3.metric("Precision", f"{ev['precision']:.1%}")
col4.metric("False-positive rate", f"{ev['false_positive_rate']:.2%}")
col5.metric("PR-AUC", f"{ev['pr_auc']:.3f}")

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Spam score distribution")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(scored.loc[scored.is_spam == 0, "spam_score"], bins=40, alpha=.65, label="Legitimate")
    ax.hist(scored.loc[scored.is_spam == 1, "spam_score"], bins=40, alpha=.65, label="Spam")
    ax.axvline(ev["threshold"], linestyle="--", label="Operating threshold")
    ax.set_xlabel("Spam score")
    ax.set_ylabel("Messages")
    ax.legend()
    st.pyplot(fig)

with right:
    st.subheader("User-impact intervention")
    ab = summary["ab_test"]
    chart = pd.DataFrame({
        "experience": ["Control", "Warning UI"],
        "click_through_rate": [ab["control_ctr"], ab["treatment_ctr"]],
    }).set_index("experience")
    st.bar_chart(chart)
    st.metric("Absolute CTR change", f"{ab['absolute_lift']:+.2%}")
    st.caption(f"Two-proportion z-test p-value: {ab['p_value']:.3g}")

st.subheader("High-risk message investigation queue")
show = scored.sort_values("spam_score", ascending=False).head(25)
cols = ["message_id", "sender_id", "receiver_id", "spam_score", "prior_reports", "messages_24h", "unique_recipients_24h", "url_count", "text"]
st.dataframe(show[cols], use_container_width=True, hide_index=True)

st.subheader("Monitoring snapshot")
st.dataframe(metrics.tail(24), use_container_width=True, hide_index=True)
