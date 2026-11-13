"""Check planned outputs, paired replicate calculations, and source integrity."""
import hashlib
import json

import numpy as np
import pandas as pd
import patsy
from scipy.stats import t
from statsmodels.stats.multitest import multipletests

from src.frequentist.explanations import ROOT, RAW, OUT, COMMON, Survey, proportion


def main():
    d = pd.read_csv(ROOT / 'data/explanation_extension.csv.gz')
    models = pd.read_csv(OUT / 'models.csv')
    focal = pd.read_csv(OUT / 'focal_tests.csv')
    assert len(models) == 26 and len(focal) == 10
    digest = hashlib.sha256((ROOT / 'config/analysis.json').read_bytes()).hexdigest()
    assert digest == json.loads((OUT / 'validation.json').read_text())['specification_sha256']
    files = json.loads((RAW / 'manifest.json').read_text())
    for source in files:
        assert hashlib.sha256((RAW / source['file']).read_bytes()).hexdigest() == source['sha256']
    # Original 2009–2016 domain fit must be reproduced before interpretation.
    original = pd.read_csv(ROOT / 'outputs/frequentist/sensitivities.csv')
    target = original[(original.outcome == 'msm_ever') & (original.model == 'direct_behavior_2009_2016')].iloc[0]
    base = models[(models.era == '2009-2016') & (models.model == 'culture_all_M0_available')].iloc[0]
    assert int(target.n) == int(base.n) and int(target.events) == int(base.events)
    np.testing.assert_allclose(target.beta, base.beta, atol=1e-10)
    checks, prevalence, overlap = [], [], []
    for era in ['2009-2016', '2009-2014']:
        sub = d.copy() if era == '2009-2016' else d[d.year.lt(2015)].copy()
        if era == '2009-2014':
            sub.weight *= 4 / 3
        sub = sub.reset_index(drop=True)
        survey = Survey(sub)
        reps = np.load(OUT / ('replicates_' + era + '.npz'))
        factor = reps['replicate_factors']
        f = focal[focal.era.eq(era)].sort_values('test')
        np.testing.assert_allclose(multipletests(f.p_value.fillna(1), method='holm')[1], f.p_holm)
        for row in f.itertuples():
            if row.status != 'estimated':
                assert row.failed_test_placeholder_for_holm and pd.isna(row.p_value)
                continue
            if row.test == 1:
                a, b = reps['culture_all_M0'][:, 3], reps['culture_all_M2'][:, 3]
            elif row.test == 2:
                a, b = reps['oral_male'][:, 4], reps['oral_female'][:, 4]
            else:
                a, b = reps[row.models][:, 0], np.zeros(len(factor))
            delta = a - b - row.point_on_test_scale
            se = np.sqrt(np.dot(factor, delta ** 2))
            np.testing.assert_allclose(se, row.se, atol=1e-12)
            np.testing.assert_allclose(2 * t.sf(abs(row.point_on_test_scale / se), row.df), row.p_value, atol=1e-12)
            checks.append(dict(era=era, test=row.test, paired_replicate_variance_verified=True))
        for row in models[models.era.eq(era)].itertuples():
            pop = sub.eligible.copy()
            if not row.model.startswith('culture_all'):
                pop &= sub.heterosexual
            if row.model.endswith('_conditional'):
                pop &= sub.msm_ever.eq(1)
            needed = COMMON + [row.outcome]
            if row.model.startswith('culture') and not row.model.endswith('_available'):
                needed += ['residence', 'nonenglish']
            if row.model.startswith('oral_'):
                needed += ['oral_male', 'oral_female']
            mask = pop & sub[needed].notna().all(axis=1)
            y, x = patsy.dmatrices(row.formula, sub.loc[mask], return_type='dataframe')
            assert len(x) == row.n and int(y.iloc[:, 0].sum()) == row.events
            for c in [0, 1]:
                prev = proportion(survey, mask & sub.circ.eq(c), sub[row.outcome].fillna(0))
                prevalence.append(dict(era=era, model=row.model, circ=c, **prev))
            for variable in ['race', 'education', 'foreign_born', 'residence', 'nonenglish']:
                for level in sorted(sub.loc[mask, variable].dropna().unique()):
                    cell = mask & sub[variable].eq(level)
                    counts = [int((cell & sub.circ.eq(c)).sum()) for c in [0, 1]]
                    overlap.append(dict(era=era, model=row.model, variable=variable, level=level,
                                        n_uncirc=counts[0], n_circ=counts[1], both_exposures_present=all(counts)))
    desc = pd.read_csv(OUT / 'descriptive_distributions.csv')
    for _, group in desc.groupby(['circ', 'variable']):
        np.testing.assert_allclose(group.prevalence.sum(), 1., atol=1e-12)
        assert group.events.sum() == group.n.iloc[0]
    pd.DataFrame(prevalence).to_csv(OUT / 'model_prevalence.csv', index=False)
    pd.DataFrame(overlap).to_csv(OUT / 'exposure_overlap.csv', index=False)
    (OUT / 'independent_output_checks.json').write_text(json.dumps(dict(
        specification_hash_verified=True, unchanged_source_files=len(files),
        original_2009_2016_point_estimate_reproduced=True,
        holm_correction_verified=True, exhaustive_distributions_verified=True,
        model_sample_reconstruction_verified=True, contrast_checks=checks), indent=2))
    print('PASS: specification, source hashes, original fit, sample reconstruction, paired variance, Holm, distributions')


if __name__ == '__main__':
    main()
