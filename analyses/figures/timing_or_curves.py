"""Timing-component OR trade-offs with covariate-varying timing composition.
Derives illustrative curves from the existing survey-weighted logistic fit.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd
from scipy.special import expit
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[2];REPO=ROOT;OUT=ROOT/'outputs/selected_figures/timing';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(REPO))
from analyses.timing.endpoints import endpoint
from src.frequentist.export import load_primary
cache, fit_metadata = load_primary()
archive=REPO/'outputs/frequentist/headline/nhanes.msm_ever.adjusted.npz'
X=cache['X0'];w=cache['target_weights'];b=cache['coefficients'];j=int(cache['circ_index'])
eta=X@b;pU=expit(eta);pC=expit(eta+b[j]);delta=pC-pU;observed=np.exp(b[j]);minimum=w@(delta/(1-pU));gap=w@delta
shares=[.01,.015,.025,.05,.10]
def solve(f,adult):
 pA=np.ones_like(pU) if np.isinf(adult) else expit(eta+np.log(adult))
 if abs(adult-observed)<1e-9:early=observed;pE=pC.copy();fX=np.full(len(w),f)
 else:
  def budget(le):
   pe=expit(eta+le);return w@((pC-pe)/(pA-pe))-f
  if adult<observed:
   le=brentq(budget,b[j]+1e-10,8.)
  else:
   if budget(0)<-1e-12:return None
   le=0. if abs(budget(0))<1e-12 else brentq(budget,0.,b[j]-1e-10)
  early=np.exp(le);pE=expit(eta+le);fX=(pC-pE)/(pA-pE)
 assert fX.min()>=-1e-8 and fX.max()<=1+1e-8
 assert abs(w@fX-f)<1e-9
 err=np.max(abs((1-fX)*pE+fX*pA-pC));assert err<1e-10
 adult_contribution=(w@(fX*(pA-pU)))/gap
 assert -.000001<=adult_contribution<=1.000001
 return dict(adult_OR=adult,early_OR=early,adult_share=f,adult_excess_fraction=adult_contribution,max_mixture_error=err)
rows=[];ends=[];curves={};xmax=250
for f in shares:
 early_only=endpoint(X,w,b,j,1-f)
 adult_only=endpoint(X,w,b,j,f)
 stop=adult_only.get('component_OR',np.inf)
 grid=np.unique(np.r_[np.geomspace(1,min(stop,xmax),450),observed,min(stop,xmax)])
 curve=[solve(f,a) for a in grid];curve=[r for r in curve if r is not None];curves[f]=pd.DataFrame(curve);rows+=curve
 end=dict(adult_share=f,early_only_OR=early_only['component_OR'],adult_only_OR=stop,minimum_adult_share=minimum)
 if np.isfinite(stop):
  v=solve(f,stop*(1-1e-10));assert abs(v['early_OR']-1)<1e-6
 else:end['early_OR_at_infinite_adult_OR']=solve(f,np.inf)['early_OR']
 ends.append(end)
pd.DataFrame(rows).to_csv(OUT/'curve_points.csv',index=False);pd.DataFrame(ends).to_csv(OUT/'endpoints.csv',index=False)
# Use the 5% scenario to explain contributions without implying a preferred timing share.
f=.05;adult_end=next(e['adult_only_OR'] for e in ends if e['adult_share']==f)
half=brentq(lambda la:solve(f,np.exp(la))['adult_excess_fraction']-.5,0,np.log(adult_end)-1e-9);mid=solve(f,np.exp(half))
contribution_rows=[]
for target,dashes,label in [(.10,(0,(12,4)),'90% of excess before age 18'),
                            (.25,(0,(8,4)),'75% of excess before age 18'),
                            (.50,(0,(5,3)),'50% of excess in each group'),
                            (.75,(0,(2,2)),'75% of excess in adults'),
                            (.90,(0,(1,2)),'90% of excess in adults')]:
 half_rows=[]
 for adult in np.geomspace(1.05,xmax,1400):
  pA=expit(eta+np.log(adult))
  def contribution_budget(le):
   pE=expit(eta+le);fx=(pC-pE)/(pA-pE)
   return (w@(fx*(pA-pU)))/gap-target
  lo,hi=(b[j]+1e-9,np.log(100)) if adult<observed else (0,b[j]-1e-9)
  if contribution_budget(lo)*contribution_budget(hi)>0:continue
  le=brentq(contribution_budget,lo,hi);pE=expit(eta+le);fx=(pC-pE)/(pA-pE)
  assert fx.min()>=0 and fx.max()<=1
  assert abs(contribution_budget(le))<1e-8
  half_rows.append(dict(adult_OR=adult,early_OR=np.exp(le),adult_share=w@fx,adult_excess_fraction=target))
 hq=pd.DataFrame(half_rows);contribution_rows+=half_rows
 if target==.5:hq.to_csv(OUT/'equal_contribution_curve.csv',index=False)
pd.DataFrame(contribution_rows).to_csv(OUT/'contribution_curves.csv',index=False)
meta=dict(outcome='lifetime male-male sexual behavior',population='NHANES1999-2016 eligible men20-59, pooled complete cases',model='survey-weighted logistic regression, fitted coefficients',adjusted_OR=float(observed),standardized_baseline=float(w@pU),standardized_circumcised=float(w@pC),minimum_adult_share=float(minimum),halfway_reference=mid,illustrated_5pct_adult_only_OR=float(adult_end),maximum_mixture_error=max(r['max_mixture_error'] for r in rows),sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [archive,REPO/'data/pooled.csv.gz',Path(__file__)]})
(OUT/'validation.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta,indent=2));print(pd.DataFrame(ends).to_string(index=False))
