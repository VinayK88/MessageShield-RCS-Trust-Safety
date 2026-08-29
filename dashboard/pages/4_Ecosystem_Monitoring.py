from pathlib import Path
import pandas as pd
import streamlit as st
from dashboard.apple_theme import apply_theme, page_header, section
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/"outputs"
st.set_page_config(page_title="Ecosystem Monitoring",page_icon="🌐",layout="wide"); apply_theme(); page_header("MessageShield · Ecosystem Monitoring","Know when the ecosystem starts to move.","Operational monitoring for prevalence, enforcement, false positives, recall, click-through, score movement, and simple anomaly heuristics.")
try: metrics=pd.read_csv(OUT/"ecosystem_metrics.csv")
except FileNotFoundError: st.warning("Run the pipeline first: `python src/run_pipeline.py --rows 30000`"); st.stop()
numeric=metrics.select_dtypes(include="number")
if numeric.empty: st.info("No numeric monitoring columns found."); st.stop()
latest=numeric.iloc[-1]; prior=numeric.iloc[-2] if len(numeric)>1 else latest
items=[]
for name,value in latest.items():
    label=name.replace("_"," ").title(); rendered=f"{value:.2%}" if 0<=value<=1 else f"{value:,.2f}"; delta=value-prior[name]; items.append((label,rendered,delta))
for start in range(0,min(len(items),16),4):
    cols=st.columns(4)
    for col,(label,value,delta) in zip(cols,items[start:start+4]): col.metric(label,value,f"{delta:+.3f} vs prior")
section("Metric trends","Inspect multiple ecosystem measures together to understand whether a change is isolated or correlated."); selected=st.multiselect("Choose metrics",list(numeric.columns),default=list(numeric.columns[:min(5,len(numeric.columns))]));
if selected: st.line_chart(numeric[selected])
section("Monitoring table","Every synthetic monitoring window remains available for comparison and debugging."); st.dataframe(metrics,use_container_width=True,hide_index=True)
section("Alert heuristics","Simple 2σ movement flags metrics for review; it does not declare adversarial intent."); alerts=[]
for col in numeric.columns:
    series=numeric[col].dropna()
    if len(series)>=4:
        baseline=series.iloc[:-1].mean(); last=series.iloc[-1]; sd=series.iloc[:-1].std()
        if sd>0 and abs(last-baseline)>2*sd: alerts.append({"metric":col,"latest":last,"baseline_mean":baseline,"severity":"Review"})
if alerts: st.dataframe(pd.DataFrame(alerts),use_container_width=True,hide_index=True)
else: st.success("No simple 2σ monitoring alerts in the latest synthetic window.")
