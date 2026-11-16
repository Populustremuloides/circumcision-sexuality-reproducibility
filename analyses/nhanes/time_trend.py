from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd
from scipy.stats import t,f
REPO=Path(__file__).resolve().parents[2]
HERE=REPO/'outputs/time_trend'
HERE.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(REPO))
from src.survey.design import Survey
from src.specification import ADJUST
inputs=[REPO/'data/analysis.csv.gz',REPO/'outputs/replication/harmonized.csv.gz']
late=pd.read_csv(inputs[0]);early=pd.read_csv(inputs[1])
# Recover the original two-year weights for analyses excluding 1999.
late['w2']=late.weight*6;early['w2']=early.WTMEC2YR
all_data=pd.concat([early,late],ignore_index=True)
assert all_data.SEQN.is_unique
all_data['trend10']=(all_data.year-2009)/10
all_data['eligible']=all_data.eligible.astype(bool)
periods=[('direct_2009_2016',2009,2015),('harmonized_2001_2016',2001,2015),('harmonized_1999_2016',1999,2015),('partner_history_2001_2008',2001,2007)]
rows=[];cycles=[];coefficients=[];flows=[];exports=[]
for label,start,end in periods:
 d=all_data[all_data.year.between(start,end)].copy().reset_index(drop=True)
 k=d.cycle.nunique()
 if start==1999:d['weight']=np.where(d.year.le(2001),d.WTMEC4YR*2/k,d.w2/k)
 else:d['weight']=d.w2/k
 assert d.weight.gt(0).all() and d.weight.notna().all()
 survey=Survey(d)
 base=ADJUST['full']
 row,domain,fit=survey.model('msm_ever',base+' + circ:trend10',d.eligible,label,return_fit=True)
 j=fit['columns'].index('circ:trend10');b=fit['coefficients'][j];se=np.sqrt(fit['covariance'][j,j]);df=row['residual_df'];crit=t.ppf(.975,df)
 rows.append(dict(period=label,test='linear_trend',n=row['n'],events=row['events'],beta=b,se=se,ratio_OR_per_decade=np.exp(b),low=np.exp(b-crit*se),high=np.exp(b+crit*se),statistic=b/se,df1=1,df2=df,p=2*t.sf(abs(b/se),df)))
 for term,bb,ss in zip(fit['columns'],fit['coefficients'],np.sqrt(np.diag(fit['covariance']))):coefficients.append(dict(period=label,model='linear',term=term,beta=bb,se=ss))
 r2,domain2,fit2=survey.model('msm_ever',base+' + circ:C(cycle)',d.eligible,label+'_categorical',return_fit=True)
 assert np.array_equal(domain,domain2)
 ids=[i for i,n in enumerate(fit2['columns']) if n.startswith('circ:C(cycle)')]
 B=fit2['coefficients'][ids];V=fit2['covariance'][np.ix_(ids,ids)];q=len(ids);stat=float(B@np.linalg.solve(V,B)/q)
 rows.append(dict(period=label,test='categorical_heterogeneity',n=r2['n'],events=r2['events'],statistic=stat,df1=q,df2=r2['residual_df'],p=f.sf(stat,q,r2['residual_df'])))
 for term,bb,ss in zip(fit2['columns'],fit2['coefficients'],np.sqrt(np.diag(fit2['covariance']))):coefficients.append(dict(period=label,model='categorical',term=term,beta=bb,se=ss))
 for cycle in sorted(d.cycle.unique()):
  a=np.zeros(len(fit2['columns']));a[fit2['columns'].index('circ')]=1
  name=f'circ:C(cycle)[T.{cycle}]'
  if name in fit2['columns']:a[fit2['columns'].index(name)]=1
  b=float(a@fit2['coefficients']);se=float(np.sqrt(a@fit2['covariance']@a));crit=t.ppf(.975,r2['residual_df']);cc=d[domain & d.cycle.eq(cycle)]
  cycles.append(dict(period=label,cycle=cycle,n=len(cc),events=int(cc.msm_ever.sum()),OR=np.exp(b),low=np.exp(b-crit*se),high=np.exp(b+crit*se)))
  flows.append(dict(period=label,cycle=cycle,eligible=int((d.eligible&d.cycle.eq(cycle)).sum()),complete=len(cc),events=int(cc.msm_ever.sum())))
 d['complete']=domain
 cols=['SEQN','cycle','year','weight','stratum','psu','eligible','complete','circ','msm_ever','age10','race','education','foreign_born','trend10']
 d[cols].to_csv(HERE/f'{label}_validation.csv.gz',index=False)
pd.DataFrame(rows).to_csv(HERE/'tests.csv',index=False)
pd.DataFrame(cycles).to_csv(HERE/'cycle_estimates.csv',index=False)
pd.DataFrame(coefficients).to_csv(HERE/'coefficients.csv',index=False)
pd.DataFrame(flows).to_csv(HERE/'sample_flow.csv',index=False)
(HERE/'provenance.json').write_text(json.dumps({'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs+[Path(__file__),REPO/'analyses/nhanes/time_trend_plan.md',REPO/'src/survey/design.py']},'repository_commit':'8ff1d6e01727de5bd743ea7cf0386755979f6430'},indent=2))
print(pd.DataFrame(rows).to_string(index=False))
print(pd.DataFrame(cycles).query("period=='direct_2009_2016'").to_string(index=False))
