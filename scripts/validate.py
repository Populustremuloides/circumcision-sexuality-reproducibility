"""Compatibility entry point; implementation: validation/frequentist/core.py."""
import sys, runpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if __name__ == "__main__":
    runpy.run_module("validation.frequentist.core",run_name="__main__")
else:
    from validation.frequentist.core import *
