"""Preserved historical count extrapolation; not an estimated lifetime age distribution."""
import json
import pandas as pd,numpy as np
from src.specification import ROOT
from src.frequentist.export import load_primary,sha
HERE=ROOT/'analyses/timing';OUT=ROOT/'outputs/timing'
def stock(t,threshold,counts):
    bands=[(max(threshold,15),44,counts['15to44']),(45,64,counts['45to64'])]
    if threshold<15:bands.insert(0,(threshold,14,counts['under15']))
    return sum(n for s in range(t-60,t+1) for lo,hi,n in bands if max(lo,20-(t-s))<=min(hi,60-(t-s)))
def main():
    OUT.mkdir(parents=True,exist_ok=True);cache,meta=load_primary()
    spec=json.loads((HERE/'source_values.json').read_text());registry=json.loads((HERE/'sources.json').read_text());ids={r['id'] for r in registry['sources']}
    assert len(ids)==14 and spec['newborn']['source_id'] in ids and spec['procedures']['source_id'] in ids
    assert spec['assumptions']['shares_are_estimated'] is False
    counts=spec['procedures']['counts'];assert stock(2016,18,counts)==43*counts['15to44']+16*counts['45to64']
    d=pd.read_csv(ROOT/meta['input_file']);z=d.set_index('SEQN').loc[cache['analytic_seqn']].copy();z['birth_early']=z.year-z.RIDAGEYR-1;z['birth_late']=z.year+1-z.RIDAGEYR
    rows=[]
    for cy,sub in z.groupby('year'):
        Nc=sub.loc[sub.circ.eq(1),'population_weight'].sum();Nf=sub.loc[sub.circ.eq(1)&sub.foreign_born.eq(1),'population_weight'].sum()
        for threshold in [18,15,10]:
            for missing in spec['assumptions']['setting_multipliers']:
                for history in spec['assumptions']['historical_multipliers']:
                    count=stock(int(cy+1),threshold,counts)*missing*history
                    rows.append(dict(cycle=int(cy),threshold=threshold,missing_multiplier=missing,historical_multiplier=history,stock=count,circ_population=Nc,fraction=min(1,count/Nc),fraction_foreign_unresolved=min(1,(count+Nf)/Nc)))
    pd.DataFrame(rows).to_csv(OUT/'count_envelopes.csv',index=False)
    coverage=[]
    for name,g in [('all_complete',z),('circumcised',z[z.circ.eq(1)])]:
        w=g.weight/g.weight.sum();coverage.append(dict(subset=name,n=len(g),weighted_population=g.weight.sum(),covered_definitely=float(w@(g.birth_early.ge(1979)&g.foreign_born.eq(0))),covered_possibly=float(w@(g.birth_late.ge(1979)&g.foreign_born.eq(0)))))
    pd.DataFrame(coverage).to_csv(OUT/'coverage.csv',index=False)
    pd.DataFrame(list(spec['newborn']['values'].items()),columns=['birth_year','hospital_neonatal_percent']).to_csv(OUT/'newborn_source_extract.csv',index=False)
    (OUT/'count_validation.json').write_text(json.dumps(dict(passed=True,source_hashes={p.name:sha(p) for p in [HERE/'source_values.json',HERE/'sources.json']},stock_2016_adult=stock(2016,18,counts),shares_estimated=False,source_artifact_sha256=meta['artifact_sha256']),indent=2)+'\n')
    print('Source audit, historical count arithmetic and cohort coverage reproduced.')
if __name__=='__main__':main()
