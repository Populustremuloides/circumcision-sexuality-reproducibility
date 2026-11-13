"""Separate male–male anal and performing-oral behavior, 2009–2016."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pyreadstat
from statsmodels.stats.multitest import multipletests
from src.frequentist.nhanes import ROOT, Survey, ADJUST, codebook_audit

OUT=ROOT/'outputs/frequentist/behavior_extension'
OUT.mkdir(exist_ok=True)
d=pd.read_csv(ROOT/'data/analysis.csv.gz')
d=d[d.year.ge(2009)].reset_index(drop=True)
d['weight']*=6/4
parts=[]; audit=[]; extracts=[]
variables=['SXQ809','SXQ836','SXQ841','SXQ853','SXQ627']
for suffix in 'FGHI':
    raw,_=pyreadstat.read_xport(str(ROOT/f'data/raw/SXQ_{suffix}.XPT'))
    rows,txt=codebook_audit(raw,f'SXQ_{suffix}',variables)
    audit+=rows; extracts+=txt
    parts.append(raw[['SEQN']+variables])
raw=pd.concat(parts,ignore_index=True)
assert raw.SEQN.is_unique
d=d.merge(raw,on='SEQN',how='left',validate='one_to_one')
assert all(x['passed'] for x in audit)
pd.DataFrame(audit).to_csv(OUT/'codebook_audit.csv',index=False)
(OUT/'codebook_extracts.txt').write_text('\n\n'.join(extracts))
yes=d.SXQ809.eq(1); no=d.SXQ809.eq(2)
# No unexplained recoding of arbitrary missing screening responses.
for out,var in [('anal_lifetime','SXQ836'),('anal_year','SXQ841'),('oral_year','SXQ627')]:
    x=d[var].where(d[var].between(0,2000))
    assert x.dropna().eq(x.dropna().round()).all()
    d[out]=(x>=1).astype(float).where(x.notna() & yes)
d['oral_lifetime']=d.SXQ853.map({1:1.,2:0.}).where(yes)
for out in ['anal_lifetime','oral_lifetime','anal_year','oral_year']:
    d.loc[no,out]=0.
for lt,yr in [('anal_lifetime','anal_year'),('oral_lifetime','oral_year')]:
    conflict=d.eligible & d[lt].eq(0) & d[yr].eq(1)
    assert not conflict.any(), (lt,'contradictory positive past-year response')
    d.loc[d[lt].eq(0),yr]=0.
    assert not d.loc[d.SXQ809.isin([7,9]) | d.SXQ809.isna(),lt].notna().any()
# Verify screening negatives do not have contrary direct responses among men.
assert not (d.eligible & no & (d.SXQ836.between(1,2000)|d.SXQ853.eq(1))).any()
d.to_csv(ROOT/'data/behavior_extension.csv.gz',index=False)
survey=Survey(d)
models=[]; prev=[]; diffs=[]; flows=[]; cells=[]
fullvars=['circ','age10','cycle','race','education','foreign_born']
for population,mask in [('all_men',d.eligible),('lifetime_msm',d.eligible & yes)]:
    for outcome in ['anal_lifetime','oral_lifetime','anal_year','oral_year']:
        complete=mask & d[fullvars+[outcome]].notna().all(axis=1)
        family='primary_lifetime' if outcome.endswith('lifetime') else 'secondary_past_year'
        for sample,m in [('available_for_model',mask),('full_model_complete_cases',complete)]:
            for name,rhs in ADJUST.items():
                try:
                    row,domain=survey.model(outcome,rhs,m,name, jackknife=(name=='full' and sample=='available_for_model' and family=='primary_lifetime'))
                    row['status']='estimated'
                except (AssertionError,np.linalg.LinAlgError) as e:
                    row=dict(outcome=outcome,model=name,status='not_estimable',error=str(e))
                row.update(population=population,family=family,sample=sample)
                models.append(row)
        records,difference=survey.prevalence(outcome,mask & d.circ.notna())
        for row in records:
            row.update(population=population); prev.append(row)
        difference['population']=population; diffs.append(difference)
        for cycle,g in d[mask].groupby('cycle'):
            avail=g.circ.notna() & g[outcome].notna()
            cc=g[fullvars+[outcome]].notna().all(axis=1)
            flows.append(dict(population=population,outcome=outcome,cycle=cycle,
                domain_n=len(g),known_circ=int(g.circ.notna().sum()),available_n=int(avail.sum()),
                complete_n=int(cc.sum()),events=int(g.loc[cc,outcome].sum())))
        for c in [0,1]:
            for y in [0,1]:
                cells.append(dict(population=population,outcome=outcome,circ=c,event=y,
                    n=int((complete & d.circ.eq(c) & d[outcome].eq(y)).sum())))
models=pd.DataFrame(models)
main=models[models.model.eq('full') & models['sample'].eq('available_for_model')].copy()
assert len(main)==8
# Retain failed tests in family size by assigning p=1 for correction only.
for family in main.family.unique():
    ix=main.family.eq(family)
    main.loc[ix,'p_holm_family']=multipletests(main.loc[ix,'p_value'].fillna(1),method='holm')[1]
main['p_holm_all_eight']=multipletests(main.p_value.fillna(1),method='holm')[1]
for frame,name in [(models,'models'),(main,'main_results'),(pd.DataFrame(prev),'prevalence'),
                   (pd.DataFrame(diffs),'prevalence_differences'),(pd.DataFrame(flows),'sample_flow'),(pd.DataFrame(cells),'cells')]:
    frame.to_csv(OUT/f'{name}.csv',index=False)
# All four full primary fits must be recorded, including any instability.
checks=dict(cycles='2009–2016',examined_n=len(d),eligible_men=int(d.eligible.sum()),
    psus=len(survey.units),strata=len(survey.strata),design_df=survey.design_df,
    audited_frequency_rows=len(audit),all_frequency_rows_match=True,
    no_screening_or_lifetime_past_year_contradictions=True,
    unadjusted_weighted_table_and_dual_covariance_checks=True,
    failed_models=models[models.status.ne('estimated')].fillna('').to_dict('records'))
# Independent weight-scale check of each estimable full model.
scaled=d.copy(); scaled.weight*=4
for row in main.itertuples():
    if row.status!='estimated': continue
    mask=scaled.eligible if row.population=='all_men' else scaled.eligible & scaled.SXQ809.eq(1)
    fit,_=Survey(scaled).model(row.outcome,ADJUST['full'],mask,'full')
    np.testing.assert_allclose([fit['beta'],fit['se']],[row.beta,row.se],rtol=1e-8)
checks['weight_scale_invariance']=True
(OUT/'validation.json').write_text(json.dumps(checks,indent=2))
print(main[['population','outcome','status','n','events','odds_ratio','ci_low','ci_high','p_value','p_holm_family','p_holm_all_eight']].to_string(index=False))
print(pd.DataFrame(prev)[['population','outcome','circ','n','events','prevalence']].to_string(index=False))
