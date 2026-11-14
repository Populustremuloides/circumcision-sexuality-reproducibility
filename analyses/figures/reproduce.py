"""Rebuild the two selected figures from existing local NHANES outputs."""
from pathlib import Path
import subprocess,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def main():
    data=ROOT/'data/analysis.csv.gz'
    archive=ROOT/'outputs/bayesian/headline/nhanes.msm_ever.adjusted.npz'
    record=archive.with_suffix('.json')
    if not all(p.exists() for p in [data,archive,record]):
        raise SystemExit('Run python scripts/reproduce.py --nhanes-only first.')
    meta=json.loads(record.read_text())
    assert meta['input_sha256']==hashlib.sha256(data.read_bytes()).hexdigest(), 'Stale Bayesian fit; reproduce NHANES first.'
    for name in ['timing_or_curves','timing_probability_curves','timing_plot']:
        subprocess.run([sys.executable,'-m','analyses.figures.'+name],cwd=ROOT,check=True)
    timing=ROOT/'outputs/selected_figures/timing'
    conf=ROOT/'outputs/selected_figures/confounding';conf.mkdir(parents=True,exist_ok=True)
    t=json.loads((timing/'validation.json').read_text())
    (conf/'validation.json').write_text(json.dumps(dict(standardized_intact_probability=t['standardized_baseline'],standardized_circumcised_probability=t['standardized_circumcised']),indent=2))
    subprocess.run([sys.executable,'-m','analyses.figures.confounding_plot'],cwd=ROOT,check=True)
    print('Selected figures regenerated in outputs/selected_figures/. Published copies are unchanged.')
if __name__=='__main__':main()
