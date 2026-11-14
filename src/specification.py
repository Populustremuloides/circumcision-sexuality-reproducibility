"""Executable common model specification; survey-weighted logistic regression formulas."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads((ROOT/"config/analyses.json").read_text())
ADJUST=SPEC["adjustment_sets"]
ANALYSES={r["id"]:r for r in SPEC["analyses"]}
