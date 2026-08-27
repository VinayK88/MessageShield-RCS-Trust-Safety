<div align="center">

# 🛡️ MessageShield

### RCS / RBM Trust & Safety Data Science Platform

**Spam · Phishing · Abuse Detection · Graph Analytics · A/B Testing · Counterfactual Inference · Ecosystem Monitoring**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Multi--Page%20Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Detection%20ML-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![NetworkX](https://img.shields.io/badge/NetworkX-Graph%20Signals-2C7FB8?style=flat-square)](https://networkx.org/)
[![Trust & Safety](https://img.shields.io/badge/Trust%20%26%20Safety-RCS%20%2F%20RBM-238636?style=flat-square)](#)

**message → sender behavior → graph context → risk score → enforcement → experiment → monitoring**

</div>

---

## 📊 Dashboard preview

<p align="center">
  <img src="assets/dashboard-preview.svg" alt="MessageShield Trust and Safety Command Center dashboard preview" width="100%" />
</p>

> **Command Center:** executive ecosystem health, model effectiveness, false-positive guardrails, intervention impact, and a high-risk investigation queue in one surface. The repository also includes dedicated views for model performance, abuse networks, experimentation, counterfactual analysis, and ecosystem monitoring.

---

## Product concept

MessageShield is a portfolio-grade Trust & Safety data science system for protecting an **RCS/RBM-style messaging ecosystem** from spam, phishing, and unwanted traffic while minimizing harm to legitimate users.

Rather than treating abuse detection as a pure classification task, the project combines **NLP, sender behavior, graph topology, experimentation, counterfactual inference, and operational monitoring** into one product-oriented workflow.

> **Privacy / provenance:** all data is synthetic. This project is inspired by common large-scale messaging Trust & Safety problems and is not affiliated with, trained on, or derived from Google production systems.

---

## What a reviewer can see in 60 seconds

| Surface | What it demonstrates |
|---|---|
| **Trust & Safety Command Center** | Executive ecosystem KPIs, spam score distribution, intervention impact, high-risk investigation queue |
| **Model Performance** | ROC-AUC, PR-AUC, threshold sensitivity, false-positive guardrail, precision-recall trade-offs |
| **Abuse Network** | Sender fan-out, campaign-like behavior, repeated text, reports, URLs, high-risk sender ranking |
| **Experiments & Counterfactuals** | A/B testing, two-proportion z-test, IPW counterfactual estimate, treatment side effects |
| **Ecosystem Monitoring** | Trend monitoring, prevalence, enforcement, recall, false positives, click-through, anomaly alerts |

---

## System architecture

```text
                         ┌────────────────────────────┐
                         │ Synthetic RCS / RBM events │
                         └─────────────┬──────────────┘
                                       │
                  ┌────────────────────┼────────────────────┐
                  │                    │                    │
                  ▼                    ▼                    ▼
        ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐
        │ Text / NLP      │  │ Behavior        │  │ Graph topology   │
        │ TF-IDF n-grams  │  │ velocity        │  │ fan-out          │
        │ spam language   │  │ reports / URLs  │  │ PageRank         │
        └────────┬────────┘  └────────┬────────┘  └────────┬─────────┘
                 └────────────────────┼────────────────────┘
                                      ▼
                            ┌───────────────────┐
                            │ Spam classifier   │
                            │ calibrated score  │
                            └─────────┬─────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
          ┌────────────────┐ ┌────────────────┐ ┌──────────────────┐
          │ Enforcement    │ │ Experimentation│ │ Monitoring       │
          │ FPR guardrail  │ │ A/B + IPW      │ │ ecosystem health │
          └────────────────┘ └────────────────┘ └──────────────────┘
```

---

## Detection strategy

The classifier fuses three signal families:

| Signal family | Examples |
|---|---|
| **Text** | TF-IDF word/bi-gram patterns, spam language, repeated phrasing |
| **Behavioral** | 24h sending velocity, unique recipients, URLs, reports, sender age |
| **Graph** | sender out-degree, weighted fan-out, PageRank, fan-out ratio |

The operating threshold is chosen to **maximize spam recall while keeping false-positive rate ≤ 2%**. This reflects the real Trust & Safety cost of blocking legitimate conversations.

---

## Multi-page dashboards

### 1. 🛡️ Trust & Safety Command Center

`dashboard/app.py`

Executive view for product, policy, and security stakeholders: spam prevalence, precision/recall, false-positive rate, PR-AUC, risk-score distributions, warning-UI impact, investigation queue, and monitoring snapshot.

### 2. 📈 Model Performance

`dashboard/pages/1_Model_Performance.py`

ROC/PR curves, calibrated operating threshold, threshold sensitivity, precision/recall/FPR trade-offs, and the explicit 2% production FPR guardrail.

### 3. 🕸️ Abuse Network & Sender Behavior

`dashboard/pages/2_Abuse_Network.py`

Recipient fan-out, sender activity, reports, repeated-text behavior, URL volume, campaign-risk ranking, and top-sender investigation queue.

### 4. 🧪 Experiments & Counterfactuals

`dashboard/pages/3_Experiments_Counterfactuals.py`

Control vs warning-UI CTR, two-proportion z-test, p-value, inverse propensity weighting, counterfactual CTR, ATE, and legitimate-user side-effect segmentation.

### 5. 🌐 Ecosystem Health & Monitoring

`dashboard/pages/4_Ecosystem_Monitoring.py`

Spam prevalence, enforcement, recall, false positives, click-through trends, score shifts, and latest-window anomaly alerts.

---

## Trust & Safety measurement framework

| Dimension | Core question | Example metric |
|---|---|---|
| **Prevalence** | How much abuse reaches the ecosystem? | spam prevalence |
| **Coverage** | How much abuse do we catch? | recall |
| **Collateral damage** | How often do we block legitimate traffic? | FPR |
| **Decision quality** | Are positive decisions reliable? | precision / PR-AUC |
| **User impact** | Does an intervention reduce risky behavior? | CTR change |
| **Causal impact** | What would happen without treatment? | IPW ATE |
| **Adversarial change** | Is traffic behavior shifting? | score / metric alerts |

---

## Repository map

```text
MessageShield-RCS-Trust-Safety/
├── assets/
│   └── dashboard-preview.svg
├── dashboard/
│   ├── app.py
│   └── pages/
│       ├── 1_Model_Performance.py
│       ├── 2_Abuse_Network.py
│       ├── 3_Experiments_Counterfactuals.py
│       └── 4_Ecosystem_Monitoring.py
├── src/
│   ├── generate_data.py
│   ├── features.py
│   ├── model.py
│   ├── experiments.py
│   ├── monitoring.py
│   └── run_pipeline.py
├── tests/
│   └── test_pipeline.py
├── requirements.txt
└── README.md
```

---

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_pipeline.py --rows 30000
streamlit run dashboard/app.py
```

---

## Why this project is relevant to messaging Trust & Safety

| Role capability | Repository evidence |
|---|---|
| Large-scale abuse analytics | synthetic event pipeline + ecosystem KPIs |
| Spam / phishing classification | NLP + behavioral + graph classifier |
| Adversarial behavior analysis | velocity, repetition, fan-out, reports, URLs |
| A/B testing | warning-UI experiment + z-test |
| Counterfactual analysis | inverse propensity weighting |
| False-positive management | explicit ≤2% FPR threshold guardrail |
| Product measurement | CTR + ecosystem-health framework |
| Automated monitoring | trend dashboards + anomaly heuristics |
| Cross-functional communication | executive dashboard + investigation surfaces |
| Python / statistics | end-to-end implementation |

---

## Interview walkthrough

> I built MessageShield as an end-to-end Trust & Safety data science system for an RCS-style messaging ecosystem. I combined NLP, sender behavior, and communication-graph signals to detect spam and phishing, then selected the operating threshold to maximize recall under a strict 2% false-positive guardrail. I evaluated a warning UI using both A/B testing and inverse-propensity-weighted counterfactual analysis, and built multi-page dashboards for executive ecosystem health, model performance, abuse networks, experimentation, and operational monitoring.

---

## Production evolution

A real large-scale deployment could extend this project with transformer/embedding message representations, multilingual abuse models, graph community detection, sender reputation, streaming feature computation, calibration by region/language/sender type, human-review feedback loops, policy-aware enforcement tiers, challenger-model evaluation, and privacy-preserving aggregation.

---

<div align="center">

### Protect ecosystem trust without sacrificing legitimate communication.

**NLP · Graph ML · Behavioral Analytics · Experimentation · Causal Inference · Monitoring**

</div>
