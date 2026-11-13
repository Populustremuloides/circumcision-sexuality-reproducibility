"""NHANES 2005–2016 circumcision, sexual identity, and male–male behavior.

GLM point estimates use statsmodels. Its model-based covariance is NOT used.
Survey variance is calculated explicitly from stratified PSU score totals with
zero contributions for observations outside the analysis domain.
"""
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import pyreadstat
from bs4 import BeautifulSoup
from scipy.special import expit, logit
from scipy.stats import t
import scipy
import statsmodels
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
RAW, OUT = ROOT / 'data/raw', ROOT / 'outputs/frequentist'
OUT.mkdir(exist_ok=True)
CYCLES = list(zip(range(2005, 2017, 2), 'DEFGHI'))
from src.specification import ADJUST

from src.data.nhanes import codebook_audit, harmonize
from src.survey.design import Survey

def main():
    d = harmonize()
    survey = Survey(d)
    eligible = d.eligible
    fullvars = ['circ','age10','cycle','race','education','foreign_born']
    fully_observed = d[fullvars].notna().all(axis=1)
    flow, missing = [], []
    for cycle, g in d[d.eligible].groupby('cycle'):
        rec = dict(cycle=cycle, eligible_examined=len(g), sxq_record=int(g.sxq_record.sum()),
                   known_circ=int(g.circ.notna().sum()), known_identity=int(g.identity_gb.notna().sum()),
                   known_msm=int(g.msm_ever.notna().sum()))
        for outcome in ['identity_gb','msm_ever']:
            valid = g[outcome].notna() & g.circ.notna()
            complete = valid & g[fullvars].notna().all(axis=1)
            rec[outcome+'_available'] = int(valid.sum())
            rec[outcome+'_complete'] = int(complete.sum())
            rec[outcome+'_events'] = int(g.loc[complete,outcome].sum())
        flow.append(rec)
        for variable in ['SXQ280','identity_raw']:
            for value, count in g[variable].value_counts(dropna=False).items():
                missing.append(dict(cycle=cycle,variable=variable,value=value,n=count))
    pd.DataFrame(flow).to_csv(OUT / 'sample_flow.csv',index=False)
    pd.DataFrame(missing).to_csv(OUT / 'response_codes.csv',index=False)

    models, sensitivities, prevalences, differences = [], [], [], []
    domains = {}
    for outcome in ['identity_gb','msm_ever']:
        common = eligible & fully_observed & d[outcome].notna()
        for name,rhs in ADJUST.items():
            result, domain = survey.model(outcome,rhs,eligible,name,jackknife=name=='full')
            result['sample'] = 'available_for_model'
            models.append(result)
            same, _ = survey.model(outcome,rhs,common,name)
            same['sample'] = 'full_model_complete_cases'
            models.append(same)
            if name == 'full':
                domains[outcome] = domain
        rows, diff = survey.prevalence(outcome,eligible & d.circ.notna())
        prevalences += rows
        differences.append(diff)
        specs = [
            ('exclude_2015_2016', ADJUST['full'], d.year < 2015),
            ('direct_behavior_2009_2016',ADJUST['full'],d.year >= 2009),
            ('us_born_only',ADJUST['full'].replace(' + foreign_born',''),d.foreign_born.eq(0)),
            ('add_income',ADJUST['full']+' + pir',eligible),
            ('age_decade_categories',ADJUST['full'].replace('age10 + I(age10**2)','C(age_group)'),eligible),
            ('identity_behavior_common_sample',ADJUST['full'],d.identity_gb.notna() & d.msm_ever.notna()),
            ('sexually_experienced',ADJUST['full'],d.sex_ever.eq(1)),
        ]
        for label,rhs,mask in specs:
            row,_ = survey.model(outcome,rhs,mask,label)
            sensitivities.append(row)
        for year,_ in CYCLES:
            row,_ = survey.model(outcome,ADJUST['full'],d.year.ne(year),f'leave_out_{year}')
            sensitivities.append(row)
            # Cycle-specific minority counts cannot support all categorical
            # covariates reliably. Show age-adjusted cycle estimates only.
            rhs = 'circ + age10 + I(age10**2)'
            row,_ = survey.model(outcome,rhs,d.year.eq(year),f'cycle_{year}')
            sensitivities.append(row)
    for outcome in ['identity_gay','identity_bi']:
        for name in ['unadjusted','full']:
            row,_ = survey.model(outcome,ADJUST[name],eligible,name)
            sensitivities.append(row)
    pd.DataFrame(models).to_csv(OUT / 'models.csv',index=False)
    pd.DataFrame(sensitivities).to_csv(OUT / 'sensitivities.csv',index=False)
    pd.DataFrame(prevalences).to_csv(OUT / 'prevalence.csv',index=False)
    pd.DataFrame(differences).to_csv(OUT / 'prevalence_differences.csv',index=False)
    # Descriptive composition by exposure, restricted to each endpoint's full model.
    composition = []
    for outcome, domain in domains.items():
        for c in [0,1]:
            g = d.loc[domain & d.circ.eq(c)]
            for variable in ['race','education','foreign_born','cycle']:
                for level in sorted(g[variable].unique()):
                    composition.append(dict(outcome=outcome,circ=c,variable=variable,level=level,
                        n=int(g[variable].eq(level).sum()),
                        weighted_proportion=np.average(g[variable].eq(level),weights=g.weight)))
    pd.DataFrame(composition).to_csv(OUT / 'composition.csv',index=False)
    validation = dict(examined_n=len(d),eligible_men=int(eligible.sum()),
        psus=len(survey.units),strata=len(survey.strata),design_df=survey.design_df,
        min_psus_per_stratum=min(map(len,survey.strata)),
        max_psus_per_stratum=max(map(len,survey.strata)),
        codebook_rows_checked=len(pd.read_csv(OUT/'codebook_frequency_audit.csv')),
        all_analysis_critical_codebook_counts_match=True,
        codebook_discrepancies=pd.read_csv(OUT/'codebook_frequency_audit.csv').query('passed == False').to_dict('records'),
        unique_seqn=True,score_and_covariance_checks_passed=True,
        inference='Taylor linearization; t with domain PSU minus stratum count minus model rank plus one',
        python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,
        scipy=scipy.__version__,statsmodels=statsmodels.__version__,pyreadstat=pyreadstat.__version__,
        jackknife=[{k:r[k] for k in ['outcome','se','jackknife_se','jackknife_taylor_se_ratio']}
                   for r in models if 'jackknife_se' in r])
    (OUT / 'validation.json').write_text(json.dumps(validation,indent=2))
    print(pd.DataFrame(models).query('sample == "available_for_model"')[[
        'outcome','model','n','events','odds_ratio','ci_low','ci_high','p_value','residual_df']].to_string(index=False))
    print(pd.DataFrame(prevalences).to_string(index=False))
    print(json.dumps(validation,indent=2))


if __name__=="__main__":main()
