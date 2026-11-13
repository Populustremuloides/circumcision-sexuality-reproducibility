"""Compatibility entry point; implementation: src/frequentist/explanations.py."""
import sys, runpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if __name__ == "__main__":
    runpy.run_module("src.frequentist.explanations",run_name="__main__")
else:
    from src.frequentist.explanations import *
