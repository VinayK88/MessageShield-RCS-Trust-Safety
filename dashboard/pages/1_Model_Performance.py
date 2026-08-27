from pathlib import Path
import json
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, roc_curve

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
st.set_page_config(page_title="Model Performance", page_icon="📈", layout="wide")
st.title("📈 Detection Model Performance")
st.caption("Threshold selection, ranking quality, and false-positive guardrails.")

try:
    df = pd.read_csv(OUT / "scored_messages.csv")
    summary = json.loads((OUT / "summary.json").read_text())
except FileNotFoundError:
    st.warning("Run the pipeline first: `python src/run_pipeline.py --rows 30000`")
    st.stop()

ev = summary["model_evaluation"]
y = df.is_spam.to_numpy()
p = df.spam_score.to_numpy()

c1, c2, c3, c4 = st.columns(4)
c1.metric("ROC-AUC", f"{ev['roc_auc']:.3f}")
c2.metric("PR-AUC", f"{ev['pr_auc']:.3f}")
c3.metric("Threshold", f"{ev['threshold']:.3f}")
c4.metric("FPR guardrail", f"{ev['false_positive_rate']:.2%}")

left, right = st.columns(2)
with left:
    st.subheader("Precision–Recall curve")
    precision, recall, _ = precision_recall_curve(y, p)
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(recall, precision)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.grid(alpha=.2)
    st.pyplot(fig)
with right:
    st.subheader("ROC curve")
    fpr, tpr, _ = roc_curve(y, p)
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(fpr, tpr)
    ax.plot([0,1],[0,1], linestyle="--")
    ax.set_xlabel("False-positive rate")
    ax.set_ylabel("True-positive rate")
    ax.grid(alpha=.2)
    st.pyplot(fig)

st.subheader("Operating-point sensitivity")
thresholds = np.linspace(.05,.95,37)
rows=[]
for t in thresholds:
    pred=(p>=t).astype(int)
    tp=((pred==1)&(y==1)).sum(); fp=((pred==1)&(y==0)).sum(); tn=((pred==0)&(y==0)).sum(); fn=((pred==0)&(y==1)).sum()
    rows.append({"threshold":t,"precision":tp/max(tp+fp,1),"recall":tp/max(tp+fn,1),"fpr":fp/max(fp+tn,1)})
curve=pd.DataFrame(rows).set_index("threshold")
st.line_chart(curve)
st.caption("The production-style operating point is selected to maximize recall while keeping FPR ≤ 2%.")
