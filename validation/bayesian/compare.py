from src.bayesian.logistic import *
import json,hashlib,subprocess
from scipy.optimize._numdiff import approx_derivative
from scipy.stats import norm
names={'msm_ever':'m014','identity_gb':'m006','identity_gay':'m055','identity_bi':'m057'}
provenance={'input_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [REPO/'data/analysis.csv.gz',ROOT/'config/analyses.json',ROOT/'validation/bayesian/validation_plan.txt']},'repo_commit':subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()}
(OUT/'provenance.json').write_text(json.dumps(provenance,indent=2));rows=[];batchrows=[];checks=[];jks=[]
if False: # Always rerun validation; never accept stale outputs as evidence.

 rows=pd.read_csv(OUT/'comparison.csv').to_dict('records');batchrows=pd.read_csv(OUT/'integration_batches.csv').to_dict('records');jks=pd.read_csv(OUT/'jackknife.csv').to_dict('records')
 checks=[dict(outcome=r['outcome'],method=r['method'],gradient_checked=True,curvature_identity_checked=True,integration_passed=bool(r['integration_passed'])) for r in rows if r['method']!='original_gaussian']
for oi,(outcome,mid) in enumerate(names.items()):
 if sum(r['outcome']==outcome for r in rows)==3:continue
 X,y,w,codes,cols,z=dataset(outcome);j=cols.index('circ');sd=priors(cols,.5);b,H=fit(X,y,w);V=covariance(X,y,w,codes,b,H)
 old=np.load(ROOT/f'outputs/bayesian/approximation/coefficient_estimates/{mid}.npz');np.testing.assert_allclose(b,old['beta'],atol=1e-7);np.testing.assert_allclose(V,old['covariance'],atol=1e-7);df=int(old['df'])
 cp=components(b,V,sd,df,'normal');su=summarize(cp,j);rows.append(dict(outcome=outcome,method='original_gaussian',OR=np.exp(su['log_median']),low=np.exp(su['log_low']),high=np.exp(su['log_high']),p_positive=su['p_positive']))
 # Independent delete-PSU refits; strata with >2 PSUs handled generally.
 JV=np.zeros_like(V);jkfails=[]
 for ix in strata:
  bb=[]
  for psu in ix:
   wr=w.copy();wr[np.isin(codes,ix)]*=len(ix)/(len(ix)-1);wr[codes==psu]=0
   try:bb.append(fit(X,y,wr,start=b)[0])
   except Exception as ex:jkfails.append(dict(psu=int(psu),error=str(ex)));bb.append(np.full_like(b,np.nan))
  br=np.array(bb);br-=br.mean(0);JV+=(len(ix)-1)/len(ix)*(br.T@br)
 if jkfails:
  jks.append(dict(outcome=outcome,Taylor_SE=np.sqrt(V[j,j]),status='unavailable: sparse-data replicate failure',failed_replicates=len(jkfails)))
  (OUT/f'jackknife_failures_{outcome}.json').write_text(json.dumps(jkfails,indent=2))
 else:
  sj=summarize(components(b,JV,sd,df,'normal'),j);jks.append(dict(outcome=outcome,Taylor_SE=np.sqrt(V[j,j]),jackknife_SE=np.sqrt(JV[j,j]),ratio=np.sqrt(JV[j,j]/V[j,j]),OR=np.exp(sj['log_median']),low=np.exp(sj['log_low']),high=np.exp(sj['log_high']),p_positive=sj['p_positive'],status='estimated',failed_replicates=0))
 # Collapse exact duplicate predictor patterns, retaining weighted sufficient statistics.
 U,inv=np.unique(X,axis=0,return_inverse=True);W=np.bincount(inv,weights=w);Y=np.bincount(inv,weights=w*y)/W
 for kind in ['pseudo','curvature']:
  mode,C,Z,offset,P,fn=target(U,Y,W,b,H,V,sd,kind)
  gn=approx_derivative(lambda v:fn(v)[0],mode+.01,method='3-point').ravel();np.testing.assert_allclose(gn,fn(mode+.01)[1],atol=1e-5,rtol=1e-5)
  Bs=[];Ws=[]
  for batch in range(4):
   B,ww,_,_=importance(U,Y,W,b,H,V,sd,kind,20261113+100*oi+10*(kind=='curvature')+batch)
   Bs.append(B);Ws.append(ww);print(outcome,kind,'batch',batch,'ESS',1/(ww@ww),flush=True)
  B=np.concatenate(Bs);ww=np.concatenate(Ws)/len(Ws)
  if kind=='pseudo':
   # Asymptotic no-prior transformation is tested exactly, then applied to centered proper-prior draws.
   T=root(V)@root(H);np.testing.assert_allclose(T@np.linalg.inv(H)@T.T,V,rtol=1e-7,atol=1e-8);mu=ww@B;B=mu+(B-mu)@T.T
  method='sandwich_adjusted_pseudo' if kind=='pseudo' else 'curvature_adjusted_logistic'
  ss=stats(B,ww,j);br=[]
  for batch in range(4):
   rr=stats(B[batch*32768:(batch+1)*32768],Ws[batch],j);br.append(rr);batchrows.append(dict(outcome=outcome,method=method,batch=batch,**rr))
  ranges={key:np.ptp([v[key] for v in br]) for key in ['OR','low','high','p_positive']}
  passed=bool(ss['ess']>=10000 and ss['max_weight']<.01 and ranges['OR']<.03 and ranges['p_positive']<.01)
  rows.append(dict(outcome=outcome,method=method,**ss,probability_batch_range=ranges['p_positive'],median_batch_range=ranges['OR'],integration_passed=passed))
  checks.append(dict(outcome=outcome,method=method,gradient_checked=True,curvature_identity_checked=True,integration_passed=passed,batch_ranges=ranges))
  np.savez_compressed(OUT/f'draws_{outcome}_{kind}.npz',draws=B,weights=ww,columns=cols)
  print('RESULT',rows[-1],flush=True)
 pd.DataFrame(rows).to_csv(OUT/'comparison.csv',index=False);pd.DataFrame(batchrows).to_csv(OUT/'integration_batches.csv',index=False);pd.DataFrame(jks).to_csv(OUT/'jackknife.csv',index=False)
(OUT/'numerical_checks.json').write_text(json.dumps(checks,indent=2));assert all(v['integration_passed'] for v in checks)
# Importance integrator test against a known multivariate Normal target.
rng=np.random.default_rng(918);p=20;mu=np.linspace(-.2,.2,p);S=np.diag(np.linspace(.1,.3,p)**2);B=multivariate_t.rvs(loc=mu,shape=S,df=8,size=131072,random_state=rng)
from scipy.stats import multivariate_normal
lw=multivariate_normal.logpdf(B,mean=mu,cov=S)-multivariate_t.logpdf(B,loc=mu,shape=S,df=8);ww=np.exp(lw-logsumexp(lw));check=stats(B,ww,0);truth=norm.cdf(mu[0]/np.sqrt(S[0,0]));assert abs(check['p_positive']-truth)<.005;assert abs(np.log(check['OR'])-mu[0])<.005
(OUT/'integrator_known_target.json').write_text(json.dumps(dict(**check,true_p_positive=truth,passed=True),indent=2))
print('DONE',flush=True)
