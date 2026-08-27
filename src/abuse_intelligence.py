from __future__ import annotations
import re
import pandas as pd

LABEL_RULES = {
    "phishing": ["verify", "suspended", "account", "confirm", "link"],
    "scam": ["winner", "gift", "claim", "crypto", "refund", "payment"],
    "impersonation": ["urgent", "payment", "confirm", "account"],
    "malware": ["download", "install", "attachment", "apk"],
}


def classify_message(text: str, spam_score: float | None = None) -> dict:
    tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
    matches = {label: len(tokens.intersection(words)) for label, words in LABEL_RULES.items()}
    label, evidence_count = max(matches.items(), key=lambda kv: kv[1])
    if evidence_count == 0:
        label = "spam" if (spam_score or 0) >= 0.65 else "benign"
    confidence = min(0.99, 0.50 + 0.10 * evidence_count + 0.35 * float(spam_score or 0))
    evidence = [w for w in LABEL_RULES.get(label, []) if w in tokens][:4]
    explanation = "Signals: " + ", ".join(evidence) if evidence else "Behavioral/model risk score drove the decision."
    return {"abuse_label": label, "ai_confidence": confidence, "ai_explanation": explanation}


def enrich_messages(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    rows = [classify_message(t, s) for t, s in zip(out.text, out.get("spam_score", pd.Series([0.0] * len(out))))]
    enriched = pd.DataFrame(rows, index=out.index)
    return pd.concat([out, enriched], axis=1)
