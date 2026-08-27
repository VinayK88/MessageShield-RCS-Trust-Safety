from pathlib import Path
import json
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
st.set_page_config(page_title="Experiments", page_icon="🧪", layout="wide")
st.title("🧪 Product Experiments & Counterfactuals")
st.caption("Measure whether safety interventions reduce risky actions without over-penalizing legitimate engagement.")

try:
    df = pd.read_csv(OUT / "scored_messages.csv")
    summary = json.loads((OUT / "summary.json").read_text())
except FileNotFoundError:
    st.warning("Run the pipeline first: `python src/run_pipeline.py --rows 30000`")
    st.stop()

ab = summary["ab_test"]
ipw = summary["counterfactual_ipw"]

c1,c2,c3,c4=st.columns(4)
c1.metric("Control CTR", f"{ab['control_ctr']:.2%}")
c2.metric("Warning CTR", f"{ab['treatment_ctr']:.2%}")
c3.metric("Absolute effect", f"{ab['absolute_lift']:+.2%}")
c4.metric("p-value", f"{ab['p_value']:.3g}")

st.subheader("Observed A/B result")
obs = pd.DataFrame({"experience":["Control","Warning UI"],"CTR":[ab['control_ctr'],ab['treatment_ctr']]}).set_index("experience")
st.bar_chart(obs)

st.subheader("Counterfactual estimate")
cf = pd.DataFrame({"scenario":["If no warning","If warning"],"Estimated CTR":[ipw['ipw_ctr_if_no_warning'],ipw['ipw_ctr_if_warning']]}).set_index("scenario")
st.bar_chart(cf)
st.metric("IPW Average Treatment Effect", f"{ipw['ate']:+.2%}")

st.subheader("Safety intervention by abuse label")
segment = df.groupby(["is_spam","warning_ui"]).clicked.mean().reset_index()
segment["message_type"] = segment.is_spam.map({0:"Legitimate",1:"Spam"})
segment["experience"] = segment.warning_ui.map({0:"Control",1:"Warning"})
pivot = segment.pivot(index="message_type", columns="experience", values="clicked")
st.dataframe(pivot.style.format("{:.2%}"), use_container_width=True)
st.caption("A strong intervention should reduce risky engagement materially while minimizing side effects on legitimate messaging.")
