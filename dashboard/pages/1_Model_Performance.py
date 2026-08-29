from pathlib import Path
import json
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, roc_curve
from dashboard.apple_theme import apply_theme, page_header, section

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
st.set_page_config(page_title="Model Performance", page_icon="📈", layout="wide")
apply_theme()
page_header("MessageShield · Model Performance","Detection quality, without hiding the tradeoffs.","Threshold selection, ranking quality, calibration-style sensitivity, and the ≤2% false-positive operating guardrail.")

try:
    df = pd.read_csv(OUT / "scored_messages.csv")
    summary = json.loads((OUT / "summary.json").read_text())
except FileNotFoundError:
    st.warning("Run the pipeline first: `python src/run_pipeline.py --rows 30000`")
    st.stop()

ev = summary["model_evaluation"]
y = df.is_spam.to_numpy(); p = df.spam_score.to_numpy()
flagged=(p>=ev['threshold']); high=(p>=.90); benign=(y==0); abusive=(y==1)
metrics=[("ROC-AUC",f"{ev['roc_auc']:.3f}"),("PR-AUC",f"{ev['pr_auc']:.3f}"),("Threshold",f"{ev['threshold']:.3f}"),("FPR",f"{ev['false_positive_rate']:.2%}"),("Recall",f"{ev['recall']:.1%}"),("Precision",f"{ev['precision']:.1%}"),("Messages",f"{len(df):,}"),("Flagged",f"{flagged.sum():,}"),("High risk",f"{high.sum():,}"),("Benign",f"{benign.sum():,}"),("Abusive",f"{abusive.sum():,}"),("Mean score",f"{p.mean():.3f}")]
for start in range(0,len(metrics),4):
    cols=st.columns(4)
    for col,(label,value) in zip(cols,metrics[start:start+4]): col.metric(label,value)

left, right = st.columns(2,gap="large")
with left:
    section("Precision–Recall curve","How positive-prediction quality changes as coverage increases.")
    precision, recall, _ = precision_recall_curve(y, p)
    fig, ax = plt.subplots(figsize=(6,4)); fig.patch.set_facecolor('white'); ax.set_facecolor('white'); ax.plot(recall, precision); ax.set_xlabel("Recall"); ax.set_ylabel("Precision"); ax.spines[["top","right"]].set_visible(False); ax.grid(alpha=.12); st.pyplot(fig,use_container_width=True)
with right:
    section("ROC curve","True-positive coverage relative to false-positive exposure.")
    fpr, tpr, _ = roc_curve(y, p)
    fig, ax = plt.subplots(figsize=(6,4)); fig.patch.set_facecolor('white'); ax.set_facecolor('white'); ax.plot(fpr,tpr); ax.plot([0,1],[0,1],linestyle="--",alpha=.45); ax.set_xlabel("False-positive rate"); ax.set_ylabel("True-positive rate"); ax.spines[["top","right"]].set_visible(False); ax.grid(alpha=.12); st.pyplot(fig,use_container_width=True)

section("Operating-point sensitivity","Compare precision, recall, and FPR over candidate thresholds instead of treating one threshold as permanent.")
thresholds=np.linspace(.05,.95,37); rows=[]
for t in thresholds:
    pred=(p>=t).astype(int); tp=((pred==1)&(y==1)).sum(); fp=((pred==1)&(y==0)).sum(); tn=((pred==0)&(y==0)).sum(); fn=((pred==0)&(y==1)).sum(); rows.append({"threshold":t,"precision":tp/max(tp+fp,1),"recall":tp/max(tp+fn,1),"fpr":fp/max(fp+tn,1)})
curve=pd.DataFrame(rows).set_index("threshold"); st.line_chart(curve); st.caption("Production-style operating point maximizes recall while keeping FPR ≤ 2% on the synthetic fixture.")
