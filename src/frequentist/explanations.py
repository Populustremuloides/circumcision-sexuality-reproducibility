"""Execute the five explanatory contrasts described in docs/methods.md.

No model selection. Preserve failed fits and jackknife failures in outputs.
Run with OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1.
"""
import hashlib
import json
import warnings
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import patsy
import pyreadstat
import statsmodels.api as sm
from scipy.special import expit, logit
from scipy.stats import t
from statsmodels.stats.multitest import multipletests
from statsmodels.tools.sm_exceptions import PerfectSeparationWarning

from src.frequentist.nhanes import ROOT, RAW, Survey, ADJUST, codebook_audit

OUT = ROOT / 'outputs/frequentist/explanations'
BASE = ADJUST['full']
RESIDENCE = BASE.replace('foreign_born', 'C(residence)')
LANGUAGE = RESIDENCE + ' + nonenglish'
COMMON = ['circ', 'age10', 'cycle', 'race', 'education', 'foreign_born']
METRICS = ['beta', 'p0', 'p1', 'rd', 'log_pr']


def analysis_provenance():
    OUT.mkdir(exist_ok=True)
    return hashlib.sha256((ROOT / 'config/analysis.json').read_bytes()).hexdigest()


def harmonize():
    d = pd.read_csv(ROOT / 'data/analysis.csv.gz')
    d = d[d.year.ge(2009)].reset_index(drop=True)
    d.weight *= 6 / 4
    audit, extracts, parts, route = [], [], [], []
    sxvars = ['SXQ809', 'SXQ803', 'SXQ853', 'SXQ800', 'SXQ806',
              'SXD171', 'SXQ410', 'SXQ550', 'SXD021']
    for suffix in 'FGHI':
        sx, _ = pyreadstat.read_xport(str(RAW / f'SXQ_{suffix}.XPT'))
        demo, _ = pyreadstat.read_xport(str(RAW / f'DEMO_{suffix}.XPT'))
        # Independent reader check, retaining the previously identified IBM-zero fix.
        alternate = pd.read_sas(RAW / f'SXQ_{suffix}.XPT')[sxvars]
        alternate = alternate.mask(alternate.abs().lt(1e-70) & alternate.ne(0), 0.)
        np.testing.assert_allclose(sx[sxvars], alternate, equal_nan=True, atol=1e-12, rtol=1e-12)
        lang = 'AIALANG' if suffix == 'F' else 'AIALANGA'
        for frame, stem, variables in [(sx, 'SXQ', sxvars), (demo, 'DEMO', ['DMDYRSUS', lang])]:
            av, ex = codebook_audit(frame, f'{stem}_{suffix}', variables)
            audit.extend(av)
            extracts.extend(ex)
        a = demo[['SEQN', 'DMDYRSUS', lang]].rename(columns={lang: 'acasi_language'})
        a = a.merge(sx[['SEQN'] + sxvars], on='SEQN', how='left', validate='one_to_one')
        parts.append(a)
    aud = pd.DataFrame(audit)
    aud.to_csv(OUT / 'codebook_audit.csv', index=False)
    (OUT / 'codebook_extracts.txt').write_text('\n\n'.join(extracts))
    # CDC 2009 count tables include top-coded values absent from the XPT.
    # Both readers agree on missing values. Keep them missing, never reconstruct
    # values from aggregate documentation or assign them to particular people.
    bad = aud[~aud.passed]
    expected_discrepancies = {('SXQ_F', 'SXD171', '2000'): (5, 0),
                             ('SXQ_F', 'SXD171', '.'): (3039, 3044),
                             ('SXQ_F', 'SXQ410', '2000'): (1, 0),
                             ('SXQ_F', 'SXQ410', '.'): (5197, 5198)}
    actual = {(r.file, r.variable, r.code): (r.expected, r.observed) for r in bad.itertuples()}
    assert actual == expected_discrepancies, actual
    d = d.merge(pd.concat(parts), on='SEQN', how='left', validate='one_to_one')
    d['residence'] = np.nan
    d.loc[d.foreign_born.eq(0), 'residence'] = 0
    d.loc[d.foreign_born.eq(1) & d.DMDYRSUS.between(1, 3), 'residence'] = 1
    d.loc[d.foreign_born.eq(1) & d.DMDYRSUS.between(4, 9), 'residence'] = 2
    d['nonenglish'] = d.acasi_language.map({1: 0., 2: 1., 3: 1.})
    yes, no = d.SXQ809.eq(1), d.SXQ809.eq(2)
    np.testing.assert_allclose(d.msm_ever, d.SXQ809.map({1: 1., 2: 0.}), equal_nan=True)
    female_no = d[['SXQ800', 'SXQ803', 'SXQ806']].eq(2).all(axis=1)
    female_yes = d[['SXQ800', 'SXQ803', 'SXQ806']].eq(1).any(axis=1)
    for raw, name in [('SXD171', 'female_count'), ('SXQ410', 'male_count'), ('SXQ550', 'male_year_count')]:
        # Threshold endpoints are unaffected by 100+/2000+ top codes.
        values = d[raw].where(d[raw].between(0, 2000))
        assert values.dropna().eq(values.dropna().round()).all()
        unexpected = d[raw].notna() & ~d[raw].isin([77777, 99999]) & values.isna()
        assert not unexpected.any(), (raw, d.loc[unexpected, raw].unique())
        d[name] = values
    d['oral_male'] = d.SXQ853.map({1: 1., 2: 0.}).where(yes)
    d.loc[no, 'oral_male'] = 0.
    d['oral_female'] = d.SXQ803.map({1: 1., 2: 0.})
    # Only documented, affirmative negative screening responses imply zero.
    d.loc[no, ['male_count', 'male_year_count']] = 0.
    d.loc[~(yes | no), ['male_count', 'male_year_count']] = np.nan
    d.loc[female_no, 'female_count'] = 0.
    # Valid female counts are asked only after a positive female screen.
    d.loc[~(female_yes | female_no), 'female_count'] = np.nan
    conflicts = {
        'no_male_screen_positive_lifetime': no & d.SXQ410.between(1, 2000),
        'no_male_screen_positive_year': no & d.SXQ550.between(1, 2000),
        'no_male_screen_positive_oral': no & d.SXQ853.eq(1),
        'yes_male_screen_zero_lifetime': yes & d.SXQ410.eq(0),
        'year_exceeds_lifetime': yes & d.male_year_count.gt(d.male_count),
        'no_female_screen_positive_count': female_no & d.SXD171.between(1, 2000),
        'yes_female_screen_zero_count': female_yes & d.SXD171.eq(0),
    }
    affected = {
        'no_male_screen_positive_lifetime': ['male_count'],
        'no_male_screen_positive_year': ['male_year_count'],
        'no_male_screen_positive_oral': ['oral_male'],
        'yes_male_screen_zero_lifetime': ['male_count'],
        'year_exceeds_lifetime': ['male_year_count'],
        'no_female_screen_positive_count': ['female_count'],
        'yes_female_screen_zero_count': ['female_count'],
    }
    for label, mask in conflicts.items():
        for cycle in d.cycle.unique():
            route.append(dict(cycle=cycle, rule=label, n=int((mask & d.eligible & d.cycle.eq(cycle)).sum())))
        d.loc[mask, affected[label]] = np.nan
    for count, outcome in [('female_count', 'female_multiple'), ('male_count', 'male_multiple')]:
        d[outcome] = d[count].ge(2).astype(float).where(d[count].notna())
    d['male_recent'] = d.male_year_count.ge(1).astype(float).where(d.male_year_count.notna())
    d['heterosexual'] = d.identity_gb.eq(0)
    pd.DataFrame(route).to_csv(OUT / 'routing_audit.csv', index=False)
    d.to_csv(ROOT / 'data/explanation_extension.csv.gz', index=False)
    return d, bad.to_dict('records')


def checked_fit(Y, X, w, start=None):
    with warnings.catch_warnings():
        warnings.simplefilter('error', PerfectSeparationWarning)
        f = sm.GLM(Y, X, family=sm.families.Binomial(), freq_weights=w).fit(
            start_params=start, tol=1e-11, maxiter=100)
    if not f.converged:
        raise ValueError('GLM did not converge')
    bread = X.T @ ((w * f.fittedvalues * (1 - f.fittedvalues))[:, None] * X)
    condition = np.linalg.cond(bread)
    if not np.isfinite(condition) or condition >= 1e10:
        raise ValueError(f'Unstable information matrix, condition={condition:g}')
    if np.max(np.abs(X.T @ (w * (Y - f.fittedvalues)))) >= 1e-6:
        raise ValueError('Score residual exceeds tolerance')
    return f, condition


class Runner:
    def __init__(self, d, era):
        self.d, self.era = d.reset_index(drop=True), era
        self.s = Survey(self.d)
        self.models, self.flows, self.validation, self.replicates = [], [], [], {}
        self.rep_psus, self.rep_factors = [], []
        for ids in self.s.strata:
            for deleted in ids:
                self.rep_psus.append((ids, deleted))
                self.rep_factors.append((len(ids) - 1) / len(ids))
        self.rep_factors = np.asarray(self.rep_factors)

    def variance(self, point, reps):
        return np.sum(self.rep_factors[:, None] * (reps - point) ** 2, axis=0)

    def model(self, label, outcome, rhs, population, extra=()):
        d = self.d
        mask = d.eligible & population
        for step, variables in [('population', []), ('known_circ', ['circ']),
                                ('known_outcome', ['circ', outcome]),
                                ('common_complete_cases', COMMON + [outcome] + list(extra))]:
            m = mask & d[variables].notna().all(axis=1)
            self.flows.append(dict(era=self.era, model=label, step=step, n=int(m.sum()),
                                   weighted_population=float(d.loc[m, 'weight'].sum())))
        mask &= d[COMMON + [outcome] + list(extra)].notna().all(axis=1)
        y, x = patsy.dmatrices(f'{outcome} ~ {rhs}', d.loc[mask], return_type='dataframe')
        idx, X, Y = x.index.to_numpy(), x.to_numpy(), y.iloc[:, 0].to_numpy()
        c = d.loc[idx, 'circ'].to_numpy()
        w = d.loc[idx, 'weight'].to_numpy()
        w /= w.mean()
        row = dict(era=self.era, model=label, outcome=outcome, formula=f'{outcome} ~ {rhs}',
                   n=len(idx), events=int(Y.sum()), n_uncirc=int((c == 0).sum()), n_circ=int((c == 1).sum()),
                   events_uncirc=int(Y[c == 0].sum()), events_circ=int(Y[c == 1].sum()),
                   parameters=X.shape[1], status='not_estimable')
        for value, suffix in [(0, 'uncirc'), (1, 'circ')]:
            row['raw_prevalence_' + suffix] = np.average(Y[c == value], weights=w[c == value]) if (c == value).any() else np.nan
        m = np.zeros(len(d), dtype=bool)
        m[idx] = True
        df = self.s.domain_df(m) - X.shape[1] + 1
        row['df'] = df
        result = dict(row=row, idx=idx, point=None, reps=None, df=df)
        try:
            assert df > 0 and np.linalg.matrix_rank(X) == X.shape[1], 'Insufficient df or rank-deficient model'
            assert set(c) == {0, 1} and set(Y) == {0, 1}, 'No exposure or outcome variation'
            fit, cond = checked_fit(Y, X, w)
            j = list(x.columns).index('circ')
            X0, X1 = X.copy(), X.copy()
            X0[:, j], X1[:, j] = 0., 1.

            def estimate(f, weights):
                p0 = np.average(expit(X0 @ f.params), weights=weights)
                p1 = np.average(expit(X1 @ f.params), weights=weights)
                return np.array([f.params[j], p0, p1, p1 - p0, np.log(p1 / p0)])

            point = estimate(fit, w)
            result['point'] = point
            row.update(dict(zip(METRICS, point)))
            row['condition'] = cond
            reference, _ = self.s.model(outcome, rhs, m, label)
            np.testing.assert_allclose(point[0], reference['beta'], atol=1e-9)
            row['taylor_se_beta'] = reference['se']
            scale_fit, _ = checked_fit(Y, X, w * 3)
            np.testing.assert_allclose(estimate(scale_fit, w * 3), point, atol=1e-8)
            codes = self.s.codes[idx]
            reps, failures = [], []
            for ids, deleted in self.rep_psus:
                rw = w.copy()
                rw[np.isin(codes, ids)] *= len(ids) / (len(ids) - 1)
                rw[codes == deleted] = 0.
                try:
                    rf, _ = checked_fit(Y, X, rw, fit.params)
                    reps.append(estimate(rf, rw))
                except (ValueError, AssertionError, np.linalg.LinAlgError, PerfectSeparationWarning) as e:
                    reps.append(np.full(5, np.nan))
                    failures.append(dict(deleted_psu=str(self.s.units.iloc[deleted].psu), error=str(e)))
            row['replicate_failures'] = len(failures)
            if failures:
                row['error'] = json.dumps(failures)
                self.validation.append(dict(model=label, failures=failures))
            else:
                reps = np.asarray(reps)
                result['reps'] = reps
                self.replicates[label] = reps
                se = np.sqrt(self.variance(point, reps))
                critical = t.ppf(.975, df)
                row['status'] = 'estimated'
                for k, name in enumerate(METRICS):
                    row[name + '_se'] = se[k]
                    row[name + '_low'] = point[k] - critical * se[k]
                    row[name + '_high'] = point[k] + critical * se[k]
                for name, k in [('odds_ratio', 0), ('prevalence_ratio', 4)]:
                    row[name] = np.exp(point[k])
                    row[name + '_low'], row[name + '_high'] = np.exp(point[k] + np.array([-1, 1]) * critical * se[k])
                row['jackknife_taylor_ratio'] = se[0] / reference['se']
                self.validation.append(dict(model=label, scale_invariance=True,
                    original_taylor_point_agreement=True, jackknife_taylor_ratio=row['jackknife_taylor_ratio'],
                    condition=cond, complete_replicates=len(reps)))
        except (ValueError, AssertionError, np.linalg.LinAlgError, PerfectSeparationWarning) as e:
            row['error'] = str(e)
        self.models.append(row)
        print(self.era, label, row['status'], 'n=', row['n'], 'replicate_failures=', row.get('replicate_failures'), flush=True)
        return result

    def contrast(self, number, name, results, metric, transform='identity'):
        row = dict(era=self.era, test=number, comparison=name, status='not_estimable', scale=transform)
        row['models'] = ','.join(r['row']['model'] for r in results)
        row['n'] = results[0]['row']['n']
        row['df'] = min(r['df'] for r in results)
        assert all(np.array_equal(r['idx'], results[0]['idx']) for r in results), 'Paired comparison sample mismatch'
        if all(r['point'] is not None for r in results):
            point = float(metric(*[r['point'] for r in results]))
            row['point_on_test_scale'] = point
            row['estimate'] = np.exp(point) if transform == 'ratio' else point
        if all(r['reps'] is not None for r in results):
            reps = np.array([metric(*a) for a in zip(*[r['reps'] for r in results])])
            variance = np.sum(self.rep_factors * (reps - point) ** 2)
            se = np.sqrt(variance)
            df = row['df']
            critical = t.ppf(.975, df)
            lo, hi = point - critical * se, point + critical * se
            row.update(status='estimated', se=se, p_value=float(2 * t.sf(abs(point / se), df)),
                       ci_low=np.exp(lo) if transform == 'ratio' else lo,
                       ci_high=np.exp(hi) if transform == 'ratio' else hi)
        return row

    def run(self):
        d = self.d
        allmen = d.eligible
        het = d.heterosexual
        tests = []
        for pop, label in [(allmen, 'all'), (het, 'heterosexual')]:
            self.model('culture_' + label + '_M0_available', 'msm_ever', BASE, pop)
            models = [self.model('culture_' + label + '_' + name, 'msm_ever', rhs, pop,
                                 ['residence', 'nonenglish'])
                      for name, rhs in [('M0', BASE), ('M1', RESIDENCE), ('M2', LANGUAGE)]]
            if label == 'all':
                tests.append(self.contrast(1, 'Reduction in adjusted prevalence difference',
                                           [models[0], models[2]], lambda a, b: a[3] - b[3]))
        oral = [self.model('oral_' + sex, outcome, BASE, het, ['oral_male', 'oral_female'])
                for sex, outcome in [('male', 'oral_male'), ('female', 'oral_female')]]
        tests.append(self.contrast(2, 'Male versus female oral prevalence-ratio contrast', oral,
                                   lambda a, b: a[4] - b[4], 'ratio'))
        for number, label, outcome, pop in [
            (3, 'female_multiple', 'female_multiple', het),
            (4, 'male_multiple_conditional', 'male_multiple', het & d.msm_ever.eq(1)),
            (5, 'male_recent_conditional', 'male_recent', het & d.msm_ever.eq(1)),
        ]:
            model = self.model(label, outcome, BASE, pop)
            tests.append(self.contrast(number, label, [model], lambda a: a[0], 'ratio'))
        tests = pd.DataFrame(tests)
        tests['p_holm'] = multipletests(tests.p_value.fillna(1), method='holm')[1]
        tests['failed_test_placeholder_for_holm'] = tests.status.ne('estimated')
        return tests


def proportion(s, mask, y):
    d = s.data
    mask = np.asarray(mask)
    w = d.loc[mask, 'weight'].to_numpy()
    values = np.asarray(y)[mask].astype(float)
    if not len(w):
        return dict(n=0, events=0, prevalence=np.nan, ci_low=np.nan, ci_high=np.nan)
    p = np.average(values, weights=w)
    influence = np.zeros(len(d))
    influence[mask] = w * (values - p) / w.sum()
    se = np.sqrt(s.covariance(influence)[0, 0])
    df = s.domain_df(mask)
    lo, hi = np.nan, np.nan
    if 0 < p < 1 and df > 0:
        lo, hi = expit(logit(p) + np.array([-1, 1]) * t.ppf(.975, df) * se / (p * (1 - p)))
    return dict(n=len(w), events=int(values.sum()), prevalence=p, ci_low=lo, ci_high=hi,
                se=se, design_df=df, weighted_population=float(w.sum()),
                boundary_interval_unavailable=bool(p in (0, 1)))


def descriptives(d):
    s = Survey(d)
    rows = []
    for c in [0, 1]:
        pop = d.eligible & d.heterosexual & d.circ.eq(c)
        for field, levels in [('female_count', [('0', lambda x: x.eq(0)), ('1', lambda x: x.eq(1)),
                ('2-4', lambda x: x.between(2, 4)), ('5+', lambda x: x.ge(5))]),
                ('male_count', [('0', lambda x: x.eq(0)), ('1', lambda x: x.eq(1)), ('2+', lambda x: x.ge(2))]),
                ('male_recent', [('no', lambda x: x.eq(0)), ('yes', lambda x: x.eq(1))])]:
            # Unknown is an explicit category, with all heterosexual men in denominator.
            for label, rule in levels + [('unknown', lambda x: x.isna())]:
                rows.append(dict(circ=c, variable=field, category=label,
                                 **proportion(s, pop, rule(d[field]))))
    pd.DataFrame(rows).to_csv(OUT / 'descriptive_distributions.csv', index=False)
    missing = []
    groupings = [('overall', 'all', d.eligible)]
    for cycle in d.cycle.unique():
        groupings.append(('cycle', cycle, d.eligible & d.cycle.eq(cycle)))
    for lang in [1, 2, 3, None]:
        groupings.append(('language', str(lang), d.eligible & (d.acasi_language.eq(lang) if lang else d.acasi_language.isna())))
    for c in [0, 1]:
        groupings.append(('circ', str(c), d.eligible & d.circ.eq(c)))
    for field in ['SXQ280', 'identity_raw', 'SXQ809']:
        states = {'missing_record': ~d.sxq_record, 'refused': d.sxq_record & d[field].eq(7),
                  'dont_know': d.sxq_record & d[field].eq(9),
                  'missing_item': d.sxq_record & d[field].isna()}
        # Identity's explicit unsure category is code 5, distinct from missing/refused.
        if field == 'identity_raw':
            states['unsure_identity'] = d.sxq_record & d[field].eq(5)
        states['any_unanswered'] = states['missing_record'] | states['refused'] | states['dont_know'] | states['missing_item']
        for dimension, value, mask in groupings:
            if field == 'SXQ280' and dimension == 'circ':
                continue
            for state, y in states.items():
                missing.append(dict(variable=field, grouping=dimension, group=value, state=state,
                                    **proportion(s, mask, y)))
    pd.DataFrame(missing).to_csv(OUT / 'missingness.csv', index=False)
    # All three screening/exposure items are scheduled for eligible men. No
    # structural missing values are reclassified as item nonresponse here.


def main():
    digest = analysis_provenance()
    d, discrepancies = harmonize()
    descriptives(d)
    models, focal, flows, checks = [], [], [], []
    for era, subset in [('2009-2016', d), ('2009-2014', d[d.year.lt(2015)].copy())]:
        if era == '2009-2014':
            subset.weight *= 4 / 3
        runner = Runner(subset, era)
        focal.append(runner.run())
        models.extend(runner.models)
        flows.extend(runner.flows)
        checks.append(dict(era=era, psus=len(runner.s.units), strata=len(runner.s.strata),
                           design_df=runner.s.design_df, checks=runner.validation))
        np.savez_compressed(OUT / ('replicates_' + era + '.npz'),
                            replicate_factors=runner.rep_factors, **runner.replicates)
    pd.DataFrame(models).to_csv(OUT / 'models.csv', index=False)
    pd.concat(focal, ignore_index=True).to_csv(OUT / 'focal_tests.csv', index=False)
    pd.DataFrame(flows).to_csv(OUT / 'sample_flow.csv', index=False)
    (OUT / 'validation.json').write_text(json.dumps(dict(specification_sha256=digest,
        executed_utc=datetime.now(timezone.utc).isoformat(), source_discrepancies=discrepancies,
        eras=checks, failed_models=[r for r in models if r['status'] != 'estimated']), indent=2))
    print(pd.concat(focal).to_string(index=False), flush=True)


if __name__ == '__main__':
    main()
