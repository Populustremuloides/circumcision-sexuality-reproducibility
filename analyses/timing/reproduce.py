"""Reproduce source-count scenarios and point timing endpoints."""
from analyses.timing.counts import main as counts
from analyses.timing.endpoints import main as endpoints
if __name__=='__main__':
    counts();endpoints()
