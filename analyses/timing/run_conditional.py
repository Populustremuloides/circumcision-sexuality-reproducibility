import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import sys,numpy as np,pandas as pd,patsy
from scipy.special import expit
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/timing';REPO=ROOT;OUT.mkdir(parents=True,exist_ok=True)
from src.frequentist.nhanes import ADJUST
D=pd.read_csv(REPO/'data/analysis.csv.gz');rng=np.random.default_rng(20261115);rows=[];infants=[]
for pop in ['all','us_born']:
 for outcome in ['msm_ever','identity_gb','identity_gay','identity_bi']:
  if not (OUT/f'model_{pop}_{outcome}.npz').exists():
   print('UNAVAILABLE MODEL',pop,outcome,flush=True);continue
  mask=D.eligible & (True if pop=='all' else D.foreign_born.eq(0));formula=outcome+' ~ '+ADJUST['full'];formula=formula.replace(' + foreign_born','') if pop=='us_born' else formula
  yy,xx=patsy.dmatrices(formula,D.loc[mask],return_type='dataframe');z=D.loc[xx.index];keep=z.circ.eq(1);w=z.loc[keep,'weight'].to_numpy();w/=w.sum();X=xx.to_numpy()[keep];j=list(xx.columns).index('circ');X[:,j]=0
  cache=np.load(OUT/f'model_{pop}_{outcome}.npz');B=rng.multivariate_normal(cache['posterior_mean'],cache['posterior_cov'],2000)
  specs=[(fi,fk,fa,ra,rk) for fi,fk,fa in [(1,0,0),(.98,0,.02),(.95,0,.05),(.9,0,.1),(.8,0,.2),(.5,0,.5),(.8,.1,.1),(.8,.15,.05),(.5,.4,.1)] for ra in [1,5,20,np.inf] for rk in [1,3] if (fa>0 or ra==1) and(fk>0 or rk==1)]
  arr={s:[[],[],[]] for s in specs}
  for start in range(0,len(B),100):
   bb=B[start:start+100];eta=X@bb.T;p0=expit(eta);pc=expit(eta+bb[:,j]);pu=w@p0
   pa={r:np.ones_like(p0) if np.isinf(r) else expit(eta+np.log(r)) for r in [1,5,20,np.inf]};pk={r:expit(eta+np.log(r)) for r in [1,3]}
   for s in specs:
    fi,fk,fa,ra,rk=s;pi=(pc-fa*pa[ra]-fk*pk[rk])/fi;avg=w@pi;valid=((pi>=0)&(pi<=1)).all(0);arr[s][0].extend(avg);arr[s][1].extend(valid);arr[s][2].extend(pu)
  for s,(pi,valid,pu) in arr.items():
   pi=np.array(pi);valid=np.array(valid);pu=np.array(pu);fi,fk,fa,ra,rk=s;meta=dict(population=pop,outcome=outcome,fI=fi,fK=fk,fA=fa,OR_A=ra,OR_K=rk)
   rows.append(dict(**meta,p_feasible=float(valid.mean()),p_positive_and_feasible=float(((pi>pu)&valid).mean()),p_negative_and_feasible=float(((pi<pu)&valid).mean()),p_infeasible=float((~valid).mean()),draws=len(B)))
   if ra==1 and rk==1:
    marginal_valid=(pi>0)&(pi<1);OR=(pi/(1-pi))/(pu/(1-pu));r=dict(**meta,p_feasible=float(valid.mean()),p_positive_and_feasible=float(((pi>pu)&valid).mean()))
    # Quantiles use all draws, never discard infeasible draws. Only transform if all marginal risks valid.
    if marginal_valid.all():r.update(marginal_OR=np.median(OR),low=np.quantile(OR,.025),high=np.quantile(OR,.975))
    infants.append(r)
  print(pop,outcome,'done',flush=True)
pd.DataFrame(rows).to_csv(OUT/'mixed_conditional_probabilities.csv',index=False);pd.DataFrame(infants).to_csv(OUT/'infant_only_intervals.csv',index=False)
