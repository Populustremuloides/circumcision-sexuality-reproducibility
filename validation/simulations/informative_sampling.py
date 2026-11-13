import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['VECLIB_MAXIMUM_THREADS']='1'
import numpy as np, pandas as pd, json
from scipy.special import expit,logit
from scipy.optimize import brentq
from scipy.stats import norm
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'outputs/validation/simulations';OUT.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(20261113)
def fit(X,y,w):
 b=np.zeros(X.shape[1]);b[0]=logit(np.average(y,weights=w))
 for _ in range(60):
  mu=expit(X@b); H=X.T@((w*mu*(1-mu))[:,None]*X);step=np.linalg.solve(H,X.T@(w*(y-mu)));b+=step
  if max(abs(step))<1e-8:break
 else:raise ValueError('convergence')
 return b,np.linalg.inv(H),X*(w*(y-expit(X@b)))[:,None]
rows=[]
for prevalence in [.02,.06]:
 for effect in [0,np.log(1.5)]:
  for cluster_sd in [.2,.8]:
   for informative in [False,True]:
    N=60*20*150;unit=np.repeat(np.arange(1200),150);c=rng.binomial(1,.75,N);a=rng.normal(size=N)
    X=np.column_stack([np.ones(N),c,a]);u=rng.normal(0,cluster_sd,1200)[unit]
    offset=effect*c+.2*a+u;intercept=brentq(lambda z:expit(z+offset).mean()-prevalence,-10,3)
    y=rng.binomial(1,expit(intercept+offset));truth=fit(X,y,np.ones(N))[0][1]
    score=.5*c+.7*y if informative else np.zeros(N)
    # Poisson inclusion odds as specified, calibrated to 50% expected participation.
    shift=brentq(lambda z:expit(z+score).mean()-.5,-5,5);pi=expit(shift+score)
    estimates=[];ses=[];posterior_means=[];posterior_sds=[];failed=0
    for rep in range(500):
     units=np.array([rng.choice(np.arange(h*20,(h+1)*20),2,replace=False) for h in range(60)]).ravel()
     ix=(units[:,None]*150+np.arange(150)).ravel();keep=rng.random(len(ix))<pi[ix];ix=ix[keep]
     codes=np.repeat(np.arange(120),150)[keep]
     try:
      b,inv,scores=fit(X[ix],y[ix],1/pi[ix]);totals=np.zeros((120,3));np.add.at(totals,codes,scores)
      dif=totals[::2]-totals[1::2];V=inv@(dif.T@dif)@inv;se=np.sqrt(V[1,1]);assert np.isfinite(se) and se>0
      estimates.append(b[1]);ses.append(se)
      P=np.diag(1/np.array([2.5,1.,1.])**2);Vi=np.linalg.inv(V);C=np.linalg.inv(Vi+P);m=C@Vi@b;posterior_means.append(m[1]);posterior_sds.append(np.sqrt(C[1,1]))
     except Exception:failed+=1
    b=np.array(estimates);se=np.array(ses);covered=abs(b-truth)<=norm.ppf(.975)*se
    reference_coverage=covered.mean();covered=abs(np.array(posterior_means)-truth)<=norm.ppf(.975)*np.array(posterior_sds);coverage=covered.mean();rows.append(dict(prevalence=prevalence,generating_logOR=effect,cluster_sd=cluster_sd,informative=informative,truth=truth,repetitions=500,failures=failed,bias=float((b-truth).mean()),flat_prior_coverage=reference_coverage,broad_prior_bias=float((np.array(posterior_means)-truth).mean()),coverage=coverage,coverage_mcse=np.sqrt(coverage*(1-coverage)/len(b)),passed=bool(coverage>=.9 and failed<=25)))
    pd.DataFrame(rows).to_csv(OUT/'simulation_validation.csv',index=False)
    print(rows[-1],flush=True)
# Calibration in the actual working normal-likelihood model, not a claim about unknown confounding.
truth=rng.normal(0,.5,100000);se=.25;observed=truth+rng.normal(0,se,len(truth));v=1/(1/.5**2+1/se**2);m=v*observed/se**2;p=norm.cdf(m/np.sqrt(v))
cal=[]
for lo,hi in zip(np.arange(0,1,.1),np.arange(.1,1.01,.1)):
 ix=(p>=lo)&(p<hi);cal.append(dict(lower=lo,upper=hi,n=int(ix.sum()),mean_probability=float(p[ix].mean()),positive_fraction=float((truth[ix]>0).mean())))
pd.DataFrame(cal).to_csv(OUT/'prior_predictive_calibration.csv',index=False)
(OUT/'simulation_gate.json').write_text(json.dumps(dict(passed=all(r['passed'] for r in rows),scenarios=16,repetitions=8000,seed=20261113,scope='fixed synthetic populations, 60 strata, 2 sampled PSUs of 20 per stratum, Poisson within-PSU sampling; calibration conditional on working normal model'),indent=2))
assert all(r['passed'] for r in rows),'Simulation gate failed; amend method before interpreting results.'
