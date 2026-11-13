from src.bayesian.logistic import *
from scipy.stats import norm,skew
import json
rng=np.random.default_rng(20261116);records=[];summary=[];failures=[]
for oi,outcome in enumerate(['msm_ever','identity_gb','identity_gay','identity_bi']):
 X,y,w,codes,cols,z=dataset(outcome);j=cols.index('circ');sd=priors(cols,.5);b0,H0=fit(X,y,w)
 for trueOR in [1.,1.5]:
  bt=b0.copy();bt[j]=np.log(trueOR);prob=expit(X@bt);threshold=norm.ppf(prob)
  for rho in [0.,.03]:
   meta=dict(outcome=outcome,true_OR=trueOR,latent_cluster_correlation=rho);local=[]
   for rep in range(250):
    latent=np.sqrt(rho)*rng.normal(size=len(units))[codes]+np.sqrt(1-rho)*rng.normal(size=len(y));ys=(latent<threshold).astype(float)
    try:
     pm,PC,*_=target(X,ys,w,bt,H0,np.eye(len(bt)),sd,'pseudo')
     mup=expit(X@pm);HP=X.T@((w*mup*(1-mup))[:,None]*X);VP=covariance(X,ys,w,codes,pm,HP);TP=root(VP)@root(HP);PC=TP@PC@TP.T
     mean=pm[j];sdj=np.sqrt(PC[j,j]);rec=dict(**meta,replicate=rep,method='posterior_plugin_pseudo_laplace',mean=mean,sd=sdj,covered=abs(mean-bt[j])<=norm.ppf(.975)*sdj,p_positive=norm.cdf(mean/sdj),events=ys.sum());records.append(rec);local.append(rec)
    except Exception as ex:failures.append(dict(**meta,replicate=rep,method='posterior_plugin_pseudo_laplace',error=str(ex)))
    try:
     b,H=fit(X,ys,w,start=bt);V=covariance(X,ys,w,codes,b,H);np.linalg.cholesky(V);P=np.diag(1/sd**2);C=np.linalg.inv(np.linalg.inv(V)+P);m=C@np.linalg.solve(V,b)
     results={'original_gaussian':(m[j],np.sqrt(C[j,j])),'frequentist_normal':(b[j],np.sqrt(V[j,j]))}
     for kind in ['pseudo','curvature']:
      bm,BC,*_=target(X,ys,w,b,H,V,sd,kind)
      if kind=='pseudo':T=root(V)@root(H);BC=T@BC@T.T
      results[kind+'_laplace']=(bm[j],np.sqrt(BC[j,j]))
     for method,(mean,sdj) in results.items():
      p=norm.cdf(mean/sdj);rec=dict(**meta,replicate=rep,method=method,mean=mean,sd=sdj,covered=abs(mean-bt[j])<=norm.ppf(.975)*sdj,p_positive=p,events=ys.sum());records.append(rec);local.append(rec)
    except Exception as ex:failures.append(dict(**meta,replicate=rep,method='MLE_dependent_methods',error=str(ex)))
   df=pd.DataFrame(local)
   for method,g in df.groupby('method'):
    cov=g.covered.mean();summary.append(dict(**meta,method=method,successful=len(g),attempts=250,bias=g['mean'].mean()-bt[j],coverage=cov,coverage_MCSE=np.sqrt(cov*(1-cov)/len(g)),mean_SE=g.sd.mean(),empirical_SD=g['mean'].std(),skew=skew(g['mean']),p_above_975=(g.p_positive>.975).mean(),p_below_025=(g.p_positive<.025).mean()))
   pd.DataFrame(summary).to_csv(OUT/'simulation_summary.csv',index=False);pd.DataFrame(failures).to_csv(OUT/'simulation_failures.csv',index=False);pd.DataFrame(records).to_csv(OUT/'simulation_replicates.csv.gz',index=False)
   print(meta,'complete; total failures',len(failures),flush=True)
print('DONE',flush=True)
