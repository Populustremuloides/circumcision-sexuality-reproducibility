"""Run one registered question with matching frequentist and Bayesian specifications."""
import argparse,json,hashlib,subprocess
from pathlib import Path
import pandas as pd
from src.specification import ROOT,ANALYSES
from src.survey.design import Survey

def frequentist(aid):
 spec=ANALYSES[aid];d=pd.read_csv(ROOT/'data/analysis.csv.gz');s=Survey(d)
 row,mask=s.model(spec['outcome'],spec['formula'].split(' ~ ',1)[1],d.eligible,'full')
 row.update(analysis_id=aid,method='survey_logistic_t',formula=spec['formula'],input_sha256=hashlib.sha256((ROOT/'data/analysis.csv.gz').read_bytes()).hexdigest(),spec_sha256=hashlib.sha256((ROOT/'config/analyses.json').read_bytes()).hexdigest(),code_sha256=hashlib.sha256((ROOT/'src/survey/design.py').read_bytes()).hexdigest(),commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip())
 out=ROOT/'outputs/frequentist/headline';out.mkdir(parents=True,exist_ok=True);(out/(aid+'.json')).write_text(json.dumps(row,indent=2)+'\n');return row

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--analysis',choices=list(ANALYSES));p.add_argument('--method',choices=['both','frequentist','bayesian'],default='both');a=p.parse_args()
 for aid in ([a.analysis] if a.analysis else ANALYSES):
  if a.method in ['both','frequentist']:frequentist(aid)
  if a.method in ['both','bayesian']:
   from src.bayesian.headline import run
   run(aid)
if __name__=='__main__':main()
