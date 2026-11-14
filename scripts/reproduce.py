"""Reproduce NHANES estimates, validation, timing scenarios and selected figures."""
import argparse,json,os,shutil,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--offline',action='store_true',help='Require checksum-verified cached source files.')
    p.add_argument('--with-maloney',action='store_true',help='Also reproduce the separate optional Maloney supplement.')
    p.add_argument('--r-check',action='store_true',help='Also compare eight models with R survey.')
    a=p.parse_args()
    if a.r_check and not shutil.which('Rscript'):p.error('Rscript and the survey package are required for --r-check.')
    out=ROOT/'outputs';logs=out/'logs';logs.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',MKL_NUM_THREADS='1',MPLBACKEND='Agg',MPLCONFIGDIR=str(out/'.matplotlib'))
    modules=[('src.data.download',(['--offline'] if a.offline else [])+(['--with-maloney'] if a.with_maloney else [])),('src.frequentist.nhanes',[]),('src.frequentist.behavior',[]),('src.frequentist.identity',[]),('src.frequentist.explanations',[]),('validation.frequentist.explanations',[]),('validation.frequentist.core',[]),('analyses.nhanes.run',[])]
    if a.with_maloney:modules.append(('analyses.maloney.run',[]))
    modules += [('validation.release',['--with-maloney'] if a.with_maloney else []),('analyses.timing.reproduce',[]),('analyses.figures.reproduce',[]),('scripts.build_results',[]),('validation.repository',[])]
    stages=[(m,[sys.executable,'-m',m]+args) for m,args in modules]
    if a.r_check:stages.insert(-1,('R_survey',['Rscript','validation/r_survey/reproduce.R']))
    status=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),arguments=vars(a),stages=[])
    for name,command in stages:
        print('Running '+name,flush=True);start=time.monotonic()
        with (logs/(name+'.log')).open('w') as log:r=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        status['stages'].append(dict(module=name,command=command,exit_code=r.returncode,seconds=round(time.monotonic()-start,2)))
        if r.returncode:status.update(status='failed',failed_stage=name)
        (out/'run.json').write_text(json.dumps(status,indent=2)+'\n')
        if r.returncode:print((logs/(name+'.log')).read_text()[-6000:]);raise SystemExit(r.returncode)
    status.update(status='passed',completed_utc=datetime.now(timezone.utc).isoformat());(out/'run.json').write_text(json.dumps(status,indent=2)+'\n');print('Reproduction passed.')
if __name__=='__main__':main()
