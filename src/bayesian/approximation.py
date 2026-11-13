import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['VECLIB_MAXIMUM_THREADS']='1'
import sys,json,hashlib,subprocess
from pathlib import Path
import numpy as np,pandas as pd,patsy,statsmodels.api as sm
from scipy.special import expit,roots_genlaguerre,logsumexp
from scipy.stats import norm
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[2];REPO=ROOT;OUT=ROOT/'outputs/bayesian/approximation';OUT.mkdir(parents=True,exist_ok=True)
from src.survey.design import Survey
from src.specification import ADJUST
rng=np.random.default_rng(20261114)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def priors(cols,scale,nuisance=1):
 sd=[]
 for c in cols:
  if c in ['circ','circ:identity_gb']:s=scale
  elif c=='Intercept':s=2.5*nuisance
  elif c=='I(age10 ** 2)':s=.5*nuisance
  else:s=1*nuisance
  sd.append(s)
 return np.array(sd)
def components(b,V,sd,df,likelihood,nodes=100):
 D=np.diag(sd**2);prec=np.diag(1/sd**2);Vi=np.linalg.inv(V)
 if likelihood=='normal':lams=np.array([1.]);logweights=np.array([0.])
 else:
  q,w=roots_genlaguerre(nodes,df/2-1);lams=q/(df/2);logweights=np.log(w)
 mus=[];covs=[];lw=[]
 for lam,logw in zip(lams,logweights):
  C=np.linalg.inv(lam*Vi+prec);m=C@(lam*Vi@b);S=V/lam+D
  lw.append(logw-.5*(np.linalg.slogdet(S)[1]+b@np.linalg.solve(S,b)))
  mus.append(m);covs.append(C)
 lw=np.array(lw);weights=np.exp(lw-logsumexp(lw));return np.array(mus),np.array(covs),weights

def summarize(comp,j):
 m,C,w=comp;s=np.sqrt(C[:,j,j]);mu=m[:,j]
 p=float(w@norm.cdf(mu/s))
 def quant(q):return brentq(lambda z:w@norm.cdf((z-mu)/s)-q,float(min(mu-12*s)),float(max(mu+12*s)))
 return dict(log_median=quant(.5),log_low=quant(.025),log_high=quant(.975),p_positive=p,p_negative=1-p)
def scalar_posterior(beta,se,sd,df,likelihood,bound=np.inf):
 if likelihood=='normal':
  v=1/(1/se**2+1/sd**2);m=v*beta/se**2
  return dict(log_median=m,log_low=m+norm.ppf(.025)*np.sqrt(v),log_high=m+norm.ppf(.975)*np.sqrt(v),p_positive=norm.cdf(m/np.sqrt(v)),p_negative=norm.cdf(-m/np.sqrt(v)))
 from scipy.integrate import quad
 from scipy.stats import t
 # Standardize to the sampling SE so integration cannot miss a narrow likelihood peak.
 def logf(z):return t.logpdf(z,df)-.5*((beta+se*z)/sd)**2
 peak=logf(0)
 def density(z):return np.exp(logf(z)-peak)
 def integrate(lo,hi):
  points=[lo]+[q for q in [-10.,-1.,0.,1.,10.] if lo<q<hi]+[hi]
  return sum(quad(density,a,b,epsabs=1e-12,epsrel=1e-10,limit=300)[0] for a,b in zip(points[:-1],points[1:]))
 lower=(-bound-beta)/se;upper=(bound-beta)/se
 Z=integrate(lower,upper)
 def cdf(x):return integrate(lower,(x-beta)/se)/Z
 p=1-cdf(0);lo=-min(bound,12*sd+abs(beta));hi=min(bound,12*sd+abs(beta))
 return dict(log_median=brentq(lambda x:cdf(x)-.5,lo,hi),log_low=brentq(lambda x:cdf(x)-.025,lo,hi),log_high=brentq(lambda x:cdf(x)-.975,lo,hi),p_positive=p,p_negative=1-p)

def sample(comp,n):
 m,C,w=comp;ix=rng.choice(len(w),n,p=w);d=np.empty((n,len(m[0])))
 for k in np.unique(ix):
  hit=np.flatnonzero(ix==k);d[hit]=rng.multivariate_normal(m[k],C[k],len(hit))
 return d

def standardize(comp,X,w,j,n=6000):
 draws=sample(comp,n);X0=X.copy();X0[:,j]=0
 # Interactions require subgroup-specific standardization; not averaged as a single exposure shift.
 ps0=[];ps1=[];weights=w/w.sum()
 for start in range(0,n,100):
  B=draws[start:start+100];eta=X0@B.T;ps0.extend(weights@expit(eta));ps1.extend(weights@expit(eta+B[:,j]))
 p0=np.array(ps0);p1=np.array(ps1);r={}
 for name,a in [('prevalence_uncirc',p0),('prevalence_circ',p1),('difference_pp',100*(p1-p0))]:
  r.update({name:np.median(a),name+'_low':np.quantile(a,.025),name+'_high':np.quantile(a,.975)})
 return r

def fit(d,mask,formula):
 s=Survey(d);y,x=patsy.dmatrices(formula,d.loc[mask & d.eligible],return_type='dataframe');idx=x.index.to_numpy();X=x.to_numpy();Y=y.iloc[:,0].to_numpy();w=d.loc[idx,'weight'].to_numpy();w=w/w.mean()
 if np.linalg.matrix_rank(X)<X.shape[1]:raise ValueError('rank deficient')
 fit=sm.GLM(Y,X,family=sm.families.Binomial(),freq_weights=w).fit(tol=1e-11,maxiter=100)
 if not fit.converged:raise ValueError('not converged')
 mu=fit.fittedvalues;H=X.T@((w*mu*(1-mu))[:,None]*X)
 if np.linalg.cond(H)>=1e10:raise ValueError('unstable information')
 inv=np.linalg.inv(H);score=X*(w*(Y-mu))[:,None];influence=np.zeros((len(d),len(x.columns)));influence[idx]=score@inv;V=s.covariance(influence)
 np.linalg.cholesky(V);domain=np.zeros(len(d),bool);domain[idx]=True;df=s.domain_df(domain)-X.shape[1]+1
 if df<=0:raise ValueError('nonpositive df')
 assert np.max(abs(score.sum(0)))<1e-6
 sc=np.zeros_like(influence);sc[idx]=score;np.testing.assert_allclose(V,inv@s.covariance(sc)@inv,rtol=1e-7,atol=1e-10)
 return np.asarray(fit.params),V,list(x.columns),df,X,w,Y

def main():
 # Validation simulations are an explicit separate stage; failures remain documented.
 manifest=json.loads((REPO/'config/sources.json').read_text());verified=[]
 for r in manifest:
  p=REPO/r['path'];assert digest(p)==r['sha256'],p;verified.append(r['path'])
 provenance=dict(source_files_verified=verified,repo_commit=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),working_tree=subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True),hashes={str(p.relative_to(ROOT)):digest(p) for p in list((REPO/'scripts').glob('*.*'))+list((REPO/'data').glob('*.gz'))+[ROOT/'config/analyses.json']})
 (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2))
 d=pd.read_csv(REPO/'data/analysis.csv.gz');beh=pd.read_csv(REPO/'data/behavior_extension.csv.gz')
 specs=[]
 def add(data,mask,row,family,grid=False,focus='circ',standard=False):
  i=len(specs);specs.append(dict(id=f'm{i:03d}',data=data,mask=np.asarray(mask),reference=row,family=family,grid=grid,focus=focus,standard=standard))
 for _,row in pd.read_csv(REPO/'outputs/frequentist/models.csv').iterrows():
  mask=d.eligible.copy()
  if row['sample']=='full_model_complete_cases':mask &= d[['circ','age10','cycle','race','education','foreign_born',row.outcome]].notna().all(axis=1)
  grid=row.model=='full' and row['sample']=='available_for_model';add(d,mask,row,'headline' if grid else 'adjustment',grid,standard=grid)
 for _,row in pd.read_csv(REPO/'outputs/frequentist/sensitivities.csv').iterrows():
  label=row.model;mask=d.eligible.copy()
  if label=='exclude_2015_2016':mask &= d.year<2015
  elif label=='direct_behavior_2009_2016':mask &= d.year>=2009
  elif label=='us_born_only':mask &= d.foreign_born.eq(0)
  elif label=='identity_behavior_common_sample':mask &= d.identity_gb.notna() & d.msm_ever.notna()
  elif label=='sexually_experienced':mask &= d.sex_ever.eq(1)
  elif label.startswith('leave_out_'):mask &= d.year.ne(int(label.split('_')[-1]))
  elif label.startswith('cycle_'):mask &= d.year.eq(int(label.split('_')[-1]))
  grid=row.outcome in ['identity_gay','identity_bi'] and label=='full';add(d,mask,row,'headline' if grid else 'sensitivity',grid,standard=grid)
 for _,row in pd.read_csv(REPO/'outputs/frequentist/behavior_extension/models.csv').iterrows():
  mask=beh.eligible.copy()
  if row.population=='lifetime_msm':mask &= beh.SXQ809.eq(1)
  if row['sample']=='full_model_complete_cases':mask &= beh[['circ','age10','cycle','race','education','foreign_born',row.outcome]].notna().all(axis=1)
  grid=row.model=='full' and row['sample']=='available_for_model';add(beh,mask,row,'behavior' if grid else 'behavior_adjustment',grid,standard=grid)
 for _,row in pd.read_csv(REPO/'outputs/frequentist/identity_subgroups/models.csv').iterrows():
  z=d[d.year.ge(2009)].copy().reset_index(drop=True) if row.period=='2009_2016' else d
  mask=z.identity_gb.eq(0 if row.group=='heterosexual' else 1)
  if row['sample']=='fixed_complete':mask &= z[['circ','msm_ever','age10','cycle','race','education','foreign_born']].notna().all(axis=1)
  grid=row.model=='full' and row['sample']=='available';add(z,mask,row,'subgroup' if grid else 'subgroup_adjustment',grid,standard=grid)
 for _,row in pd.read_csv(REPO/'outputs/frequentist/identity_subgroups/interactions.csv').iterrows():
  z=d[d.year.ge(2009)].copy().reset_index(drop=True) if row.period=='2009_2016' else d
  row=row.copy();row['outcome']='msm_ever';row['model']='interaction';add(z,z.eligible,row,'interaction',True,'circ:identity_gb')
 manifest=[]
 for sp in specs:
  r=sp['reference'].to_dict();r={k:(None if pd.isna(v) else v) for k,v in r.items()}
  manifest.append(dict(id=sp['id'],family=sp['family'],grid=sp['grid'],focus=sp['focus'],mask_sha256=hashlib.sha256(sp['mask'].tobytes()).hexdigest(),reference=r))
 (OUT/'model_manifest.json').write_text(json.dumps(manifest,indent=2))
 # Prior predictive checks before fitting outcome models; only covariate design is used.
 pre=[]
 for sp in [s for s in specs if s['family']=='headline']:
  row=sp['reference'];_,x=patsy.dmatrices(row.formula,sp['data'].loc[sp['mask'] & sp['data'].eligible],return_type='dataframe');sd=priors(list(x.columns),.5)
  B=rng.normal(size=(2000,len(sd)))*sd;ix=rng.choice(len(x),min(1000,len(x)),replace=False);rates=expit(x.to_numpy()[ix]@B.T).mean(0)
  pre.append(dict(id=sp['id'],outcome=row.outcome,prevalence_q025=float(np.quantile(rates,.025)),prevalence_median=float(np.median(rates)),prevalence_q975=float(np.quantile(rates,.975)),note='Broad baseline prior intentionally not calibrated to observed event prevalence'))
 (OUT/'prior_predictive_checks.json').write_text(json.dumps(pre,indent=2))
 results=[];checks=[];failures=[];(OUT/'coefficient_estimates').mkdir(exist_ok=True)
 for sp in specs:
  row=sp['reference'];meta={k:row[k] for k in ['outcome','model','sample','population','group','period'] if k in row};meta.update(id=sp['id'],family=sp['family'],focus=sp['focus'])
  try:
   b,V,cols,df,X,w,Y=fit(sp['data'],sp['mask'],row.formula);j=cols.index(sp['focus'])
   np.testing.assert_allclose([b[j],np.sqrt(V[j,j])],[row.beta,row.se],atol=1e-8,rtol=1e-7);assert len(Y)==int(row.n) and int(Y.sum())==int(row.events)
   if 'residual_df' in row:assert df==row.residual_df
   np.savez_compressed(OUT/'coefficient_estimates'/f'{sp["id"]}.npz',beta=b,covariance=V,columns=cols,df=df)
   # Scale invariance algebra checked by independent bread-meat order above.
   broad=components(b,V,np.full(len(b),1e6),df,'normal');np.testing.assert_allclose(broad[0][0],b,atol=1e-6);np.testing.assert_allclose(broad[1][0],V,atol=1e-6)
   grids=[('primary',.5,'normal',1)]
   if sp['grid']:grids=[(name,scale,lik,1) for name,scale in [('primary',.5),('skeptical',.25),('broad',1.)] for lik in ['normal','t']]+[('nuisance_broad',.5,'normal',2)]
   for name,scale,lik,nuis in grids:
    comp=components(b,V,priors(cols,scale,nuis),df,lik);su=summarize(comp,j)
    if lik=='t':
     check=summarize(components(b,V,priors(cols,scale,nuis),df,lik,nodes=180),j)
     assert max(abs(check[k]-su[k]) for k in su)<1e-5,'quadrature disagreement'
    rec=dict(**meta,n=len(Y),events=int(Y.sum()),df=df,prior=name,likelihood=lik,**su)
    rec.update(odds_ratio=np.exp(su['log_median']),ci_low=np.exp(su['log_low']),ci_high=np.exp(su['log_high']))
    if sp['standard'] and name=='primary' and lik=='normal':rec.update(standardize(comp,X,w,cols.index('circ')))
    results.append(rec)
   checks.append(dict(id=sp['id'],reference_match=True,n=len(Y),events=int(Y.sum()),df=df,min_covariance_eigenvalue=float(np.linalg.eigvalsh(V).min())))
  except Exception as e:
   failures.append(dict(**meta,error=repr(e)));print('FAIL',failures[-1],flush=True)
  pd.DataFrame(results).to_csv(OUT/'nhanes_results.csv',index=False);pd.DataFrame(failures).to_csv(OUT/'nhanes_failures.csv',index=False)
  print(sp['id'],meta, 'complete',flush=True)
 # Existing linked jackknife contrasts, specified scalar likelihoods.
 explanatory=[]
 for _,r in pd.read_csv(REPO/'outputs/frequentist/explanations/focal_tests.csv').iterrows():
  if r.status!='estimated':failures.append(dict(family='explanation',error='reference not estimable',comparison=r.comparison));continue
  b=np.array([r.point_on_test_scale]);V=np.array([[r.se**2]])
  for name,factor in [('primary',1.),('skeptical',.5),('broad',2.)]:
   sd=(.05 if r.scale=='identity' else .5)*factor
   for lik in ['normal','t']:
    su=scalar_posterior(r.point_on_test_scale,r.se,sd,r.df,lik,2 if r.scale=='identity' else np.inf)
    # Bounds [-2,2] on difference-of-differences have negligible mass for these priors.
    assert r.scale!='identity' or norm.cdf(-2/sd)+norm.sf(2/sd)<1e-80
    rec=dict(era=r.era,test=r.test,comparison=r.comparison,n=r.n,scale=r.scale,prior=name,likelihood=lik,**su)
    transform=np.exp if r.scale=='ratio' else lambda v:100*v
    rec.update(estimate=transform(su['log_median']),low=transform(su['log_low']),high=transform(su['log_high']))
    explanatory.append(rec)
 pd.DataFrame(explanatory).to_csv(OUT/'explanatory_results.csv',index=False)
 (OUT/'nhanes_validation.json').write_text(json.dumps(dict(checked_models=checks,failures=failures,source_files_verified=len(verified),approximation='full-vector design-based Gaussian likelihood; t sensitivity by gamma-mixture quadrature',standardization='conditional empirical covariate distribution; 6000 independent draws'),indent=2))
 print('FINISHED',len(results),'rows',len(failures),'failures',flush=True)
if __name__=='__main__':main()
