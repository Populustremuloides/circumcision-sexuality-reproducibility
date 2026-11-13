import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import sys,json
import numpy as np,pandas as pd,patsy
from scipy.special import expit
from scipy.stats import t
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/timing';REPO=ROOT;OUT.mkdir(parents=True,exist_ok=True)
from src.frequentist.nhanes import ADJUST
D=pd.read_csv(REPO/'data/analysis.csv.gz');units=D[['stratum','psu']].drop_duplicates(); strata=[g.psu.tolist() for _,g in units.groupby('stratum')]
rows=[];fail=[];validation=[]
def calibrate(w,y,c,g,f,R):
 den=np.bincount(g,weights=w*c);num=np.bincount(g,weights=w*c*y);p=np.divide(num,den,out=np.zeros_like(num),where=den>0)
 if np.isinf(R):
  q1=np.minimum(1,np.divide(f,p,out=np.ones_like(p),where=p>0));q0=np.maximum(0,np.divide(f-p,1-p,out=np.zeros_like(p),where=p<1))
 else:
  a=(1-p)*(R-1);b=1+(p-f)*(R-1);q0=2*f/(b+np.sqrt(b*b+4*a*f));q1=R*q0/(1+(R-1)*q0)
 q=np.where(y==1,q1[g],q0[g])*c
 assert np.allclose(np.bincount(g,weights=w*q),f*den,atol=1e-7)
 return q

def solve(E,L,y,w,q,start):
 b=start.copy();we=w*(1-q);wl=w*q
 def ll(beta):
  ze=E@beta;zl=L@beta;return np.sum(we*(y*ze-np.logaddexp(0,ze))+wl*(y*zl-np.logaddexp(0,zl)))
 for _ in range(60):
  pe=expit(E@b);pl=expit(L@b);sc=E.T@(we*(y-pe))+L.T@(wl*(y-pl));H=E.T@((we*pe*(1-pe))[:,None]*E)+L.T@((wl*pl*(1-pl))[:,None]*L)
  step=np.linalg.solve(H,sc);old=ll(b);scale=1
  while scale>1e-6 and ll(b+scale*step)<old-1e-8:scale/=2
  b+=scale*step
  if np.max(np.abs(sc))<1e-7:return b
 raise ValueError('Newton nonconvergence')
for pop in ['all','us_born']:
 for outcome in ['msm_ever','identity_gb','identity_gay','identity_bi']:
  if not (OUT/f'model_{pop}_{outcome}.npz').exists():
   print('UNAVAILABLE MODEL',pop,outcome,flush=True);continue
  mask=D.eligible & (True if pop=='all' else D.foreign_born.eq(0));formula=outcome+' ~ '+ADJUST['full'];formula=formula.replace(' + foreign_born','') if pop=='us_born' else formula
  yy,xx=patsy.dmatrices(formula,D.loc[mask],return_type='dataframe');z=D.loc[xx.index];X=xx.to_numpy();y=yy.iloc[:,0].to_numpy();w=z.weight.to_numpy();w/=w.mean();c=z.circ.to_numpy();j=list(xx.columns).index('circ');cache=np.load(OUT/f'model_{pop}_{outcome}.npz');orig=cache['beta'];E=np.c_[X,np.zeros(len(X))];L=E.copy();L[:,j]=0;L[:,-1]=c
  g=pd.factorize(z.cycle+'_'+((z.year-z.RIDAGEYR)//10).astype(str)+'_'+z.foreign_born.astype(str))[0]
  start=np.r_[orig,orig[j]]
  # With R1 and common timing budget within each group, recombined fit must be identical.
  qb=calibrate(w,y,c,g,.1,1);base=solve(E,L,y,w,qb,start);np.testing.assert_allclose(base[j],orig[j],atol=1e-7);np.testing.assert_allclose(base[-1],orig[j],atol=1e-7)
  validation.append(dict(population=pop,outcome=outcome,recombined_original=True))
  for f in [.01,.02,.03,.05,.10,.20]:
   for R in [.5,1,2,5,10,20,50,np.inf]:
    meta=dict(population=pop,outcome=outcome,fraction=f,allocation_OR=R)
    try:
     q=calibrate(w,y,c,g,f,R);b=solve(E,L,y,w,q,start);rec=dict(**meta,early_OR=np.exp(b[j]),late_OR=np.exp(b[-1]),n=len(y),variance='point_only')
     if outcome=='msm_ever' and f in [.02,.05,.10] and R in [1,10,50,np.inf]:
      cov=np.zeros((len(b),len(b)));nr=0
      for psus in strata:
       reps=[]
       for psu in psus:
        wr=w.copy();in_s=z.psu.isin(psus).to_numpy();wr[in_s]*=len(psus)/(len(psus)-1);wr[z.psu.eq(psu).to_numpy()]=0
        qr=calibrate(wr,y,c,g,f,R);reps.append(solve(E,L,y,wr,qr,b));nr+=1
       r=np.array(reps);rr=r-r.mean(0);cov+=(len(psus)-1)/len(psus)*(rr.T@rr)
      se=np.sqrt(cov[j,j]);df=len(units)-len(strata)-(len(b)-1);rec.update(variance='stratified_delete_PSU_jackknife_recalibrated',early_se=se,early_low=np.exp(b[j]-t.ppf(.975,df)*se),early_high=np.exp(b[j]+t.ppf(.975,df)*se),replicates=nr,df=df)
     rows.append(rec)
    except Exception as ex:fail.append(dict(**meta,error=str(ex)))
   pd.DataFrame(rows).to_csv(OUT/'allocation_results.csv',index=False);pd.DataFrame(fail).to_csv(OUT/'allocation_failures.csv',index=False)
   print(pop,outcome,f,'completed',len(fail),'failures',flush=True)
(OUT/'allocation_validation.json').write_text(json.dumps(dict(checks=validation,failures=fail),indent=2))
