from pathlib import Path
import json
import pandas as pd
import streamlit as st
from dashboard.apple_theme import apply_theme, page_header, section

ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/"outputs"
st.set_page_config(page_title="Experiments",page_icon="🧪",layout="wide"); apply_theme(); page_header("MessageShield · Experiments","Measure protection without losing sight of user friction.","A/B testing and counterfactual analysis compare warning interventions, risky engagement, legitimate-user impact, and treatment effects.")
try: df=pd.read_csv(OUT/"scored_messages.csv"); summary=json.loads((OUT/"summary.json").read_text())
except FileNotFoundError: st.warning("Run the pipeline first: `python src/run_pipeline.py --rows 30000`"); st.stop()
ab=summary["ab_test"]; ipw=summary["counterfactual_ipw"]
control=df[df.warning_ui==0]; treatment=df[df.warning_ui==1]; spam=df[df.is_spam==1]; legit=df[df.is_spam==0]
metrics=[("Control CTR",f"{ab['control_ctr']:.2%}"),("Warning CTR",f"{ab['treatment_ctr']:.2%}"),("Absolute effect",f"{ab['absolute_lift']:+.2%}"),("Relative effect",f"{ab['relative_lift']:+.1%}"),("p-value",f"{ab['p_value']:.3g}"),("IPW ATE",f"{ipw['ate']:+.2%}"),("Control messages",f"{len(control):,}"),("Treatment messages",f"{len(treatment):,}"),("Spam messages",f"{len(spam):,}"),("Legitimate messages",f"{len(legit):,}"),("Warning exposure",f"{df.warning_ui.mean():.1%}"),("Overall CTR",f"{df.clicked.mean():.2%}")]
for s in range(0,len(metrics),4):
    cols=st.columns(4)
    for c,(l,v) in zip(cols,metrics[s:s+4]): c.metric(l,v)
section("Observed A/B result","Directly observed click-through under control and warning experiences."); obs=pd.DataFrame({"experience":["Control","Warning UI"],"CTR":[ab['control_ctr'],ab['treatment_ctr']]}).set_index("experience"); st.bar_chart(obs)
section("Counterfactual estimate","IPW estimates expected click-through if comparable traffic had experienced each policy."); cf=pd.DataFrame({"scenario":["If no warning","If warning"],"Estimated CTR":[ipw['ipw_ctr_if_no_warning'],ipw['ipw_ctr_if_warning']]}).set_index("scenario"); st.bar_chart(cf)
section("Safety intervention by abuse label","A useful intervention reduces harmful engagement while limiting side effects on legitimate conversations."); segment=df.groupby(["is_spam","warning_ui"]).clicked.mean().reset_index(); segment["message_type"]=segment.is_spam.map({0:"Legitimate",1:"Spam"}); segment["experience"]=segment.warning_ui.map({0:"Control",1:"Warning"}); pivot=segment.pivot(index="message_type",columns="experience",values="clicked"); st.dataframe(pivot.style.format("{:.2%}"),use_container_width=True)
st.caption("Synthetic experiment mechanics only; this does not establish real-world causal impact.")
