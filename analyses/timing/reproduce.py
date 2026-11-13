"""Reproduce the documented timing package from the shared NHANES analysis inputs."""
import argparse,json,subprocess,sys,hashlib,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=ROOT/'analyses/timing';OUT=ROOT/'outputs/timing'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--full',action='store_true',help='Also rerun full original timing grids and synthetic allocations.');p.add_argument('--check',action='store_true',help='Verify generated endpoint documentation rather than update it.');a=p.parse_args()
 spec=json.loads((HERE/'source_values.json').read_text());registry=json.loads((HERE/'sources.json').read_text());ids={r['id'] for r in registry['sources']}
 assert len(ids)==14 and spec['newborn']['source_id'] in ids and spec['procedures']['source_id'] in ids
 assert spec['assumptions']['shares_are_estimated'] is False
 assert spec['procedures']['counts']=={'under15':92000,'15to44':15000,'45to64':13000,'65plus':21000}
 assert sum(spec['procedures']['counts'].values())==141000 and spec['procedures']['reported_total']==142000
 # Verify stock arithmetic without importing run_timing, whose top-level code executes models.
 source=(HERE/'run_timing.py').read_text();module=ast.parse(source);stock=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='stock');context={'counts':spec['procedures']['counts']};exec(compile(ast.Module(body=[stock],type_ignores=[]),str(HERE/'run_timing.py'),'exec'),context)
 assert context['stock'](2016,18)==43*15000+16*13000==853000
 required=ROOT/'outputs/bayesian/headline/nhanes.msm_ever.adjusted.npz'
 if not required.exists():raise SystemExit('Run python scripts/reproduce.py first to generate the direct headline fit.')
 provenance=OUT/'provenance.json';stale=True
 if provenance.exists():
  hashes=json.loads(provenance.read_text())['inputs']
  expected=['data/analysis.csv.gz','config/analyses.json','analyses/timing/source_values.json','analyses/timing/sources.json']
  stale=any(hashes.get(f)!=hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in expected)
 if a.full or stale or not (OUT/'model_us_born_msm_ever.npz').exists():
  subprocess.run([sys.executable,'-m','analyses.timing.run_timing'],cwd=ROOT,check=True)
 if a.full:
  for module in ['analyses.timing.run_allocation','analyses.timing.run_conditional']:subprocess.run([sys.executable,'-m',module],cwd=ROOT,check=True)
 command=[sys.executable,'-m','analyses.timing.endpoints']+(['--check'] if a.check else [])
 subprocess.run(command,cwd=ROOT,check=True)
 record=json.loads((OUT/'endpoint_validation.json').read_text());assert record['passed']
 record.update(source_registry_checked=True,stock_arithmetic_checked=True,full_original_grids_rerun=a.full,source_values_sha256=hashlib.sha256((HERE/'source_values.json').read_bytes()).hexdigest())
 (OUT/'package_validation.json').write_text(json.dumps(record,indent=2)+'\n');print('Timing package checks passed.')
if __name__=='__main__':main()
