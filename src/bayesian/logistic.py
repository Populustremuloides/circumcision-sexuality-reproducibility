import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['VECLIB_MAXIMUM_THREADS']='1'
from pathlib import Path
import sys,numpy as np,pandas as pd,patsy
from scipy.special import expit,logsumexp
from scipy.optimize import minimize
from scipy.stats import multivariate_t
ROOT=Path(__file__).resolve().parents[2];REPO=ROOT;OUT=ROOT/'outputs/validation/bayesian';OUT.mkdir(parents=True,exist_ok=True)
from src.bayesian.approximation import priors,components,summarize
from src.specification import ADJUST,ANALYSES
D=pd.read_csv(REPO/'data/analysis.csv.gz');units=D[['stratum','psu']].drop_duplicates().sort_values(['stratum','psu']);strata=list(units.groupby('stratum',sort=False).indices.values())
def root(M,power=.5):
 v,u=np.linalg.eigh(M)
 if v.min()<=0:raise ValueError('nonpositive eigenvalue')
 return (u*v**power)@u.T

def dataset(outcome):
 y,x=patsy.dmatrices(ANALYSES['nhanes.'+outcome+'.adjusted']['formula'],D.loc[D.eligible],return_type='dataframe');z=D.loc[x.index];w=z.weight.to_numpy();w/=w.mean();codes=pd.Categorical(z.psu,categories=units.psu).codes
 return x.to_numpy(),y.iloc[:,0].to_numpy(),w,codes,list(x.columns),z

def fit(X,y,w,start=None):
 b=np.zeros(X.shape[1]) if start is None else start.copy()
 if start is None:b[0]=np.log(np.average(y,weights=w)/(1-np.average(y,weights=w)))
 def ll(b):
  eta=X@b;return np.sum(w*(y*eta-np.logaddexp(0,eta)))
 for _ in range(80):
  mu=expit(X@b);H=X.T@((w*mu*(1-mu))[:,None]*X);score=X.T@(w*(y-mu))
  if np.linalg.cond(H)>1e10:raise ValueError('unstable information')
  step=np.linalg.solve(H,score);alpha=1;old=ll(b)
  while alpha>1e-6 and ll(b+alpha*step)<old-1e-9:alpha/=2
  b+=alpha*step
  if np.max(abs(score))<1e-7:return b,H
 raise ValueError('fit convergence')

def covariance(X,y,w,codes,b,H):
 scores=X*(w*(y-expit(X@b)))[:,None];totals=np.zeros((len(units),X.shape[1]));np.add.at(totals,codes,scores);J=np.zeros_like(H)
 for ix in strata:
  v=totals[ix]-totals[ix].mean(0);J+=len(ix)/(len(ix)-1)*v.T@v
 Hi=np.linalg.inv(H);return Hi@J@Hi

def target(X,y,w,b,H,V,sd,kind):
 A=np.eye(len(b)) if kind=='pseudo' else root(H,-.5)@root(V,-.5)
 if kind!='pseudo':np.testing.assert_allclose(A.T@H@A,np.linalg.inv(V),rtol=1e-7,atol=1e-6)
 Z=X@A;offset=X@b-Z@b;P=np.diag(1/sd**2)
 def fun(beta):
  eta=offset+Z@beta;mu=expit(eta);f=np.sum(w*(np.logaddexp(0,eta)-y*eta))+.5*beta@P@beta
  g=Z.T@(w*(mu-y))+P@beta
  return f,g
 def hess(beta):
  mu=expit(offset+Z@beta);return Z.T@((w*mu*(1-mu))[:,None]*Z)+P
 opt=minimize(fun,b,jac=True,hess=hess,method='trust-exact',options={'gtol':1e-8,'maxiter':100})
 if np.max(abs(fun(opt.x)[1]))>1e-5:raise ValueError('posterior optimizer gradient')
 C=np.linalg.inv(hess(opt.x))
 return opt.x,C,Z,offset,P,fun

def importance(X,y,w,b,H,V,sd,kind,seed,n=32768):
 mode,C,Z,offset,P,fun=target(X,y,w,b,H,V,sd,kind);rng=np.random.default_rng(seed)
 draws=multivariate_t.rvs(loc=mode,shape=C,df=8,size=n,random_state=rng);lp=[]
 for k in range(0,n,128):
  B=draws[k:k+128];eta=offset[:,None]+Z@B.T
  lp.extend(w@(y[:,None]*eta-np.logaddexp(0,eta))-.5*np.einsum('ij,jk,ik->i',B,P,B))
 lw=np.array(lp)-multivariate_t.logpdf(draws,loc=mode,shape=C,df=8);ww=np.exp(lw-logsumexp(lw))
 return draws,ww,mode,C

def stats(draws,w,j):
 vals=draws[:,j];ix=np.argsort(vals);qs=np.interp([.025,.5,.975],np.cumsum(w[ix])-.5*w[ix],vals[ix]);return dict(OR=np.exp(qs[1]),low=np.exp(qs[0]),high=np.exp(qs[2]),p_positive=float(w@(vals>0)),ess=1/np.sum(w*w),max_weight=w.max())
