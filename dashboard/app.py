from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

st.set_page_config(page_title="MessageShield", page_icon="🛡️", layout="wide")

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
        color: #1d1d1f;
    }
    .stApp { background: #ffffff; }
    .block-container { max-width: 1380px; padding-top: 2.1rem; padding-bottom: 4rem; }
    h1, h2, h3 { letter-spacing: -0.03em; }
    h1 { font-size: 3rem !important; font-weight: 700 !important; }
    h2 { font-weight: 650 !important; }
    p, label, .stCaption { color: #6e6e73 !important; }
    [data-testid="stSidebar"] { background: rgba(245,245,247,.96); border-right: 1px solid #e8e8ed; }
    [data-testid="stMetric"] {
        background: #f5f5f7;
        border: 1px solid #ececf0;
        border-radius: 22px;
        padding: 1.25rem 1.3rem;
        box-shadow: 0 8px 28px rgba(0,0,0,.035);
    }
    [data-testid="stMetricLabel"] { font-size: .80rem; color: #6e6e73; }
    [data-testid="stMetricValue"] { font-size: 2.05rem; color: #1d1d1f; letter-spacing: -.03em; }
    [data-testid="stDataFrame"] { border: 1px solid #ececf0; border-radius: 18px; overflow: hidden; }
    div[data-testid="stVerticalBlockBorderWrapper"] { border-color: #ececf0 !important; border-radius: 24px !important; }
    .apple-eyebrow { color:#0071e3; font-size:.78rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; margin-bottom:.45rem; }
    .apple-hero { font-size:3.25rem; line-height:1.02; font-weight:700; letter-spacing:-.055em; color:#1d1d1f; margin:0; }
    .apple-subtitle { font-size:1.15rem; line-height:1.5; max-width:860px; color:#6e6e73; margin-top:.85rem; }
    .apple-chip { display:inline-block; background:#f5f5f7; color:#424245; border-radius:999px; padding:.38rem .72rem; font-size:.76rem; margin:.25rem .3rem .1rem 0; border:1px solid #ececf0; }
    .apple-section-title { font-size:1.55rem; font-weight:650; letter-spacing:-.035em; color:#1d1d1f; margin-bottom:.2rem; }
    .apple-section-sub { color:#86868b; font-size:.92rem; margin-bottom:1rem; }
    hr { border-color:#eeeeef !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="apple-eyebrow">MessageShield · Trust & Safety</div>', unsafe_allow_html=True)
st.markdown('<div class="apple-hero">A clearer view of messaging risk.</div>', unsafe_allow_html=True)
st.markdown('<div class="apple-subtitle">Monitor abuse prevalence, model quality, user impact, and enforcement health across a synthetic RCS/RBM ecosystem—without losing sight of legitimate communication.</div>', unsafe_allow_html=True)
st.markdown('<span class="apple-chip">RCS / RBM</span><span class="apple-chip">AI abuse intelligence</span><span class="apple-chip">≤2% FPR guardrail</span><span class="apple-chip">A/B + counterfactual</span>', unsafe_allow_html=True)

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
st.write("")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Abuse prevalence", f"{ev['spam_prevalence']:.1%}")
col2.metric("Detection recall", f"{ev['recall']:.1%}")
col3.metric("Precision", f"{ev['precision']:.1%}")
col4.metric("False-positive rate", f"{ev['false_positive_rate']:.2%}")
col5.metric("PR-AUC", f"{ev['pr_auc']:.3f}")

st.write("")
st.divider()
left, right = st.columns([1.05, .95], gap="large")
with left:
    st.markdown('<div class="apple-section-title">Risk score distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="apple-section-sub">How confidently the model separates legitimate from abusive traffic.</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.hist(scored.loc[scored.is_spam == 0, "spam_score"], bins=40, alpha=.65, label="Legitimate")
    ax.hist(scored.loc[scored.is_spam == 1, "spam_score"], bins=40, alpha=.65, label="Spam / abuse")
    ax.axvline(ev["threshold"], linestyle="--", linewidth=1.5, label="Operating threshold")
    ax.set_xlabel("Risk score")
    ax.set_ylabel("Messages")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_alpha(.18)
    ax.grid(axis="y", alpha=.12)
    ax.legend(frameon=False)
    st.pyplot(fig, use_container_width=True)

with right:
    st.markdown('<div class="apple-section-title">User-impact intervention</div>', unsafe_allow_html=True)
    st.markdown('<div class="apple-section-sub">Does a warning UI reduce risky click-through without excessive friction?</div>', unsafe_allow_html=True)
    ab = summary["ab_test"]
    chart = pd.DataFrame({
        "experience": ["Control", "Warning UI"],
        "click_through_rate": [ab["control_ctr"], ab["treatment_ctr"]],
    }).set_index("experience")
    st.bar_chart(chart, height=310)
    a, b = st.columns(2)
    a.metric("Absolute CTR change", f"{ab['absolute_lift']:+.2%}")
    b.metric("Experiment p-value", f"{ab['p_value']:.3g}")

st.write("")
st.markdown('<div class="apple-section-title">Priority investigations</div>', unsafe_allow_html=True)
st.markdown('<div class="apple-section-sub">Highest-risk messages ranked for analyst review using score, reports, velocity, reach, URLs, and content evidence.</div>', unsafe_allow_html=True)
show = scored.sort_values("spam_score", ascending=False).head(25)
cols = ["message_id", "sender_id", "receiver_id", "spam_score", "prior_reports", "messages_24h", "unique_recipients_24h", "url_count", "text"]
st.dataframe(show[cols], use_container_width=True, hide_index=True)

st.write("")
st.markdown('<div class="apple-section-title">Ecosystem monitoring</div>', unsafe_allow_html=True)
st.markdown('<div class="apple-section-sub">Latest operational windows for prevalence, enforcement, model quality, and user behavior.</div>', unsafe_allow_html=True)
st.dataframe(metrics.tail(24), use_container_width=True, hide_index=True)
