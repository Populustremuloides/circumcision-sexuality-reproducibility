"""Stable signatures of failed fits; raw messages remain in analysis output files."""
import json,re
import pandas as pd

def failure_signature(value):
    if pd.isna(value):return None
    value=str(value)
    if value.startswith('['):
        rows=json.loads(value)
        return sorted((str(row['deleted_psu']),failure_signature(row['error'])) for row in rows)
    match=re.fullmatch(r'Unstable information matrix, condition=([0-9.eE+\-]+)',value)
    if match:
        condition=float(match.group(1))
        # Preserve the actual failure criterion, not the platform-specific last digits.
        assert condition >= 1e10, value
        return 'unstable_information_matrix'
    # Unknown diagnostics remain exact comparisons, rather than silently ignored.
    return value
