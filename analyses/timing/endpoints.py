"""Point timing endpoints from the exported primary survey-logistic fit."""
import json
import numpy as np,pandas as pd
from scipy.special import expit
from scipy.optimize import brentq
from src.specification import ROOT
from src.frequentist.export import load_primary
OUT=ROOT/'outputs/timing';HERE=ROOT/'analyses/timing'
def endpoint(X,weights,beta,j,f):
 eta=X@beta;p0=expit(eta);p1=expit(eta+beta[j]);delta=p1-p0
 assert beta[j]>0,'This positive endpoint presentation requires a positive fitted association.'
 minimum=float(weights@(delta/(1-p0)))
 if f<minimum:return dict(feasible=False,minimum_fraction=minimum)
 lr=beta[j] if f==1 else brentq(lambda lr:weights@(delta/(expit(eta+lr)-p0))-f,beta[j]+1e-10,40)
 pg=expit(eta+lr);fg=delta/(pg-p0)
 np.testing.assert_allclose(weights@fg,f,atol=1e-10);assert fg.max()<=1+1e-8
 np.testing.assert_allclose((1-fg)*p0+fg*pg,p1,atol=1e-10)
 subgroup_weights=weights*fg/f;baseline=float(subgroup_weights@p0);prevalence=float(subgroup_weights@pg)
 return dict(feasible=True,minimum_fraction=minimum,component_OR=float(np.exp(lr)),component_baseline=baseline,component_prevalence=prevalence,prevalence_ratio=prevalence/baseline,target_baseline=float(weights@p0),target_circumcised=float(weights@p1),max_mixture_error=float(np.max(abs((1-fg)*p0+fg*pg-p1))))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cache,meta=load_primary();X=cache['X0'];w=cache['target_weights'];b=cache['coefficients'];j=int(cache['circ_index'])
    spec=json.loads((HERE/'source_values.json').read_text());rows=[]
    for scenario,key in [('adult_only','adult_shares'),('infant_only','infant_shares')]:
        for fraction in spec['assumptions'][key]:
            rows.append(dict(scenario=scenario,fraction=fraction,**endpoint(X,w,b,j,fraction)))
    df=pd.DataFrame(rows);df.to_csv(OUT/'endpoint_results.csv',index=False)
    full=endpoint(X,w,b,j,1.)
    np.testing.assert_allclose(full['component_OR'],meta['odds_ratio'],rtol=1e-12)
    assert not endpoint(X,w,b,j,full['minimum_fraction']/2)['feasible']
    (OUT/'endpoint_validation.json').write_text(json.dumps(dict(passed=True,method='frequentist point scenarios',uncertainty='No scenario confidence intervals calculated',source_artifact_sha256=meta['artifact_sha256'],input_sha256=meta['input_sha256'],minimum_fraction=full['minimum_fraction'],standardization=meta['standardization'],mixtures_reconstructed=True,scenario_rows=len(rows)),indent=2)+'\n')
    print(df.to_string(index=False))
if __name__=='__main__':main()
