import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['VECLIB_MAXIMUM_THREADS']='1'
import sys,json,itertools
from pathlib import Path
import numpy as np,pandas as pd
from scipy.special import expit,logsumexp,roots_hermitenorm
from scipy.optimize import minimize
from scipy.integrate import cumulative_trapezoid
from scipy.stats import norm,qmc
ROOT=Path(__file__).resolve().parents[2];REPO=ROOT;OUT=ROOT/'outputs/bayesian/maloney';OUT.mkdir(parents=True,exist_ok=True)
from src.frequentist.maloney import QUESTIONS,recode

def quadrature(d,order):
 q,w=roots_hermitenorm(order);ix=np.array(list(itertools.product(range(order),repeat=d)));return q[ix],np.log(w[ix]).sum(1)-d/2*np.log(2*np.pi)
def setup(frame,terms,outcome):
 X=np.column_stack([np.ones(len(frame))]+[frame[t].to_numpy() for t in terms]);y=frame[outcome].to_numpy();xu,ix=np.unique(X,axis=0,return_inverse=True)
 return xu,np.bincount(ix,weights=y),np.bincount(ix),X

def solve(X,k,n,sd):
 P=np.diag(1/sd**2)
 def f(b):
  eta=X@b;return np.sum(n*np.logaddexp(0,eta)-k*eta)+.5*np.sum((b/sd)**2)
 def jac(b):return X.T@(n*expit(X@b)-k)+P@b
 opt=minimize(f,np.zeros(len(sd)),jac=jac,method='BFGS',options={'gtol':1e-9})
 assert max(abs(jac(opt.x)))<1e-6
 mu=expit(X@opt.x);H=X.T@((n*mu*(1-mu))[:,None]*X)+P
 return opt.x,np.linalg.inv(H),-f(opt.x)

def logtarget(B,X,k,n,sd):
 eta=B@X.T;return eta@k-np.logaddexp(0,eta)@n-.5*((B/sd)**2).sum(1)

def marginal(X,k,n,sd,mode,C,j,order,points):
 others=np.array([i for i in range(len(sd)) if i!=j]);v=C[j,j];s=np.sqrt(v)
 grid=np.linspace(min(mode[j]-12*s,-7*sd[j]),max(mode[j]+12*s,7*sd[j]),points)
 cn=C[np.ix_(others,others)]-np.outer(C[others,j],C[j,others])/v;L=np.linalg.cholesky(cn)
 z,lw=quadrature(len(others),order);noise=z@L.T;logs=[]
 for value in grid:
  m=mode[others]+C[others,j]/v*(value-mode[j]);B=np.empty((len(z),len(sd)));B[:,j]=value;B[:,others]=m+noise
  # Normalizing constants of proposal are constant in the focal grid coordinate.
  logs.append(logsumexp(lw+logtarget(B,X,k,n,sd)+.5*(z*z).sum(1)))
 dens=np.exp(np.array(logs)-max(logs));cdf=np.r_[0,cumulative_trapezoid(dens,grid)];cdf/=cdf[-1]
 assert dens[0]/dens.max()<1e-10 and dens[-1]/dens.max()<1e-10
 return dict(log_median=np.interp(.5,cdf,grid),log_low=np.interp(.025,cdf,grid),log_high=np.interp(.975,cdf,grid),p_positive=1-np.interp(0,grid,cdf))
def weighted_quantile(x,w,qs):
 ix=np.argsort(x);return np.interp(qs,np.cumsum(w[ix]),x[ix])
def rates(X,k,n,sd,mode,C,j,order):
 u=qmc.Sobol(d=len(sd),scramble=True,seed=20261115).random_base2(order);z=norm.ppf(u);lw=np.full(len(z),-np.log(len(z)));B=mode+z@np.linalg.cholesky(C).T;logw=lw+logtarget(B,X,k,n,sd)+.5*(z*z).sum(1);w=np.exp(logw-logsumexp(logw))
 X0=X.copy();X0[:,j]=0;X1=X.copy();X1[:,j]=1
 # For interaction model, changing a main effect also changes its product term.
 if X.shape[1]==4 and j in [1,2]:X0[:,3]=0;X1[:,3]=X1[:,3-j]
 p0=expit(B@X0.T)@(n/n.sum());p1=expit(B@X1.T)@(n/n.sum());r={}
 for key,x in [('prevalence_unexposed',p0),('prevalence_exposed',p1),('difference_pp',100*(p1-p0))]:
  a=weighted_quantile(x,w,[.5,.025,.975]);r.update({key:a[0],key+'_low':a[1],key+'_high':a[2]})
 return r

def main():
 raw=pd.read_excel(REPO/'data/maloney/source.xlsx',sheet_name='umfrageonline-946995');d=raw[list(QUESTIONS.values())].rename(columns={v:k for k,v in QUESTIONS.items()})
 d=d[d.status.eq('participated and completed') & d.circumcised.eq('yes') & d.age.isin(['Birth - 12 months','More than 1 year old - 18 years old'])].copy()
 d['regret']=recode(d.regret,{'No regret':0,'Minimal regret':1,'Moderate regret':1,'Significant regret':1,'Severe regret':1})
 comfort={'Extremely comfortable':0,'Comfortable':0,'Minimal discomfort':1,'Moderate discomfort':1,'Significant discomfort':1}
 for col in ['visibility','partner']:d[col]=recode(d[col],comfort)
 d['masculinity']=recode(d.masculinity,{1:1,2:1,3:1,4:0,5:0,6:0});d=d.dropna(subset=['regret','visibility','masculinity']);assert len(d)==326
 d['interaction']=d.masculinity*d.visibility
 results=[];validation=[]
 for sample,frame in [('primary',d),('sensitivity_325',d.dropna(subset=['partner']))]:
  if sample!='primary':assert len(frame)==325
  specs=[('masculinity_regret',frame,['masculinity'],'regret'),('masculinity_visibility',frame,['masculinity'],'visibility'),('both_neither_regret',frame[frame.masculinity.eq(frame.visibility)],['masculinity'],'regret'),('additive_regret',frame,['masculinity','visibility'],'regret'),('interaction_regret',frame,['masculinity','visibility','interaction'],'regret')]
  for model,f,terms,y in specs:
   X,k,n,_=setup(f,terms,y)
   for prior,scale in [('primary',.5),('skeptical',.25),('broad',1.)]:
    sd=np.array([2.5]+[scale]*len(terms));mode,C,_=solve(X,k,n,sd)
    for j,term in enumerate(terms,1):
     a=marginal(X,k,n,sd,mode,C,j,12,801);b=marginal(X,k,n,sd,mode,C,j,20,1601)
     error=max(abs(a[q]-b[q]) for q in a)
     if error>.001:
      c=marginal(X,k,n,sd,mode,C,j,28,2401);error=max(abs(c[q]-b[q]) for q in b);b=c
     assert error<.001,(sample,model,prior,term,error)
     r=dict(sample=sample,model=model,outcome=y,term=term,prior=prior,n=len(f),events=int(f[y].sum()),**b)
     r.update(odds_ratio=np.exp(b['log_median']),ci_low=np.exp(b['log_low']),ci_high=np.exp(b['log_high']),p_negative=1-b['p_positive'])
     if prior=='primary' and term!='interaction':
      ra=rates(X,k,n,sd,mode,C,j,17);rb=rates(X,k,n,sd,mode,C,j,19)
      # Joint quadrature quantiles are less smooth than directional integration; tolerance 0.15 pp.
      rate_error=max(abs(ra[q]-rb[q])/(100 if q.startswith('difference') else 1) for q in ra)
      if rate_error>.0015:
       rc=rates(X,k,n,sd,mode,C,j,21);rate_error=max(abs(rc[q]-rb[q])/(100 if q.startswith('difference') else 1) for q in rb);rb=rc
      assert rate_error<.0015,(model,term,rate_error)
      r.update(rb)
     results.append(r);validation.append(dict(sample=sample,model=model,prior=prior,term=term,marginal_max_discrepancy=error))
    pd.DataFrame(results).to_csv(OUT/'maloney_results.csv',index=False);print(sample,model,prior,'complete',flush=True)
 (OUT/'maloney_validation.json').write_text(json.dumps(dict(method='direct Bernoulli likelihood; adaptive quadrature; grid/order convergence',checks=validation),indent=2))
if __name__=='__main__':main()
