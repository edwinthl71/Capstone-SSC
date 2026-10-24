"""Late-delivery risk model: pure-Python scorer for the exported Gradient Boosting trees (no scikit-learn needed)."""
import json
import math
from pathlib import Path

MODEL = json.loads((Path(__file__).parent / "model.json").read_text())
MODES = {"First Class": 1, "Second Class": 2, "Same Day": 0, "Standard Class": 4}
PROMISE_DAYS = {1: 1, 2: 2, 0: 0, 4: 4}
BANDS = [(2 / 3, "High"), (1 / 3, "Medium"), (0.0, "Low")]  # same cut-offs as the notebook
BAND_COLOURS = {"High": "#c93f52", "Medium": "#c98a0b", "Low": "#2f8a5f"}
DEPTS = MODEL["depts"]
DEFAULTS = MODEL["defaults"]


def predict(order: dict) -> float:
    """order keys: days_sched, hour, dow, month, Payment_Type_ID, n_items, total_qty, order_sales, avg_discount_rate, dept_code"""
    x = [order[f] for f in MODEL["features"]]
    raw = MODEL["init"]
    for left, right, feat, thr, val in MODEL["trees"]:
        n = 0
        while left[n] != -1:
            n = left[n] if x[feat[n]] <= thr[n] else right[n]
        raw += MODEL["lr"] * val[n]
    return 1.0 / (1.0 + math.exp(-raw))


def band(p: float) -> str:
    for cut, name in BANDS:
        if p >= cut:
            return name
    return "Low"


def action(b: str) -> str:
    return {"High": "Likely to miss its promised date. Quote a realistic date, warn the customer, or upgrade the carrier.",
            "Medium": "Could go either way. Monitor it and consider a proactive delay notice.",
            "Low": "Likely to arrive on time. No action needed at checkout."}[b]
