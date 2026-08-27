from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
st.set_page_config(page_title="Ecosystem Monitoring", page_icon="🌐", layout="wide")
st.title("🌐 Ecosystem Health & Monitoring")
st.caption("Operational monitoring for spam prevalence, enforcement, false positives, recall, click-through, and score shifts.")

try:
    metrics = pd.read_csv(OUT / "ecosystem_metrics.csv")
except FileNotFoundError:
    st.warning("Run the pipeline first: `python src/run_pipeline.py --rows 30000`")
    st.stop()

numeric = metrics.select_dtypes(include="number")
if numeric.empty:
    st.info("No numeric monitoring columns found.")
    st.stop()

latest = numeric.iloc[-1]
cols = st.columns(min(5, len(latest)))
for i, (name, value) in enumerate(latest.items()):
    if i >= len(cols):
        break
    label = name.replace("_", " ").title()
    if 0 <= value <= 1:
        cols[i].metric(label, f"{value:.2%}")
    else:
        cols[i].metric(label, f"{value:,.2f}")

st.subheader("Metric trends")
selected = st.multiselect("Choose metrics", list(numeric.columns), default=list(numeric.columns[:min(4,len(numeric.columns))]))
if selected:
    st.line_chart(numeric[selected])

st.subheader("Monitoring table")
st.dataframe(metrics, use_container_width=True, hide_index=True)

st.subheader("Alert heuristics")
alerts=[]
for col in numeric.columns:
    series=numeric[col].dropna()
    if len(series)>=4:
        baseline=series.iloc[:-1].mean()
        last=series.iloc[-1]
        sd=series.iloc[:-1].std()
        if sd>0 and abs(last-baseline)>2*sd:
            alerts.append({"metric":col,"latest":last,"baseline_mean":baseline,"severity":"Review"})
if alerts:
    st.dataframe(pd.DataFrame(alerts), use_container_width=True, hide_index=True)
else:
    st.success("No simple 2σ monitoring alerts in the latest window.")
