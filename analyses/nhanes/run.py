"""Run registered survey-logistic models and export their complete fitted vectors."""
import argparse
import pandas as pd
from src.specification import ROOT,ANALYSES
from src.survey.design import Survey
from src.frequentist.export import write_fit

def frequentist(aid):
    spec=ANALYSES[aid];d=pd.read_csv(ROOT/'data/analysis.csv.gz');s=Survey(d)
    row,mask,details=s.model(spec['outcome'],spec['formula'].split(' ~ ',1)[1],d.eligible,'full',return_fit=True)
    return write_fit(aid,d,row,details)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--analysis',choices=list(ANALYSES));a=p.parse_args()
    for aid in ([a.analysis] if a.analysis else ANALYSES):
        row=frequentist(aid);print(aid,row['n'],row['events'],row['odds_ratio'])
if __name__=='__main__':main()
