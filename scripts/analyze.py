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

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / 'data/raw', ROOT / 'outputs'
OUT.mkdir(exist_ok=True)
CYCLES = list(zip(range(2005, 2017, 2), 'DEFGHI'))
ADJUST = {
    'unadjusted': 'circ',
    'age_cycle': 'circ + age10 + I(age10**2) + C(cycle)',
    'demographic': 'circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education)',
    'full': 'circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born',
}


def codebook_audit(frame, name, variables):
    soup = BeautifulSoup((RAW / f'{name}.htm').read_text(), 'html.parser')
    rows, extracts = [], []
    for var in variables:
        tag = soup.find(id=var)
        assert tag is not None, (name, var)
        section = tag.parent
        extracts.append(section.get_text(' ', strip=True))
        for tr in section.select('table tbody tr'):
            cells = [td.get_text(' ', strip=True) for td in tr.find_all('td')]
            if len(cells) < 3:
                continue
            value, label, count = cells[:3]
            expected = int(count.replace(',', ''))
            if value == '.':
                observed = int(frame[var].isna().sum())
            elif ' to ' in value:
                lo, hi = map(float, value.split(' to '))
                observed = int(frame[var].between(lo, hi).sum())
            else:
                observed = int(frame[var].eq(float(value)).sum())
            rows.append(dict(file=name, variable=var, code=value, label=label,
                             expected=expected, observed=observed, passed=expected == observed))
            # Record discrepancies rather than silently editing source microdata.
            # Check analysis-critical discrepancies after all files are audited.
    return rows, extracts


def harmonize():
    frames, audit, extracts, routing, parser_checks = [], [], [], [], []
    for year, suffix in CYCLES:
        imported = {}
        for component in ['DEMO','SXQ']:
            path = RAW / f'{component}_{suffix}.XPT'
            frame, _ = pyreadstat.read_xport(str(path))
            alternate = pd.read_sas(path)
            assert list(frame.columns) == list(alternate.columns)
            # pandas' XPORT reader in this runtime decodes IBM floating zero
            # as 16**(-65). ReadStat reads the original bytes correctly.
            # Verify agreement after canonicalizing ONLY these tiny values.
            tiny = alternate.abs().lt(1e-70) & alternate.ne(0)
            canonical = alternate.mask(tiny,0.)
            np.testing.assert_allclose(frame.to_numpy(),canonical.to_numpy(),equal_nan=True,rtol=1e-12,atol=1e-12)
            parser_checks.append(dict(file=path.name,pandas_tiny_zeros=int(tiny.sum().sum()),
                                      agreement_after_zero_correction=True))
            imported[component] = frame
        demo, sxq = imported['DEMO'], imported['SXQ']
        assert demo.SEQN.is_unique and sxq.SEQN.is_unique
        assert set(sxq.SEQN).issubset(set(demo.SEQN))
        identity = 'SXQ296' if suffix == 'I' else 'SXQ292'
        birthplace = 'DMDBORN' if suffix == 'D' else ('DMDBORN2' if suffix in 'EF' else 'DMDBORN4')
        sv = ['SXQ280', identity, 'SXQ410', 'SXQ021' if suffix in 'DE' else 'SXQ809']
        av, ex = codebook_audit(sxq, f'SXQ_{suffix}', sv)
        audit += av
        extracts += [f'\n{year} SEXUAL BEHAVIOR\n'] + ex
        av, ex = codebook_audit(demo, f'DEMO_{suffix}', [birthplace, 'DMDEDUC2', 'RIDRETH1'])
        audit += av
        extracts += [f'\n{year} DEMOGRAPHICS\n'] + ex
        d = demo.merge(sxq, on='SEQN', how='left', validate='one_to_one', indicator=True)
        d['sxq_record'] = d['_merge'].eq('both')
        d['cycle'] = f'{year}-{year+1}'
        d['year'] = year
        d['weight'] = d.WTMEC2YR / 6
        d['stratum'] = d.cycle + '_' + d.SDMVSTRA.astype(int).astype(str)
        d['psu'] = d.stratum + '_' + d.SDMVPSU.astype(int).astype(str)
        d['eligible'] = d.RIAGENDR.eq(1) & d.RIDAGEYR.between(20, 59) & d.weight.gt(0)
        d['circ'] = d.SXQ280.map({1: 1., 2: 0.})
        gaycode, straightcode = (1, 2) if suffix == 'I' else (2, 1)
        d['identity_raw'] = d[identity]
        d['identity_gb'] = d[identity].map({straightcode: 0., gaycode: 1., 3: 1.})
        d['identity_gay'] = d[identity].map({straightcode: 0., gaycode: 1.})
        d['identity_bi'] = d[identity].map({straightcode: 0., 3: 1.})
        d['sex_ever'] = d['SXQ021' if suffix in 'DE' else 'SXD021'].map({1: 1., 2: 0.})
        if suffix in 'DE':
            count = d.SXQ410.where(d.SXQ410.between(0, 2000))
            assert (count.dropna() == count.dropna().round()).all()
            d['msm_ever'] = (count >= 1).astype(float).where(count.notna())
            conflict = d.sex_ever.eq(0) & count.gt(0)
            assert not conflict.any()
            d.loc[d.sex_ever.eq(0), 'msm_ever'] = 0.
            routing.append(dict(cycle=d.cycle.iloc[0], never_sex_coded_no=int((d.eligible & d.sex_ever.eq(0)).sum()),
                                inconsistent_never_sex_positive_count=int(conflict.sum())))
        else:
            d['msm_ever'] = d.SXQ809.map({1: 1., 2: 0.})
            conflict = d.SXQ809.eq(2) & d.SXQ410.between(1, 2000)
            assert not conflict.any()
            routing.append(dict(cycle=d.cycle.iloc[0], never_sex_coded_no=0,
                                inconsistent_no_msm_positive_count=int(conflict.sum())))
        d['age10'] = (d.RIDAGEYR - 40) / 10
        d['race'] = d.RIDRETH1.where(d.RIDRETH1.between(1, 5))
        d['education'] = d.DMDEDUC2.where(d.DMDEDUC2.between(1, 5))
        valid_born = [1, 2, 3] if suffix == 'D' else ([1, 2, 4, 5] if suffix in 'EF' else [1, 2])
        d['foreign_born'] = d[birthplace].ne(1).astype(float).where(d[birthplace].isin(valid_born))
        d['pir'] = d.INDFMPIR
        d['age_group'] = pd.cut(d.RIDAGEYR, [19, 29, 39, 49, 59], labels=False).astype(float)
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    assert d.SEQN.is_unique
    d = d[d.weight > 0].reset_index(drop=True)
    audits = pd.DataFrame(audit)
    audits.to_csv(OUT / 'codebook_frequency_audit.csv', index=False)
    discrepancies = audits[~audits.passed]
    print('Codebook discrepancies:', discrepancies.to_dict('records'), flush=True)
    critical = discrepancies[~((discrepancies.variable == 'SXQ410') & discrepancies.file.isin(['SXQ_F','SXQ_G','SXQ_H','SXQ_I']))]
    assert critical.empty, critical.to_dict('records')
    (OUT / 'codebook_extracts.txt').write_text('\n\n'.join(extracts))
    pd.DataFrame(routing).to_csv(OUT / 'routing_audit.csv', index=False)
    pd.DataFrame(parser_checks).to_csv(OUT / 'reader_crosscheck.csv', index=False)
    keep = ['SEQN','cycle','year','weight','stratum','psu','eligible','sxq_record','RIAGENDR',
            'RIDAGEYR','circ','identity_raw','identity_gb','identity_gay','identity_bi','sex_ever',
            'msm_ever','age10','race','education','foreign_born','pir','age_group','SXQ280']
    d[keep].to_csv(ROOT / 'data/analysis.csv.gz', index=False)
    return d


class Survey:
    def __init__(self, data):
        self.data = data
        self.units = data[['stratum', 'psu']].drop_duplicates().sort_values(['stratum','psu']).reset_index(drop=True)
        self.codes = pd.Categorical(data.psu, categories=self.units.psu).codes
        self.strata = list(self.units.groupby('stratum').indices.values())
        assert min(map(len, self.strata)) >= 2
        self.design_df = len(self.units) - len(self.strata)

    def covariance(self, influence):
        influence = np.asarray(influence)
        if influence.ndim == 1:
            influence = influence[:,None]
        totals = np.zeros((len(self.units), influence.shape[1]))
        np.add.at(totals, self.codes, influence)
        covariance = np.zeros((influence.shape[1], influence.shape[1]))
        for ids in self.strata:
            centered = totals[ids] - totals[ids].mean(axis=0)
            covariance += len(ids) / (len(ids)-1) * centered.T @ centered
        return covariance

    def domain_df(self, mask):
        units = self.data.loc[mask, ['stratum','psu']].drop_duplicates()
        return len(units) - units.stratum.nunique()

    def model(self, outcome, rhs, mask, label, jackknife=False):
        mask = np.asarray(mask) & self.data.eligible.to_numpy()
        y, x = patsy.dmatrices(f'{outcome} ~ {rhs}', self.data.loc[mask], return_type='dataframe')
        idx = x.index.to_numpy()
        w = self.data.loc[idx,'weight'].to_numpy()
        w = w / w.mean()
        X, Y = x.to_numpy(), y.iloc[:,0].to_numpy()
        fit = sm.GLM(Y, X, family=sm.families.Binomial(), freq_weights=w).fit(tol=1e-11, maxiter=100)
        assert fit.converged and np.linalg.matrix_rank(X) == X.shape[1]
        residual_score = X * (w * (Y-fit.fittedvalues))[:,None]
        bread = X.T @ ((w * fit.fittedvalues * (1-fit.fittedvalues))[:,None] * X)
        assert np.linalg.cond(bread) < 1e10, (label, 'unstable information matrix', np.linalg.cond(bread))
        inv = np.linalg.inv(bread)
        influence = np.zeros((len(self.data), X.shape[1]))
        influence[idx] = residual_score @ inv
        covariance = self.covariance(influence)
        j = list(x.columns).index('circ')
        beta, se = fit.params[j], np.sqrt(covariance[j,j])
        domain = np.zeros(len(self.data), dtype=bool)
        domain[idx] = True
        ddf = self.domain_df(domain)
        df = ddf - X.shape[1] + 1
        assert df > 0
        critical = t.ppf(.975, df)
        row = dict(outcome=outcome, model=label, n=len(idx), events=int(Y.sum()),
                   n_circ=int(self.data.loc[idx,'circ'].eq(1).sum()),
                   n_uncirc=int(self.data.loc[idx,'circ'].eq(0).sum()),
                   events_circ=int(Y[self.data.loc[idx,'circ'].eq(1)].sum()),
                   events_uncirc=int(Y[self.data.loc[idx,'circ'].eq(0)].sum()),
                   beta=beta, se=se, odds_ratio=np.exp(beta),
                   ci_low=np.exp(beta-critical*se), ci_high=np.exp(beta+critical*se),
                   p_value=2*t.sf(abs(beta/se),df), design_df=ddf, residual_df=df,
                   parameters=X.shape[1], max_abs_score=float(np.max(abs(residual_score.sum(axis=0)))),
                   kish_n=float(w.sum()**2/(w*w).sum()), formula=f'{outcome} ~ {rhs}')
        assert row['max_abs_score'] < 1e-6
        # Independent survey sandwich using PSU score totals before the bread.
        score_frame = pd.DataFrame(residual_score, index=idx)
        score_frame['psu'] = self.data.loc[idx,'psu']
        totals = score_frame.groupby('psu').sum().reindex(self.units.psu, fill_value=0).to_numpy()
        meat = np.zeros_like(bread)
        for ids in self.strata:
            a = totals[ids]
            meat += len(ids)/(len(ids)-1) * (a.T@a - np.outer(a.sum(axis=0), a.sum(axis=0))/len(ids))
        np.testing.assert_allclose(covariance, inv @ meat @ inv, rtol=1e-8, atol=1e-11)
        if label == 'unadjusted':
            c = self.data.loc[idx,'circ'].to_numpy()
            cells = [w[(c==a) & (Y==b)].sum() for a,b in [(1,1),(1,0),(0,1),(0,0)]]
            direct = cells[0]*cells[3]/(cells[1]*cells[2])
            np.testing.assert_allclose(row['odds_ratio'],direct,rtol=1e-8)
        if jackknife:
            # JKn deletes each PSU and upweights other PSUs within its stratum.
            # Center on the full estimate (mse=TRUE), retaining all other strata.
            codes = self.codes[idx]
            variance = 0.
            for ids in self.strata:
                h = np.isin(codes, ids)
                for deleted in ids:
                    rw = w.copy()
                    rw[h] *= len(ids)/(len(ids)-1)
                    rw[codes == deleted] = 0
                    rf = sm.GLM(Y, X, family=sm.families.Binomial(), freq_weights=rw).fit(
                        start_params=fit.params, tol=1e-10, maxiter=80)
                    assert rf.converged
                    variance += (len(ids)-1)/len(ids) * (rf.params[j]-beta)**2
            row['jackknife_se'] = np.sqrt(variance)
            row['jackknife_taylor_se_ratio'] = np.sqrt(variance)/se
        return row, domain

    def prevalence(self, outcome, mask):
        records, influences = [], []
        for c in [0,1]:
            m = mask & self.data.circ.eq(c) & self.data[outcome].notna()
            w = self.data.loc[m,'weight'].to_numpy()
            y = self.data.loc[m,outcome].to_numpy()
            p = np.average(y,weights=w)
            influence = np.zeros(len(self.data))
            influence[m] = w*(y-p)/w.sum()
            se = np.sqrt(self.covariance(influence)[0,0])
            df = self.domain_df(m)
            limits = expit(logit(p) + np.array([-1,1])*t.ppf(.975,df)*se/(p*(1-p)))
            records.append(dict(outcome=outcome, circ=c, n=len(y), events=int(y.sum()),
                                prevalence=p, se=se, ci_low=limits[0], ci_high=limits[1],
                                kish_n=w.sum()**2/(w*w).sum(), design_df=df))
            influences.append(influence)
        delta = records[1]['prevalence'] - records[0]['prevalence']
        se = np.sqrt(self.covariance(influences[1]-influences[0])[0,0])
        df = self.domain_df(mask & self.data[outcome].notna() & self.data.circ.notna())
        diff = dict(outcome=outcome, difference=delta, se=se,
                    ci_low=delta-t.ppf(.975,df)*se,ci_high=delta+t.ppf(.975,df)*se,
                    p_value=2*t.sf(abs(delta/se),df))
        return records, diff


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


if __name__ == '__main__':
    main()
