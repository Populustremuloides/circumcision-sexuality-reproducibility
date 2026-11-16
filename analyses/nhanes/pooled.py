"""Pooled behavior sample, questionnaire-skip audit and fixed sensitivity checks.

Earlier screening negatives are retained as structural zeros in the primary
analysis; exclusions below assess ambiguity without inventing partner histories.
"""
import json
import numpy as np,pandas as pd,pyreadstat
from src.specification import ROOT,ADJUST
from src.survey.design import Survey

def main():
 out=ROOT/'outputs/pooled';out.mkdir(parents=True,exist_ok=True)
 early=pd.read_csv(ROOT/'outputs/replication/harmonized.csv.gz');late=pd.read_csv(ROOT/'data/analysis.csv.gz')
 early['population_weight']=np.where(early.year.le(2001),2*early.WTMEC4YR,early.WTMEC2YR)
 early['weight']=np.where(early.year.le(2001),early.WTMEC4YR*2/9,early.WTMEC2YR/9)
 late['population_weight']=late.weight*6;late['weight']=late.population_weight/9
 d=pd.concat([early,late],ignore_index=True);assert d.SEQN.is_unique
 d['screen_negative']=False;d['screen_negative_ever_married']=False
 audits=[]
 for year,g in d.groupby('year'):
  year=int(year);suffix={1999:'',2001:'_B',2003:'_C',2005:'_D',2007:'_E',2009:'_F',2011:'_G',2013:'_H',2015:'_I'}[year]
  raw=ROOT/('data/replication' if year<2005 else 'data/raw');ext='xpt' if year<2005 else 'XPT'
  sx,_=pyreadstat.read_xport(str(raw/f'SXQ{suffix}.{ext}'));demo,_=pyreadstat.read_xport(str(raw/f'DEMO{suffix}.{ext}'))
  x=g[['SEQN','eligible','msm_ever']].merge(sx,on='SEQN',how='left',validate='one_to_one').merge(demo[['SEQN','DMDMARTL']],on='SEQN',how='left',validate='one_to_one')
  if year<2009:
   screen='SXQ020' if year<2005 else 'SXQ021';count='SXQ200' if year<2005 else 'SXQ410';upper=9999 if year<2005 else 2000
   neg=x[screen].eq(2);positive=x[count].between(1,upper);contrad=neg&positive
   assert not contrad.any()
   ambiguous=neg&x.DMDMARTL.isin([1,2,3,4,6])
   never_ids=x.loc[neg,'SEQN'];amb_ids=x.loc[ambiguous,'SEQN']
   d.loc[d.SEQN.isin(never_ids),'screen_negative']=True;d.loc[d.SEQN.isin(amb_ids),'screen_negative_ever_married']=True
   audits.append(dict(cycle=g.cycle.iloc[0],source=screen+' + '+count,eligible=int(x.eligible.sum()),screen_negative=int((x.eligible&neg).sum()),screen_negative_married_or_former_or_cohabiting=int((x.eligible&ambiguous).sum()),contradictory_positive_count=int((x.eligible&contrad).sum()),unknown_behavior=int((x.eligible&x.msm_ever.isna()).sum())))
  else:
   assert not (x.SXQ809.eq(2)&x.SXQ410.between(1,2000)).any()
   audits.append(dict(cycle=g.cycle.iloc[0],source='SXQ809',eligible=int(x.eligible.sum()),screen_negative=0,screen_negative_married_or_former_or_cohabiting=0,contradictory_positive_count=0,unknown_behavior=int((x.eligible&x.msm_ever.isna()).sum())))
 # Remove raw-only variables from combined output; retain the design population.
 cols=['SEQN','cycle','year','weight','population_weight','stratum','psu','eligible','RIAGENDR','RIDAGEYR','circ','msm_ever','age10','race','education','foreign_born','screen_negative','screen_negative_ever_married']
 d[cols].to_csv(ROOT/'data/pooled.csv.gz',index=False);pd.DataFrame(audits).to_csv(out/'skip_audit.csv',index=False)
 results=[]
 specifications=[('full',1999,None),('exclude_1999_2000',2001,None),('original_2005_2016',2005,None),('direct_2009_2016',2009,None),('exclude_ambiguous_screen_zeros',1999,'screen_negative_ever_married'),('exclude_all_earlier_screen_zeros',1999,'screen_negative')]
 for name,start,exclude in specifications:
  z=d[d.year.ge(start)].copy().reset_index(drop=True)
  if start>1999:
   z['weight']=z.population_weight/z.cycle.nunique()
   if start==2001:
    z.loc[z.year.eq(2001),'weight']=early.set_index('SEQN').loc[z.loc[z.year.eq(2001),'SEQN'],'WTMEC2YR'].to_numpy()/z.cycle.nunique()
  mask=z.eligible & (~z[exclude] if exclude else True)
  row,_=Survey(z).model('msm_ever',ADJUST['full'],mask,name);results.append(row)
  z['complete']=mask&z[['circ','msm_ever','age10','race','education','foreign_born']].notna().all(axis=1)
  z.to_csv(out/f'{name}_validation.csv.gz',index=False)
 pd.DataFrame(results).to_csv(out/'models.csv',index=False)
 sequence=[]
 complete=d.eligible & d[['circ','msm_ever','age10','race','education','foreign_born']].notna().all(axis=1)
 for name,rhs in ADJUST.items():
  for sample,mask in [('available',d.eligible),('common_complete',complete)]:
   row,_=Survey(d).model('msm_ever',rhs,mask,name);row['sample']=sample;sequence.append(row)
 pd.DataFrame(sequence).to_csv(out/'adjustment_sequence.csv',index=False)
 prev,diff=Survey(d).prevalence('msm_ever',d.eligible)
 pd.DataFrame(prev).to_csv(out/'prevalence.csv',index=False);pd.DataFrame([diff]).to_csv(out/'prevalence_difference.csv',index=False)
 assert results[0]['n']==12973 and results[0]['events']==662
 print(pd.DataFrame(results)[['model','n','events','odds_ratio','ci_low','ci_high','p_value']].to_string(index=False))
 print(pd.DataFrame(audits).to_string(index=False))
if __name__=='__main__':main()
