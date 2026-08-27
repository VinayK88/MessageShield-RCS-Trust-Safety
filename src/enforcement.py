from __future__ import annotations
import pandas as pd


def decide_action(row: pd.Series) -> str:
    score = float(row.get("spam_score", 0.0))
    reports = float(row.get("prior_reports", 0.0))
    fanout = float(row.get("unique_recipients_24h", 0.0))
    label = str(row.get("abuse_label", "benign"))

    if score >= 0.92 and (reports >= 2 or fanout >= 30 or label in {"phishing", "malware"}):
        return "BLOCK"
    if score >= 0.82:
        return "QUARANTINE"
    if score >= 0.68:
        return "WARN"
    if score >= 0.52 and fanout >= 15:
        return "RATE_LIMIT"
    if score >= 0.45:
        return "HUMAN_REVIEW"
    return "ALLOW"


def apply_enforcement(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["recommended_action"] = out.apply(decide_action, axis=1)
    return out
