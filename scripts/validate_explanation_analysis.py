"""Compatibility entry point; implementation: validation/frequentist/explanations.py."""
import sys, runpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if __name__ == "__main__":
    runpy.run_module("validation.frequentist.explanations",run_name="__main__")
else:
    from validation.frequentist.explanations import *
