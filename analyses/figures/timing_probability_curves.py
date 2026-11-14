"""Timing-component OR trade-offs with covariate-varying timing composition.
Derives illustrative curves from the existing calibrated Bayesian fit.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['MPLCONFIGDIR']='/tmp/circ-timing-matplotlib'
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd,patsy
from scipy.special import expit
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
ROOT=Path(__file__).resolve().parents[2];REPO=ROOT;OUT=ROOT/'outputs/selected_figures/timing';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(REPO))
from src.specification import ADJUST
from analyses.timing.endpoints import endpoint
D=pd.read_csv(REPO/'data/analysis.csv.gz');_,xx=patsy.dmatrices('msm_ever ~ '+ADJUST['full'],D.loc[D.eligible],return_type='dataframe');z=D.loc[xx.index];take=z.circ.eq(1);w=z.loc[take,'weight'].to_numpy();w/=w.sum();X=xx.to_numpy()[take];j=list(xx.columns).index('circ');X[:,j]=0
archive=REPO/'outputs/bayesian/headline/nhanes.msm_ever.adjusted.npz';cache=np.load(archive);assert list(cache['columns'])==list(xx.columns);b=cache['weights']@cache['draws'];eta=X@b;pU=expit(eta);pC=expit(eta+b[j]);delta=pC-pU;observed=np.exp(b[j]);minimum=w@(delta/(1-pU));gap=w@delta
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
 return dict(adult_probability=float(w@(fX*pA)/f), early_probability=float(w@((1-fX)*pE)/(1-f)), adult_OR=adult,early_OR=early,adult_share=f,adult_excess_fraction=adult_contribution,max_mixture_error=err)

colors=['#9AA7B3','#657C8C','#318C96','#366A9B','#283C68']
rows=[]
for f,c in zip(shares,colors):
 stop=endpoint(X,w,b,j,f).get('component_OR',np.inf)
 grid=np.unique(np.r_[np.geomspace(1,min(stop,1e8),900),observed,stop])
 q=pd.DataFrame([v for a in grid if (v:=solve(f,a)) is not None]);rows+=q.to_dict('records')
 assert np.max(abs(f*q.adult_probability+(1-f)*q.early_probability-w@pC))<1e-9
 label=f'{100*f:g}'+('%*' if f==.015 else '%')+f' adult / {100*(1-f):g}% before 18'
pd.DataFrame(rows).to_csv(OUT/'probability_curves.csv',index=False)
contrib=[]
for target,dashes,label in [(.10,(0,(12,4)),'90% of excess before age 18'),(.25,(0,(8,4)),'75% of excess before age 18'),(.50,(0,(5,3)),'50% of excess in each group'),(.75,(0,(2,2)),'75% of excess in adults'),(.90,(0,(1,2)),'90% of excess in adults')]:
 rr=[]
 for adult in np.r_[np.geomspace(1.01,1e8,2000),np.inf]:
  pA=np.ones_like(pU) if np.isinf(adult) else expit(eta+np.log(adult))
  def budget(le):
   pE=expit(eta+le);fx=(pC-pE)/(pA-pE)
   return w@(fx*(pA-pU))/gap-target
  lo,hi=(b[j]+1e-9,np.log(100)) if adult<observed else (0,b[j]-1e-9)
  if budget(lo)*budget(hi)>0:continue
  le=brentq(budget,lo,hi);pE=expit(eta+le);fx=(pC-pE)/(pA-pE);f=w@fx
  assert fx.min()>=0 and fx.max()<=1 and abs(budget(le))<1e-8
  pa=w@(fx*pA)/f;pe=w@((1-fx)*pE)/(1-f)
  assert abs(f*pa+(1-f)*pe-w@pC)<1e-10
  rr.append(dict(adult_probability=pa,early_probability=pe,adult_share=f,adult_excess_fraction=target))
 q=pd.DataFrame(rr);contrib+=rr
pd.DataFrame(contrib).to_csv(OUT/'probability_contributions.csv',index=False)
common=float(w@pC)*100
from matplotlib.ticker import PercentFormatter
(OUT/'probability_validation.json').write_text(json.dumps({'standardized_total_probability':float(w@pC),'colored_points':len(rows),'contribution_points':len(contrib),'max_total_probability_error':max(abs(r['adult_share']*r['adult_probability']+(1-r['adult_share'])*r['early_probability']-w@pC) for r in rows+contrib)},indent=2))
print('Generated and validated probability figure.')
# Exact 100%-adult-excess boundary for shading in the paired figure.
edge=[]
for adult in np.r_[np.geomspace(observed*(1+1e-6),1e8,1500),np.inf]:
 pa=np.ones_like(pU) if np.isinf(adult) else expit(eta+np.log(adult))
 fx=(pC-pU)/(pa-pU);f=w@fx
 edge.append({'adult_probability':w@(fx*pa)/f,'early_probability':w@((1-fx)*pU)/(1-f),'adult_share':f})
pd.DataFrame(edge).to_csv(OUT/'probability_full_adult_excess.csv',index=False)
# Zero-adult-excess boundary: adult conditional OR=1, before-18 OR above fitted OR.
edge=[]
for early in np.geomspace(observed*(1+1e-6),100,1500):
 pe=expit(eta+np.log(early));fx=(pC-pe)/(pU-pe);f=w@fx
 assert fx.min()>=0 and fx.max()<=1
 pa_bar=w@(fx*pU)/f;pe_bar=w@((1-fx)*pe)/(1-f)
 assert abs(f*pa_bar+(1-f)*pe_bar-w@pC)<1e-10
 edge.append({'adult_probability':pa_bar,'early_probability':pe_bar,'adult_share':f})
pd.DataFrame(edge).to_csv(OUT/'probability_zero_adult_excess.csv',index=False)
