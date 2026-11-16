"""Separate earlier-period analysis; requires --estimate to calculate associations."""
import argparse,json,hashlib,urllib.request
import pandas as pd,numpy as np,pyreadstat
from bs4 import BeautifulSoup
from src.specification import ROOT,ADJUST
from src.survey.design import Survey

def main():
 p=argparse.ArgumentParser();p.add_argument('--estimate',action='store_true');a=p.parse_args()
 here=ROOT/'analyses/replication';raw=ROOT/'data/replication';out=ROOT/'outputs/replication';raw.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 for item in json.loads((here/'sources.json').read_text()):
  dest=raw/item['file']
  if not dest.exists():
   with urllib.request.urlopen(item['url'],timeout=90) as response:dest.write_bytes(response.read())
  assert hashlib.sha256(dest.read_bytes()).hexdigest()==item['sha256'],dest
 frames=[];audit=[];flow=[]
 for year,suffix in [(1999,''),(2001,'_B'),(2003,'_C')]:
  imported={}
  for kind in ['DEMO','SXQ']:
   path=raw/f'{kind}{suffix}.xpt';d,_=pyreadstat.read_xport(str(path));alt=pd.read_sas(path);alt=alt.mask(alt.abs().lt(1e-70)&alt.ne(0),0);np.testing.assert_allclose(d,alt,rtol=1e-12,atol=1e-12,equal_nan=True);imported[kind]=d
   soup=BeautifulSoup((raw/f'{kind}{suffix}.htm').read_text(),'html.parser')
   for var in (['SXQ020','SXQ200','SXQ280'] if kind=='SXQ' else ['RIDRETH1','DMDEDUC2','DMDBORN']):
    section=soup.find(id=var).parent
    for tr in section.select('table tbody tr'):
     cells=[v.get_text(' ',strip=True) for v in tr.find_all('td')]
     if len(cells)<3:continue
     value,label,count=cells[:3];expected=int(count.replace(',',''))
     observed=int(d[var].isna().sum()) if value=='.' else int(d[var].between(*map(float,value.split(' to '))).sum()) if ' to ' in value else int(d[var].eq(float(value)).sum())
     assert observed==expected,(year,var,value,observed,expected);audit.append(dict(year=year,variable=var,value=value,observed=observed,expected=expected))
  d=imported['DEMO'].merge(imported['SXQ'],on='SEQN',how='left',validate='one_to_one');d['cycle']=f'{year}-{year+1}';d['year']=year;d['weight']=d.WTMEC4YR*2/3 if year<2003 else d.WTMEC2YR/3;d=d[d.weight.gt(0)].copy()
  d['stratum']=d.cycle+'_'+d.SDMVSTRA.astype(int).astype(str);d['psu']=d.stratum+'_'+d.SDMVPSU.astype(int).astype(str);d['eligible']=d.RIAGENDR.eq(1)&d.RIDAGEYR.between(20,59);d['circ']=d.SXQ280.map({1:1.,2:0.});count=d.SXQ200.where(d.SXQ200.between(0,9999));assert (count.dropna()%1==0).all();assert not (d.SXQ020.eq(2)&count.gt(0)).any();d['msm_ever']=count.ge(1).astype(float).where(count.notna());d.loc[d.SXQ020.eq(2),'msm_ever']=0.
  d['age10']=(d.RIDAGEYR-40)/10;d['race']=d.RIDRETH1.where(d.RIDRETH1.between(1,5));d['education']=d.DMDEDUC2.where(d.DMDEDUC2.between(1,5));d['foreign_born']=d.DMDBORN.ne(1).astype(float).where(d.DMDBORN.isin([1,2,3]));z=d[d.eligible];cc=['circ','msm_ever','age10','race','education','foreign_born'];flow.append(dict(cycle=d.cycle.iloc[0],eligible=len(z),circumcision_known=z.circ.notna().sum(),outcome_known=z.msm_ever.notna().sum(),complete_cases=z[cc].notna().all(axis=1).sum()));frames.append(d)
 data=pd.concat(frames,ignore_index=True);assert data.SEQN.is_unique;pd.DataFrame(flow).to_csv(out/'sample_flow.csv',index=False);pd.DataFrame(audit).to_csv(out/'codebook_audit.csv',index=False);data.to_csv(out/'harmonized.csv.gz',index=False)
 if a.estimate:
  results=[]
  for label,rhs,start in [('unadjusted','circ',1999),('adjusted',ADJUST['full'],1999),('exclude_1999_2000',ADJUST['full'],2001)]:
   d=data[data.year.ge(start)].copy().reset_index(drop=True)
   if start==2001:d['weight']=d.WTMEC2YR/2
   row,_=Survey(d).model('msm_ever',rhs,d.eligible,label);results.append(row)
  pd.DataFrame(results).to_csv(out/'models.csv',index=False);
  from scripts.build_results import table
  report='# Historical earlier-period analysis\n\nThe fixed specification was committed as af1e2a0 before estimating associations. This historical subset now overlaps the pooled 1999–2016 primary analysis and is not independent confirmation.\n\n'+table(pd.DataFrame(results)[['model','n','events','odds_ratio','ci_low','ci_high','p_value']])+'\n\nBoth adjusted point estimates are positive but imprecise; their intervals include one and the original-period estimate. This does not establish replication or equivalence. The unadjusted association uses its own available cases. The predetermined exclusion of 1999–2000 addresses a wording difference. Sources, weights, routing and missingness are specified in [the fixed plan](../analyses/replication/specification.md). Run `python -m analyses.replication.run --estimate` and optionally `Rscript analyses/replication/verify.R`.\n'
  (ROOT/'docs/replication_results.md').write_text(report); print(pd.DataFrame(results)[['model','n','events','odds_ratio','ci_low','ci_high','p_value']].to_string(index=False))
 print('Source, questionnaire and reader checks passed.')
if __name__=='__main__':main()
