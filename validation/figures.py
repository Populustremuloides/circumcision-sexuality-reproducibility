"""Validate consistent frequentist targets and every saved timing mixture point."""
import json
import numpy as np,pandas as pd
from scipy.special import expit
from src.specification import ROOT
from src.frequentist.export import load_primary

def main():
    c,m=load_primary();out=ROOT/'outputs/selected_figures';td=out/'timing';cd=out/'confounding'
    a=json.loads((td/'validation.json').read_text());b=json.loads((td/'probability_validation.json').read_text());f=json.loads((cd/'probability_bands_validation.json').read_text())
    p0=m['standardization']['intact_probability'];p1=m['standardization']['circumcised_probability']
    np.testing.assert_allclose([a['standardized_baseline'],a['standardized_circumcised'],f['intact_probability'],f['circumcised_probability']],[p0,p1,p0,p1],atol=1e-13)
    w=c['target_weights'];eta=c['X0']@c['coefficients'];u=expit(eta);pc=expit(eta+c['coefficients'][int(c['circ_index'])]);err=0.;tested=0
    for name in ['curve_points.csv','contribution_curves.csv']:
        for r in pd.read_csv(td/name).itertuples():
            pa=expit(eta+np.log(r.adult_OR));pe=expit(eta+np.log(r.early_OR))
            if abs(r.adult_OR-r.early_OR)<1e-9:fx=np.full(len(w),r.adult_share)
            else:fx=(pc-pe)/(pa-pe)
            assert fx.min()>=-1e-8 and fx.max()<=1+1e-8
            np.testing.assert_allclose(w@fx,r.adult_share,atol=1e-9)
            error=float(abs((1-fx)*pe+fx*pa-pc).max());assert error<1e-10;err=max(err,error);tested+=1
    for name in ['probability_curves.csv','probability_contributions.csv','probability_full_adult_excess.csv','probability_zero_adult_excess.csv']:
        d=pd.read_csv(td/name);assert d.adult_probability.between(-1e-12,1+1e-12).all() and d.early_probability.between(-1e-12,1+1e-12).all()
        np.testing.assert_allclose(d.adult_share*d.adult_probability+(1-d.adult_share)*d.early_probability,p1,atol=1e-9)
    d=pd.read_csv(cd/'probability_bands_curve_points.csv')
    for q,target in [('intact_confounder_prevalence',p0),('circumcised_confounder_prevalence',p1)]:np.testing.assert_allclose((1-d[q])*d.outcome_probability_without+d[q]*d.outcome_probability_with,target,atol=1e-12)
    result=dict(passed=True,standardization=m['standardization'],primary_model_artifact=m['artifact_sha256'],OR_curve_points=tested,max_mixture_error=err,confounder_curve_points=len(d),feasible_color_samples=f['feasible_color_samples'],no_scenario_uncertainty_claimed=True)
    (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print('Both figures reproduce the same frequentist targets; all mixture checks passed.')
if __name__=='__main__':main()
