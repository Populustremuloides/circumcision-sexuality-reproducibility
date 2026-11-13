"""Compatibility entry point; implementation: src/frequentist/identity.py."""
import sys, runpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if __name__ == "__main__":
    runpy.run_module("src.frequentist.identity",run_name="__main__")
else:
    from src.frequentist.identity import *
