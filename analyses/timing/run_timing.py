import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['VECLIB_MAXIMUM_THREADS']='1'
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd,patsy
from scipy.special import expit,logit
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'outputs/timing'; REPO=ROOT; OUT.mkdir(parents=True,exist_ok=True)
from src.bayesian.approximation import fit,components,priors,sample,summarize,ADJUST
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [REPO/'data/analysis.csv.gz',ROOT/'analyses/timing/extraction_addendum.txt',ROOT/'config/analyses.json',ROOT/'analyses/timing/source_values.json',ROOT/'analyses/timing/sources.json']}}
(OUT/'provenance.json').write_text(json.dumps(manifest,indent=2))
# Clear generated model caches and failure logs so unsuccessful new fits cannot reuse old files.
for cached in OUT.glob('model_*.npz'):cached.unlink()
(OUT/'model_failures.jsonl').write_text('')
d=pd.read_csv(REPO/'data/analysis.csv.gz');d['birth_early']=d.year-d.RIDAGEYR-1;d['birth_late']=d.year+1-d.RIDAGEYR
source_values=json.loads((ROOT/'analyses/timing/source_values.json').read_text())
rates={int(year):percent/100 for year,percent in source_values['newborn']['values'].items()}
counts=source_values['procedures']['counts']
pd.DataFrame({'birth_year':rates.keys(),'hospital_neonatal_rate':rates.values()}).to_csv(OUT/'newborn_source_extract.csv',index=False)
coverage=[];stocks=[];main=[];required=[];fixed=[];probs=[];raw=[];mixed=[];checks=[]
fractions=np.unique(np.r_[.001,.0025,.005,np.arange(1,101)/100])
def stock(t,threshold):
 bands=[(max(threshold,15),44,counts['15to44']),(45,64,counts['45to64'])]
 if threshold<15:bands.insert(0,(threshold,14,counts['under15']))
 return sum(n for s in range(t-60,t+1) for lo,hi,n in bands if max(lo,20-(t-s))<=min(hi,60-(t-s)))
def q(a):return dict(median=float(np.median(a)),low=float(np.quantile(a,.025)),high=float(np.quantile(a,.975)))
for population in ['all','us_born']:
 for outcome in ['msm_ever','identity_gb','identity_gay','identity_bi']:
  mask=d.eligible & (True if population=='all' else d.foreign_born.eq(0))
  formula=outcome+' ~ '+ADJUST['full'].replace(' + foreign_born','') if population=='us_born' else outcome+' ~ '+ADJUST['full']
  yy,xx=patsy.dmatrices(formula,d.loc[mask],return_type='dataframe');z=d.loc[xx.index].copy();w=z.weight.to_numpy();isc=z.circ.to_numpy()==1;wc=w[isc]/w[isc].sum();X=xx.to_numpy()[isc];j=list(xx.columns).index('circ');X[:,j]=0
  meta=dict(population=population,outcome=outcome)
  try:b,V,cols,df,_,_,_=fit(d,mask,formula)
  except Exception as ex:
   with (OUT/'model_failures.jsonl').open('a') as fh:fh.write(json.dumps(dict(**meta,error=str(ex)))+'\n')
   print('FAILED',meta,str(ex),flush=True);continue
  comp=components(b,V,priors(cols,.5),df,'normal');B=sample(comp,4000);m=comp[0][0]
  np.savez_compressed(OUT/f'model_{population}_{outcome}.npz',beta=b,covariance=V,columns=cols,posterior_mean=m,posterior_cov=comp[1][0],df=df)
  for name,sub in [('all_complete',z),('circumcised',z.loc[isc])]:
   ww=sub.weight/sub.weight.sum();coverage.append(dict(**meta,subset=name,n=len(sub),weighted_population=sub.weight.sum(),birth_min=sub.birth_early.min(),birth_max=sub.birth_late.max(),foreign_fraction=float(ww@sub.foreign_born),covered_definitely=float(ww@(sub.birth_early.ge(1979)&sub.foreign_born.eq(0))),covered_possibly=float(ww@(sub.birth_late.ge(1979)&sub.foreign_born.eq(0)))))
  for cy,sub in z.groupby('year'):
   Nc=6*sub.loc[sub.circ.eq(1),'weight'].sum();Nf=6*sub.loc[sub.circ.eq(1)&sub.foreign_born.eq(1),'weight'].sum()
   for threshold in [18,15,10]:
    for missing in source_values['assumptions']['setting_multipliers']:
     for history in source_values['assumptions']['historical_multipliers']:
      count=stock(int(cy+1),threshold)*missing*history
      stocks.append(dict(**meta,cycle=int(cy),threshold=threshold,missing_multiplier=missing,historical_multiplier=history,stock=count,circ_population=Nc,fraction=min(1,count/Nc),fraction_foreign_unresolved=min(1,(count+Nf)/Nc)))
  p0raw=np.average(z.loc[~isc,outcome],weights=w[~isc]);p1raw=np.average(z.loc[isc,outcome],weights=w[isc]);raw.append(dict(**meta,pU=p0raw,pC=p1raw,min_fraction=max(0,(p1raw-p0raw)/(1-p0raw))))
  drawp0=[];drawp1=[];drawmin=[];drawmax=[];drawlower=[]
  for start in range(0,len(B),100):
   bb=B[start:start+100];p0=expit(X@bb.T);p1=expit(X@bb.T+bb[:,j]);delta=p1-p0
   drawp0.extend(wc@p0);drawp1.extend(wc@p1);drawmin.extend(wc@np.maximum(delta/(1-p0),-delta/p0));drawmax.extend(np.max(np.maximum(delta/(1-p0),-delta/p0),axis=0));drawlower.extend(wc@(delta/(1-p0)))
  P0=np.array(drawp0);P1=np.array(drawp1);Fmin=np.array(drawmin);Fmax=np.array(drawmax);D=P1-P0
  su=summarize(comp,j);summary=dict(**meta,n=len(z),events=int(z[outcome].sum()),circ_population=w[isc].sum(),adjusted_OR=np.exp(m[j]),OR_low=np.exp(su['log_low']),OR_high=np.exp(su['log_high']),p_positive=su['p_positive'],unregularized_OR=np.exp(b[j]))
  for label,a in [('pU',P0),('pC',P1),('difference',D),('minimum_positive_budget',np.maximum(0,drawlower)),('minimum_any_direction_budget',Fmin)]:summary.update({label+'_'+k:v for k,v in q(a).items()})
  main.append(summary)
  for estimate,bb in [('primary',m),('unregularized',b)]:
   p0=expit(X@bb);p1=expit(X@bb+bb[j]);delta=p1-p0;pU=wc@p0;pC=wc@p1
   fmin=float(wc@(delta/(1-p0))) if bb[j]>0 else float(wc@(-delta/p0))
   for f in fractions:
    # Constant-fraction components, exact model-stratum mixtures; retain invalid patterns.
    pc=p0+delta/f;valid=(pc>=0)&(pc<=1);pcomp=wc@pc
    fixed.append(dict(**meta,estimate=estimate,fraction=f,component_prevalence=pcomp,marginal_OR=(pcomp/(1-pcomp))/(pU/(1-pU)) if 0<pcomp<1 else np.nan,invalid_weight=float(wc@(~valid)),all_strata_feasible=bool(valid.all())))
    # Flexible fraction with a common component odds ratio: exact construction.
    if f>=fmin and f<=1:
     if f==1:logR=bb[j]
     elif bb[j]>0:logR=brentq(lambda lr:float(wc@(delta/(expit(X@bb+lr)-p0)))-f,bb[j]+1e-10,40)
     else:logR=brentq(lambda lr:float(wc@(delta/(expit(X@bb+lr)-p0)))-f,-40,bb[j]-1e-10)
     pa=expit(X@bb+logR);fx=delta/(pa-p0);assert np.max(fx)<=1+1e-7
     np.testing.assert_allclose((1-fx)*p0+fx*pa,p1,atol=1e-10)
     required.append(dict(**meta,estimate=estimate,fraction=f,feasible=True,component_OR=np.exp(logR),component_prevalence=float(wc@(fx*pa)/f),selected_positive_count=float(w[isc].sum()*(wc@(fx*pa))),minimum_fraction=fmin))
    else:required.append(dict(**meta,estimate=estimate,fraction=f,feasible=False,component_OR=np.nan,component_prevalence=np.nan,minimum_fraction=fmin))
   # Complete simplex marginal screen; necessary, not sufficient stratum feasibility.
   fi=np.array([i/100 for i in range(1,101) for a in range(101-i)]);fa=np.array([a/100 for i in range(1,101) for a in range(101-i)]);fk=1-fi-fa
   rows=[]
   for ra in [.5,1,1.5,2,3,5,10,20,np.inf]:
    pa=np.ones_like(p0) if np.isinf(ra) else expit(logit(p0)+np.log(ra))
    for rk in [.5,1,1.5,2,3,5,10,20]:
     pk=expit(logit(p0)+np.log(rk));pi=(pC-fa*(wc@pa)-fk*(wc@pk))/fi;valid=(pi>=0)&(pi<=1)
     rows.append(pd.DataFrame(dict(fI=fi,fA=fa,fK=fk,OR_A=ra,OR_K=rk,pI_marginal=pi,marginal_feasible=valid,infant_marginal_OR=np.where(valid,(pi/(1-pi))/(pU/(1-pU)),np.nan))))
   target=OUT/f'mixed_simplex_{population}_{outcome}_{estimate}.csv.gz'
   pd.concat(rows,ignore_index=True).to_csv(target,index=False)
  for f in fractions:
   pp=P0+D/f;valid=Fmax<=f;probs.append(dict(**meta,fraction=f,p_feasible_all_strata=float(valid.mean()),p_feasible_flexible_fraction=float((Fmin<=f).mean()),p_positive_and_feasible=float(((D>0)&valid).mean()),p_negative_and_feasible=float(((D<0)&valid).mean()),p_infeasible=float((~valid).mean()),p_positive_original=su['p_positive']))
  # Choice-driven subset v uses effective fraction; outputs explicit full grid.
  for f in [.01,.02,.03,.05,.10,.20]:
   for v in [.25,.5,.75,1]:
    probs.append(dict(**meta,fraction=f,choice_fraction=v,effective_fraction=f*v,p_feasible_flexible_fraction=float((Fmin<=f*v).mean()),p_positive_original=su['p_positive']))
  # Frozen-prior/likelihood sensitivities of minimum budget.
  for prior,scale,nuis in [('primary',.5,1),('skeptical',.25,1),('broad',1,1),('nuisance_broad',.5,2)]:
   for lik in ['normal','t']:
    cp=components(b,V,priors(cols,scale,nuis),df,lik);bm=cp[2]@cp[0];pu=expit(X@bm);pc=expit(X@bm+bm[j]);checks.append(dict(**meta,prior=prior,likelihood=lik,p_positive=summarize(cp,j)['p_positive'],minimum_positive_budget=float(wc@np.maximum(0,(pc-pu)/(1-pu)))))
  print(meta,summary,flush=True)
for name,rows in [('headline',main),('coverage',coverage),('count_envelopes',stocks),('raw_check',raw),('required_component',required),('constant_fraction',fixed),('conditional_probabilities',probs),('prior_sensitivity',checks)]:pd.DataFrame(rows).to_csv(OUT/(name+'.csv'),index=False)
(OUT/'mixture_validation.json').write_text(json.dumps({'models':len(main),'draws_per_model':4000,'exact_flexible_mixture_reconstruction':True,'simplex_note':'Marginal necessary feasibility screen only; conditional subset checked separately','external_count_uncertainty':'No confidence bounds claimed; multiplier sensitivity only'},indent=2))
