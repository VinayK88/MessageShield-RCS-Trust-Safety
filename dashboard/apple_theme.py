import streamlit as st

APPLE_CSS='''
<style>
:root{--ink:#1d1d1f;--muted:#6e6e73;--soft:#f5f5f7;--line:#e8e8ed;--blue:#0071e3}
html,body,[class*="css"]{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Helvetica Neue",Arial,sans-serif;color:var(--ink)}
.stApp{background:#fff}.block-container{max-width:1450px;padding:1.8rem 2.4rem 5rem}
[data-testid="stSidebar"]{background:rgba(245,245,247,.96);border-right:1px solid var(--line)}
[data-testid="stMetric"]{background:var(--soft);border:1px solid rgba(0,0,0,.04);border-radius:24px;padding:1.05rem 1.15rem;min-height:112px;box-shadow:0 9px 28px rgba(0,0,0,.03)}
[data-testid="stMetricLabel"]{color:var(--muted);font-size:.72rem;font-weight:650}[data-testid="stMetricValue"]{font-size:1.85rem;font-weight:650;letter-spacing:-.04em}
[data-testid="stDataFrame"],[data-testid="stTable"]{border:1px solid var(--line);border-radius:22px;overflow:hidden}.stTabs [data-baseweb="tab"]{border-radius:999px;font-weight:600}
h1,h2,h3{letter-spacing:-.04em}.page-eyebrow{color:var(--blue);font-size:.74rem;font-weight:700;letter-spacing:.11em;text-transform:uppercase;margin:.35rem 0 .45rem}.page-title{font-size:3.2rem;line-height:1.02;font-weight:650;letter-spacing:-.055em;margin:0}.page-sub{color:var(--muted);font-size:1.05rem;line-height:1.55;max-width:900px;margin:.7rem 0 1.5rem}.section-title{font-size:1.7rem;font-weight:650;letter-spacing:-.04em;margin:1.2rem 0 .2rem}.section-sub{color:#86868b;font-size:.93rem;margin-bottom:1rem}.note{background:var(--soft);border:1px solid rgba(0,0,0,.04);border-radius:20px;padding:1rem 1.2rem;color:var(--muted)}
</style>
'''

def apply_theme(): st.markdown(APPLE_CSS,unsafe_allow_html=True)
def page_header(eyebrow,title,subtitle): st.markdown(f'<div class="page-eyebrow">{eyebrow}</div><div class="page-title">{title}</div><div class="page-sub">{subtitle}</div>',unsafe_allow_html=True)
def section(title,subtitle=''): st.markdown(f'<div class="section-title">{title}</div><div class="section-sub">{subtitle}</div>',unsafe_allow_html=True)
