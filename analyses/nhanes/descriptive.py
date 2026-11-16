"""Generate Table 1 from the exact exported primary complete-case sample."""
import json,hashlib
import numpy as np,pandas as pd
from src.specification import ROOT
from src.frequentist.export import load_primary

def main():
 cache,meta=load_primary();d=pd.read_csv(ROOT/meta['input_file']);z=d.set_index('SEQN').loc[cache['analytic_seqn']];out=ROOT/'outputs/descriptive';out.mkdir(parents=True,exist_ok=True);rows=[]
 categories={'race':{1:'Mexican American',2:'Other Hispanic',3:'Non-Hispanic White',4:'Non-Hispanic Black',5:'Other race, including multiracial'},'education':{1:'Less than ninth grade',2:'Ninth–eleventh grade, no diploma',3:'High school graduate or GED',4:'Some college or associate degree',5:'College graduate or above'},'foreign_born':{0:'Born in 50 U.S. states or DC',1:'Born outside 50 U.S. states/DC'},'cycle':{x:x for x in sorted(z.cycle.unique())}}
 for group,g in [('Total',z),('Intact',z[z.circ.eq(0)]),('Circumcised',z[z.circ.eq(1)])]:
  w=g.weight/g.weight.sum();mean=float(w@g.RIDAGEYR);sd=float(np.sqrt(w@((g.RIDAGEYR-mean)**2)));rows.extend([dict(group=group,variable='N',category='Unweighted sample size',n=len(g),value=len(g),statistic='count'),dict(group=group,variable='age',category='Age, years (mean, SD)',n=len(g),value=mean,sd=sd,statistic='weighted_mean_sd')])
  for variable,levels in categories.items():
   assert g[variable].notna().all();total=0
   for code,label in levels.items():
    mask=g[variable].eq(code);value=float(100*(w@mask));total+=value;rows.append(dict(group=group,variable=variable,category=label,n=int(mask.sum()),value=value,statistic='weighted_percent'))
   np.testing.assert_allclose(total,100,atol=1e-10)
 table=pd.DataFrame(rows);table.to_csv(out/'table1.csv',index=False)
 lines=[r'\begin{table}[htbp]',r'\centering\small',r'\caption{Characteristics of the primary NHANES 1999--2016 analytic sample by circumcision status.}',r'\label{tab:demographics}',r'\begin{tabular}{lrrr}\toprule',r'Characteristic & Total & Intact & Circumcised \\\midrule']
 for variable in ['N','age','race','education','foreign_born','cycle']:
  if variable not in ['N','age']:lines.append(r'\multicolumn{4}{l}{\textit{'+{'race':'Race/ethnicity','education':'Educational attainment','foreign_born':'Nativity','cycle':'Survey cycle'}[variable]+r'}}\\')
  for label in table.loc[table.variable.eq(variable),'category'].drop_duplicates():
   vals=[]
   for group in ['Total','Intact','Circumcised']:
    r=table[(table.group==group)&(table.variable==variable)&(table.category==label)].iloc[0]
    vals.append(f'{int(r.n):,}' if variable=='N' else f'{r.value:.1f} ({r.sd:.1f})' if variable=='age' else f'{int(r.n):,} ({r.value:.1f})')
   lines.append(label.replace('–','--')+' & '+' & '.join(vals)+r' \\')
 lines += [r'\bottomrule\end{tabular}',r'\par\smallskip\begin{minipage}{\linewidth}\footnotesize Entries are unweighted counts (survey-weighted percentages), except sample sizes and age. Age is the survey-weighted mean (population standard deviation, not standard error). Percentages use examination weights within each column. The sample comprises complete cases for the fully adjusted lifetime male--male behavior model; all displayed covariates are complete. Supplementary sample flow documents exclusions.\end{minipage}',r'\end{table}']
 (out/'table1.tex').write_text('\n'.join(lines)+'\n');eligible=d[d.eligible];required=['circ','msm_ever','age10','cycle','race','education','foreign_born'];remaining=eligible.copy();flow=[]
 for label,cols in [('Eligible examined men',[]),('Known circumcision',['circ']),('Known behavioral outcome',['msm_ever']),('Complete adjustment covariates',required)]:
  before=len(remaining);remaining=remaining.dropna(subset=cols);flow.append(dict(stage=label,n=len(remaining),excluded_from_previous=before-len(remaining)))
 assert set(remaining.SEQN)==set(cache['analytic_seqn']);pd.DataFrame(flow).to_csv(out/'sample_flow_sequential.csv',index=False)
 missing=eligible[required].isna().sum().rename('missing_n');missing.to_csv(out/'missingness.csv');(out/'metadata.json').write_text(json.dumps(dict(n=len(z),target='primary outcome-specific complete cases',artifact_sha256=meta['artifact_sha256'],input_sha256=meta['input_sha256'],code_sha256=hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest(),age_sd='weighted population SD; not SE',missingness_counts='overlapping before sequential exclusions'),indent=2)+'\n');print(pd.DataFrame(flow).to_string(index=False))
if __name__=='__main__':main()
