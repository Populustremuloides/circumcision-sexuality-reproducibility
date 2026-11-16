"""Rebuild the two selected figures from existing local NHANES outputs."""
from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parents[2]
def main():
    from src.frequentist.export import load_primary
    load_primary()  # Validate hashes, full coefficients and the standardization target.
    for name in ['timing_or_curves','timing_probability_curves','timing_plot']:
        subprocess.run([sys.executable,'-m','analyses.figures.'+name],cwd=ROOT,check=True)
    timing=ROOT/'outputs/selected_figures/timing'
    conf=ROOT/'outputs/selected_figures/confounding';conf.mkdir(parents=True,exist_ok=True)
    t=json.loads((timing/'validation.json').read_text())
    (conf/'validation.json').write_text(json.dumps(dict(standardized_intact_probability=t['standardized_baseline'],standardized_circumcised_probability=t['standardized_circumcised']),indent=2))
    subprocess.run([sys.executable,'-m','analyses.figures.confounding_plot'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'-m','validation.figures'],cwd=ROOT,check=True)
    print('Selected figures regenerated in outputs/selected_figures/. Published copies are unchanged.')
if __name__=='__main__':main()
