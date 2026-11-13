"""Generate the two timing endpoint tables from existing fitted coefficients.

Uses a common component OR and covariate-varying timing fraction. No timing
fraction is estimated, no priors are changed, and no outcome regression is refit.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import argparse,json,hashlib
import numpy as np,pandas as pd,patsy
from scipy.special import expit
from scipy.optimize import brentq
from src.specification import ROOT,ADJUST
OUT=ROOT/'outputs/timing';HERE=ROOT/'analyses/timing'
def weighted_quantile(x,w):
 ix=np.argsort(x);return np.interp([.025,.5,.975],np.cumsum(w[ix])-.5*w[ix],x[ix])
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
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');a=parser.parse_args()
 d=pd.read_csv(ROOT/'data/analysis.csv.gz');sources=json.loads((HERE/'source_values.json').read_text());records=[];bounds=[];hashes={}
 direct=ROOT/'outputs/bayesian/headline/nhanes.msm_ever.adjusted.npz'
 direct_record=json.loads(direct.with_suffix('.json').read_text())
 assert direct_record['input_sha256']==hashlib.sha256((ROOT/'data/analysis.csv.gz').read_bytes()).hexdigest(),'Direct fit is stale; rerun the shared pipeline.'
 inputs=[ROOT/'data/analysis.csv.gz',HERE/'source_values.json',HERE/'sources.json',Path(__file__),direct]
 for pop in ['all','us_born']:
  rhs=ADJUST['full'] if pop=='all' else ADJUST['full'].replace(' + foreign_born','')
  _,x=patsy.dmatrices('msm_ever ~ '+rhs,d.loc[d.eligible&(True if pop=='all' else d.foreign_born.eq(0))],return_type='dataframe');z=d.loc[x.index];take=z.circ.eq(1);X=x.to_numpy()[take];w=z.loc[take,'weight'].to_numpy();w/=w.sum();j=list(x.columns).index('circ');X[:,j]=0
  cached=OUT/f'model_{pop}_msm_ever.npz';inputs.append(cached);old=np.load(cached);assert list(old['columns'])==list(x.columns)
  models=[('gaussian_summary',old['posterior_mean'])]
  if pop=='all':
   archive=np.load(direct);assert list(archive['columns'])==list(x.columns);B=archive['draws'];bw=archive['weights'];models.insert(0,('direct_calibrated',bw@B))
   # Propagate the existing full posterior, keeping all draw weights and fixed empirical X.
   minima=[]
   for start in range(0,len(B),128):
    b=B[start:start+128];p0=expit(X@b.T);p1=expit(X@b.T+b[:,j]);minima.extend(w@np.maximum(0,(p1-p0)/(1-p0)))
   lo,med,hi=weighted_quantile(np.array(minima),bw);bounds.append(dict(population=pop,method='direct_calibrated',low=lo,median=med,high=hi,p_positive=float(bw@(B[:,j]>0)),draws=len(B)))
  for method,b in models:
   complete=endpoint(X,w,b,j,1.)
   np.testing.assert_allclose(complete['component_OR'],np.exp(b[j]),rtol=1e-10)
   assert not endpoint(X,w,b,j,complete['minimum_fraction']/2)['feasible']
   for scenario,key in [('adult_only','adult_shares'),('infant_only','infant_shares')]:
    for f in sources['assumptions'][key]:records.append(dict(population=pop,method=method,scenario=scenario,fraction=f,**endpoint(X,w,b,j,f)))
 # Independently check the old calculation before presenting the direct-method extension.
 reference=pd.read_csv(OUT/'required_component.csv')
 for r in records:
  if r['method']=='gaussian_summary':
   old=reference[(reference.population==r['population'])&(reference.outcome=='msm_ever')&(reference.estimate=='primary')&np.isclose(reference.fraction,r['fraction'])].iloc[0]
   np.testing.assert_allclose([r['component_OR'],r['component_prevalence'],r['minimum_fraction']],[old.component_OR,old.component_prevalence,old.minimum_fraction],rtol=1e-8,atol=1e-10)
 df=pd.DataFrame(records);df.to_csv(OUT/'endpoint_results.csv',index=False);pd.DataFrame(bounds).to_csv(OUT/'endpoint_uncertainty.csv',index=False)
 for p in inputs:hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 (OUT/'endpoint_validation.json').write_text(json.dumps(dict(passed=True,mixtures_reconstructed=True,previous_endpoint_results_reproduced=True,inputs=hashes,draws=int(bounds[0]['draws']),inference='conditional associations; no inferred timing share'),indent=2)+'\n')
 lines=['# Endpoint results','Generated by [endpoints.py](endpoints.py) from previously fitted coefficients and posterior draws. The direct calibrated Bayesian method is shown first, matching the repository headline method. The original Gaussian approximation and U.S.-born restriction follow as checks. These are conditional association scenarios, not estimated timing distributions or causal effects.']
 for (pop,method),g in df.groupby(['population','method'],sort=False):
  base=g.iloc[0];lines += [f'## {pop} — {method}',f'At the posterior coefficient mean, the adjusted baseline is {100*base.target_baseline:.2f}% and the circumcised prevalence is {100*base.target_circumcised:.2f}%, standardized to circumcised complete cases. This is a different summary from the median of posterior prevalence draws.',f'The adult-only minimum is {100*base.minimum_fraction:.2f}% of circumcised men, attained only at100% behavioral prevalence in that component.']
  for scenario,title in [('adult_only','All of the association assigned to adulthood'),('infant_only','All of the association assigned to infancy')]:
   lines += [f'### {title}','| Assumed component share | Baseline for that component | Required behavioral prevalence | Prevalence ratio | Common adjusted OR |','|---|---:|---:|---:|---:|']
   for _,r in g[g.scenario.eq(scenario)].iterrows():lines.append(f'| {100*r.fraction:.0f}% | {100*r.component_baseline:.2f}% | {100*r.component_prevalence:.2f}% | {r.prevalence_ratio:.2f} | {r.component_OR:.2f} |')
 lines += ['## Model uncertainty',f'For the direct calibrated posterior, the minimum positive adult share has median {100*med:.2f}% and a95% posterior interval of {100*lo:.2f}–{100*hi:.2f}%. This interval propagates uncertainty in the current-status association, conditional on the observed covariate distribution and the endpoint assumptions. It does not incorporate an external timing distribution or validate historical counts. Required component ORs in the tables are illustrative point calculations; no confidence or credible intervals for those ORs are claimed.', '## Reading the comparisons','The component baseline is the predicted never-circumcised prevalence standardized to the same covariate distribution as the constructed infant or adult component. The prevalence ratio therefore compares like distributions. It is distinct from the conditional odds ratio. Component shares may vary with covariates, while their survey-weighted mean equals the stated share.', 'The infant-only scenario fixes both childhood and adult groups at baseline. Setting only the adult group to baseline instead supports a preadult interpretation. Adult surgery having no effect on subsequent behavior does not establish that men selected for adult surgery had baseline-equivalent behavior beforehand. See [methods](methods.md).']
 text='\n\n'.join(lines);import re
 text=re.sub(r'(\|[^\n]*\|)\n\n(?=\|)',r'\1\n',text).replace('at100%','at 100%').replace('a95%','a 95%')+'\n'
 direct_rows=df[(df.population=='all')&(df.method=='direct_calibrated')]
 adult=direct_rows[(direct_rows.scenario=='adult_only')&np.isclose(direct_rows.fraction,.05)].iloc[0]
 infant=direct_rows[(direct_rows.scenario=='infant_only')&np.isclose(direct_rows.fraction,.90)].iloc[0]
 reporting=f'''# Guide for reporting the two endpoints

This is drafting material for a future paper update. The manuscript has not been modified.

## Suggested methods wording

We performed timing sensitivity analyses because age at circumcision was not observed in NHANES. A structured source audit informed a historical procedure-count benchmark but did not identify the infant-circumcised share of the analytic population. We therefore specified infant and adult shares as scenarios. One endpoint assumed that infant- and childhood-circumcised men had the same covariate-specific behavioral prevalence as never-circumcised men, assigning the entire excess to adulthood. The opposite endpoint fixed childhood and adult groups at baseline and assigned the excess to infancy. Within the fitted covariate patterns, we solved for a common timing-component odds ratio and component fractions whose weighted mean equaled the specified share. Behavioral prevalence and its baseline comparison were standardized to the same constructed component distribution.

## Suggested results wording

At the fitted current-status association, an adult-only explanation required at least {100*adult.minimum_fraction:.1f}% of circumcised men to have undergone adult circumcision, attained only if all men in that component reported lifetime male–male sexual behavior. If adult procedures accounted for 5% of circumcised men, the required behavioral prevalence was approximately {100*adult.component_prevalence:.0f}%, compared with a matched baseline of approximately {100*adult.component_baseline:.0f}% (adjusted OR {adult.component_OR:.1f}). Under the opposite assumption, with all later-circumcised groups at baseline and 90% of circumcised men assigned to infancy, the required infant-component prevalence was {100*infant.component_prevalence:.1f}% against a baseline of {100*infant.component_baseline:.1f}% (adjusted OR {infant.component_OR:.2f}). These calculations describe conditional endpoints rather than observed timing-specific associations.

## Uncertainty to accompany the result

The minimum positive adult-share budget had posterior median {100*med:.2f}% and a95% interval of {100*lo:.2f}–{100*hi:.2f}%, under the fitted current-status model and fixed empirical covariate distribution. This interval excludes uncertainty about historical procedure coverage and does not establish that a smaller adult share is impossible. The component ORs are illustrative point calculations, not separately observed subgroup estimates.

## Suggested table caption

Required lifetime male–male behavioral prevalence and odds ratio under two timing restrictions. Component shares are assumed percentages of currently circumcised men. The adult-only endpoint fixes infancy and childhood at the never-circumcised baseline; the infant-only endpoint fixes childhood and adulthood at that baseline. Baseline and required prevalence are standardized to the same constructed timing-component covariate distribution. Common component ORs and covariate-varying timing fractions reproduce the modeled current-status association. The scenarios do not estimate age at surgery or identify causal effects.

## How to connect the sources to the interpretation

Cite [S01 and S07](sources.md) for birth-cohort coverage and the historical procedure-count benchmark, using [the supplied bibliography](references.bib). The count extrapolation gives a conditional benchmark rather than an all-setting adult upper bound. Cite [S03](sources.md#s03--el-bcheraoui-et-al-2014-jama-pediatrics) only for the contemporary recorded procedure-age distribution. Its95.3% infant procedure share does not justify calling95% of the NHANES adults infant-circumcised. The other audited studies retain their documented roles and access limits.

The two endpoints organize the possible distribution of the observed association. They are not exhaustive explanations or causal bounds. Mixed infant, childhood and adult associations remain possible. Even excluding an adult-only explanation would leave childhood timing, unmeasured confounding and reporting differences unresolved. Similarly, no measured behavioral change after adult surgery does not establish baseline-equivalent behavior among men who selected surgery.

Use the [generated results](results.md) and [full methods](methods.md) together. Keep the common-OR endpoint results separate from constant-fraction marginal ORs and from the synthetic preadult/adult allocation regressions. A high conditional probability of a positive infant association under a later-null restriction inherits that restriction and is not a probability that infancy caused the association.
'''.replace('a95%', 'a 95%').replace('Its95.3%', 'Its 95.3%').replace('calling95%', 'calling 95%')
 for dest,content in [(HERE/'results.md',text),(HERE/'reporting.md',reporting)]:
  if a.check:assert dest.read_text()==content,f'Endpoint documentation is stale: {dest}'
  else:dest.write_text(content)
 print(df.to_string(index=False));print('Endpoint checks passed.')
if __name__=='__main__':main()
