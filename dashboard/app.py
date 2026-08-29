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
    .block-container { max-width: 1450px; padding-top: 2.4rem; padding-bottom: 4rem; }
    h1, h2, h3 { letter-spacing: -0.035em; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Arial, sans-serif; }
    p, label, .stCaption { color: #6e6e73 !important; }
    [data-testid="stSidebar"] { background: rgba(245,245,247,.97); border-right: 1px solid #e8e8ed; }
    [data-testid="stMetric"] {
        background: #f5f5f7;
        border: 1px solid #ececf0;
        border-radius: 24px;
        padding: 1.15rem 1.2rem;
        box-shadow: 0 8px 28px rgba(0,0,0,.028);
        min-height: 118px;
    }
    [data-testid="stMetricLabel"] { font-size: .75rem; color: #6e6e73; font-weight: 600; letter-spacing: .01em; }
    [data-testid="stMetricValue"] { font-size: 1.9rem; color: #1d1d1f; letter-spacing: -.04em; font-weight: 650; }
    [data-testid="stMetricDelta"] { font-size: .72rem; }
    [data-testid="stDataFrame"] { border: 1px solid #ececf0; border-radius: 20px; overflow: hidden; }
    .apple-eyebrow { color:#0071e3; font-size:.76rem; font-weight:700; letter-spacing:.10em; text-transform:uppercase; margin-bottom:.6rem; }
    .apple-hero { font-size:3.65rem; line-height:1.02; font-weight:650; letter-spacing:-.058em; color:#1d1d1f; margin:0; }
    .apple-subtitle { font-size:1.14rem; line-height:1.55; max-width:920px; color:#6e6e73; margin-top:.9rem; }
    .apple-chip { display:inline-block; background:#f5f5f7; color:#424245; border-radius:999px; padding:.42rem .78rem; font-size:.74rem; margin:.3rem .32rem .1rem 0; border:1px solid #ececf0; }
    .apple-section-title { font-size:1.5rem; font-weight:650; letter-spacing:-.03em; color:#1d1d1f; margin-bottom:.18rem; }
    .apple-section-sub { color:#86868b; font-size:.9rem; margin-bottom:1rem; }
    .kpi-band { margin-top:1.5rem; margin-bottom:.25rem; }
    hr { border-color:#eeeeef !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="apple-eyebrow">MessageShield · Trust & Safety</div>', unsafe_allow_html=True)
st.markdown('<div class="apple-hero">A clearer view of messaging risk.</div>', unsafe_allow_html=True)
st.markdown('<div class="apple-subtitle">Monitor abuse prevalence, detection quality, user impact, and enforcement health across a synthetic RCS/RBM ecosystem—without losing sight of legitimate communication.</div>', unsafe_allow_html=True)
st.markdown('<span class="apple-chip">RCS / RBM</span><span class="apple-chip">AI abuse intelligence</span><span class="apple-chip">≤2% FPR guardrail</span><span class="apple-chip">A/B + counterfactual</span><span class="apple-chip">Policy decisioning</span>', unsafe_allow_html=True)

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
ab = summary["ab_test"]
threshold = ev["threshold"]
flagged = scored["spam_score"] >= threshold
enforcement_rate = float(flagged.mean())
high_risk_mask = scored["spam_score"] >= 0.90
high_risk_rate = float(high_risk_mask.mean())
avg_reports = float(scored["prior_reports"].mean())
avg_reach = float(scored["unique_recipients_24h"].mean())
warning_effect = float(ab["absolute_lift"])
total_messages = len(scored)
flagged_count = int(flagged.sum())
high_risk_count = int(high_risk_mask.sum())
reported_rate = float((scored["prior_reports"] > 0).mean())
url_rate = float((scored["url_count"] > 0).mean())
senders = int(scored["sender_id"].nunique())
receivers = int(scored["receiver_id"].nunique())
mean_score = float(scored["spam_score"].mean())
p95_velocity = float(scored["messages_24h"].quantile(.95))
p95_reach = float(scored["unique_recipients_24h"].quantile(.95))

st.markdown('<div class="kpi-band"></div>', unsafe_allow_html=True)
kpi_rows = [
    [("Abuse prevalence",f"{ev['spam_prevalence']:.1%}"),("Detection recall",f"{ev['recall']:.1%}"),("Precision",f"{ev['precision']:.1%}"),("False-positive rate",f"{ev['false_positive_rate']:.2%}"),("PR-AUC",f"{ev['pr_auc']:.3f}")],
    [("Messages",f"{total_messages:,}"),("Flagged",f"{flagged_count:,}"),("High-risk",f"{high_risk_count:,}"),("Enforcement rate",f"{enforcement_rate:.1%}"),("High-risk traffic",f"{high_risk_rate:.1%}")],
    [("Senders",f"{senders:,}"),("Receivers",f"{receivers:,}"),("Reported traffic",f"{reported_rate:.1%}"),("URL-bearing",f"{url_rate:.1%}"),("Mean risk score",f"{mean_score:.3f}")],
    [("Avg reports / msg",f"{avg_reports:.2f}"),("Avg recipient reach",f"{avg_reach:.1f}"),("P95 velocity",f"{p95_velocity:.0f}"),("P95 reach",f"{p95_reach:.0f}"),("Warning UI effect",f"{warning_effect:+.2%}")],
]
for row in kpi_rows:
    cols=st.columns(5)
    for col,(label,value) in zip(cols,row): col.metric(label,value)

st.write("")
st.divider()
left, right = st.columns([1.05, .95], gap="large")
with left:
    st.markdown('<div class="apple-section-title">Risk score distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="apple-section-sub">How confidently the model separates legitimate from abusive traffic.</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.hist(scored.loc[scored.is_spam == 0, "spam_score"], bins=40, alpha=.62, label="Legitimate")
    ax.hist(scored.loc[scored.is_spam == 1, "spam_score"], bins=40, alpha=.62, label="Spam / abuse")
    ax.axvline(threshold, linestyle="--", linewidth=1.5, label="Operating threshold")
    ax.set_xlabel("Risk score")
    ax.set_ylabel("Messages")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_alpha(.18)
    ax.grid(axis="y", alpha=.10)
    ax.legend(frameon=False)
    st.pyplot(fig, use_container_width=True)

with right:
    st.markdown('<div class="apple-section-title">User-impact intervention</div>', unsafe_allow_html=True)
    st.markdown('<div class="apple-section-sub">Does a warning UI reduce risky click-through without excessive friction?</div>', unsafe_allow_html=True)
    chart = pd.DataFrame({
        "experience": ["Control", "Warning UI"],
        "click_through_rate": [ab["control_ctr"], ab["treatment_ctr"]],
    }).set_index("experience")
    st.bar_chart(chart, height=310)
    a, b, c = st.columns(3)
    a.metric("Absolute CTR change", f"{ab['absolute_lift']:+.2%}")
    b.metric("Relative lift", f"{ab['relative_lift']:+.1%}")
    c.metric("p-value", f"{ab['p_value']:.3g}")

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
