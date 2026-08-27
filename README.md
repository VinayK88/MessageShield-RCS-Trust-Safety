# MessageShield: RCS Trust & Safety Data Science

A portfolio-grade Trust & Safety data science project for detecting **spam, phishing, and unwanted messaging traffic** in an RCS/RBM-style ecosystem while explicitly controlling harm to legitimate users.

The project combines **message text**, **sender behavior**, and **communication-graph signals**, then evaluates product interventions with **A/B testing** and **counterfactual inference**. It also produces ecosystem-health metrics for spam prevalence, false positives, enforcement efficacy, and user impact.

> This repository uses fully synthetic data. It is inspired by the analytical problems common to large-scale messaging Trust & Safety systems and is not affiliated with or derived from Google production systems.

## Why this project

A production anti-abuse system cannot optimize only for model accuracy. Blocking legitimate conversations is costly, adversaries adapt, and product interventions can affect engagement. MessageShield therefore frames the problem around four questions:

1. **Detection:** Can we identify abusive messages using content, behavioral, and graph signals?
2. **User safety:** How much spam can we catch while holding the false-positive rate below a strict guardrail?
3. **Product impact:** Does a warning UI reduce risky click-through, and what side effects does it have?
4. **Ecosystem health:** Are spam prevalence, enforcement efficacy, or model scores shifting over time?

## System architecture

```text
Synthetic RCS/RBM events
        |
        v
+----------------------+      +----------------------+
| Text signals         |      | Behavioral signals   |
| TF-IDF n-grams       |      | velocity / reports   |
+----------+-----------+      +-----------+----------+
           \                          /
            \                        /
             v                      v
             +----------------------+
             | Communication graph  |
             | fan-out / PageRank   |
             +----------+-----------+
                        |
                        v
             +----------------------+
             | Spam classifier      |
             | calibrated threshold |
             +----------+-----------+
                        |
          +-------------+-------------+
          |                           |
          v                           v
+-------------------+        +------------------------+
| Ecosystem metrics |        | Product measurement    |
| FPR / recall /    |        | A/B test + IPW ATE     |
| prevalence / CTR  |        | warning UI             |
+-------------------+        +------------------------+
```

## What it demonstrates

- Python-based end-to-end analytics pipeline
- Statistical classification for spam/phishing detection
- NLP using TF-IDF word and bi-gram features
- Behavioral abuse features such as sending velocity and recipient fan-out
- Graph-derived sender features using NetworkX
- Imbalanced classification with PR-AUC and operational threshold selection
- False-positive guardrails to protect legitimate users
- Randomized-style A/B test analysis with a two-proportion z-test
- Counterfactual treatment-effect estimation using inverse propensity weighting
- Ecosystem-health monitoring and anomaly alerts
- Reproducible synthetic-data generation

## Modeling approach

The classifier combines **text**, **behavioral**, and **graph** signals. The operational threshold is selected for the **highest spam recall while keeping false-positive rate ≤ 2%**, reflecting the cost of blocking legitimate communication.

## Experimentation

`ab_test_report()` compares warning-UI click-through rates using a two-proportion z-test. `ipw_counterfactual()` estimates the average treatment effect using inverse propensity weighting when exposure is not perfectly randomized.

## Core Trust & Safety metrics

The monitoring layer reports spam prevalence, enforcement rate, false-positive rate, spam recall, user click rate, and model-score shift alerts.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_pipeline.py --rows 30000
```

## Example interview walkthrough

> I built an end-to-end Trust & Safety data science system for an RCS-style messaging ecosystem. I combined NLP features with sender behavior and communication-graph signals, trained a spam classifier, and selected the operating threshold to maximize abuse recall under a 2% false-positive guardrail. I also evaluated a warning UI with both an A/B test and inverse-propensity-weighted counterfactual analysis, then built monitoring for spam prevalence, enforcement rate, false positives, recall, user click-through, and score shifts.

## How this maps to a messaging Trust & Safety DS role

| Role capability | Repository evidence |
|---|---|
| Large-scale abuse analytics | Synthetic event pipeline and ecosystem metrics |
| Spam/phishing classification | NLP + behavioral + graph classifier |
| Adversarial behavior analysis | velocity, repetition, fan-out and graph features |
| A/B testing | two-proportion test for safety-warning intervention |
| Counterfactual analysis | inverse propensity weighting |
| False-positive management | explicit 2% FPR threshold guardrail |
| Product measurement | CTR and ecosystem-health metrics |
| Python / statistics | end-to-end implementation |

## License

MIT — intended for educational and portfolio use.
