"""Separate circumcised-only analysis of regret and reported experiences.

Primary sample uses only variables needed for the analysis. The sensitivity
sample adds partner-visibility completeness to reproduce the previous manuscript
sample. The corrected manuscript reports the 326-person primary analysis.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact
from scipy.stats.contingency import odds_ratio
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/frequentist/maloney'
QUESTIONS = {
    'status': 'Participation status',
    'circumcised': '15. Are you circumcised?',
    'age': '16. At what age were you circumcised?',
    'regret': '17. How much do you regret being circumcised?',
    'partner': '39. How comfortable do you feel having a sexual partner see your penis?',
    'visibility': '40. How comfortable do you feel having other people see your penis?',
    'masculinity': 'When I think about my sexual life, I feel like less of a man',
}


def recode(series, mapping):
    unknown = set(series.dropna().unique()) - set(mapping)
    if unknown:
        raise ValueError(f'Unrecognized responses in {series.name}: {unknown}')
    return series.map(mapping)


def exact_association(frame, exposure, outcome, label, sample):
    # Row 0 is exposed, column 0 is outcome present: OR > 1 is positive.
    table = pd.crosstab(frame[exposure], frame[outcome]).reindex(
        index=[1, 0], columns=[1, 0], fill_value=0).to_numpy()
    estimate = odds_ratio(table, kind='conditional')
    ci = estimate.confidence_interval(confidence_level=.95)
    return dict(sample=sample, comparison=label, method='conditional exact OR; two-sided Fisher p',
                n=int(table.sum()), odds_ratio=estimate.statistic,
                sample_odds_ratio=odds_ratio(table, kind='sample').statistic, ci_low=ci.low,
                ci_high=ci.high, p=fisher_exact(table).pvalue)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'data/maloney/source.xlsx'
    spec = next(x for x in json.loads((ROOT/'config/sources.json').read_text())
                if x['path'] == 'data/maloney/source.xlsx')
    assert hashlib.sha256(source.read_bytes()).hexdigest() == spec['sha256']
    raw = pd.read_excel(source, sheet_name='umfrageonline-946995')
    d = raw[list(QUESTIONS.values())].rename(columns={v:k for k,v in QUESTIONS.items()})
    print({key: d[key].value_counts(dropna=False).to_dict() for key in ['status','circumcised','age']})
    eligible = d.status.eq('participated and completed') & d.circumcised.eq('yes') & d.age.isin([
        'Birth - 12 months', 'More than 1 year old - 18 years old'])
    d = d.loc[eligible].copy()
    regret = {'No regret':0, 'Minimal regret':1, 'Moderate regret':1,
              'Significant regret':1, 'Severe regret':1}
    comfort = {'Extremely comfortable':0, 'Comfortable':0, 'Minimal discomfort':1,
               'Moderate discomfort':1, 'Significant discomfort':1}
    d['regret'] = recode(d.regret, regret)
    d['visibility'] = recode(d.visibility, comfort)
    d['masculinity'] = recode(d.masculinity, {1:1,2:1,3:1,4:0,5:0,6:0})
    d['partner'] = recode(d.partner, comfort)
    primary = d.dropna(subset=['regret','visibility','masculinity'])
    samples = {'primary':primary, 'manuscript_sensitivity':primary.dropna(subset=['partner'])}
    associations, counts, flows = [], [], []
    for sample, frame in samples.items():
        flows.append(dict(sample=sample, n=len(frame), regret=int(frame.regret.sum())))
        assert len(frame) > 0, 'No eligible observations; inspect source labels.'
        count = frame.groupby(['masculinity','visibility','regret']).size().rename('n').reset_index()
        count.insert(0, 'sample', sample)
        counts.append(count)
        associations.append(exact_association(frame,'masculinity','regret','masculinity–regret',sample))
        associations.append(exact_association(frame,'masculinity','visibility','masculinity–visibility',sample))
        both_neither = frame.loc[frame.masculinity.eq(frame.visibility)]
        associations.append(exact_association(both_neither,'masculinity','regret','both versus neither–regret',sample))
        for interaction in [False, True]:
            x = frame[['masculinity','visibility']].astype(float).copy()
            if interaction:
                x['interaction'] = x.masculinity*x.visibility
            fit = sm.GLM(frame.regret.astype(float), sm.add_constant(x), family=sm.families.Binomial()).fit()
            if not fit.converged:
                raise RuntimeError('Maloney logistic model did not converge')
            ci = np.exp(fit.conf_int())
            for term in x:
                associations.append(dict(sample=sample, comparison=f'{"interaction" if interaction else "additive"} model: {term}',
                    method='binomial logit; Wald CI and p', n=len(frame), odds_ratio=np.exp(fit.params[term]),
                    ci_low=ci.loc[term,0],ci_high=ci.loc[term,1],p=fit.pvalues[term]))
    pd.concat(counts).to_csv(OUT/'joint_counts.csv',index=False)
    pd.DataFrame(associations).to_csv(OUT/'associations.csv',index=False)
    pd.DataFrame(flows).to_csv(OUT/'sample_flow.csv',index=False)
    (OUT/'validation.json').write_text(json.dumps(dict(source_sha256=spec['sha256'],
        source_rows=len(raw),eligible_rows=len(d),primary_rows=len(primary),
        sensitivity_rows=len(samples['manuscript_sensitivity']),
        explanation='Sensitivity additionally requires partner-visibility response, which is not used in the models.',
        unknown_labels_checked=True,logistic_models_converged=True),indent=2)+'\n')
    print('Maloney supplement completed:', flows)


if __name__ == '__main__':
    main()
