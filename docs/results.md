# Results and code

Generated from validated frequentist records. All p-values are nominal and two-sided unless a named Holm family is displayed.

## Lifetime male–male behavior

Analysis `nhanes.msm_ever.adjusted`; N = 9,161, events = 498.

```sh
python -m analyses.nhanes.run --analysis nhanes.msm_ever.adjusted
```

Formula: `msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[Specification](../config/analyses.json) · [Runner](../analyses/nhanes/run.py) · [Survey estimator](../src/survey/design.py). Result: `outputs/frequentist/headline/nhanes.msm_ever.adjusted.json`; complete fitted coefficients, covariance and standardization inputs: corresponding `.npz`.

## Gay/bisexual versus heterosexual identity

Analysis `nhanes.identity_gb.adjusted`; N = 8,962, events = 333.

```sh
python -m analyses.nhanes.run --analysis nhanes.identity_gb.adjusted
```

Formula: `identity_gb ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[Specification](../config/analyses.json) · [Runner](../analyses/nhanes/run.py) · [Survey estimator](../src/survey/design.py). Result: `outputs/frequentist/headline/nhanes.identity_gb.adjusted.json`; complete fitted coefficients, covariance and standardization inputs: corresponding `.npz`.

## Gay versus heterosexual identity

Analysis `nhanes.identity_gay.adjusted`; N = 8,825, events = 196.

```sh
python -m analyses.nhanes.run --analysis nhanes.identity_gay.adjusted
```

Formula: `identity_gay ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[Specification](../config/analyses.json) · [Runner](../analyses/nhanes/run.py) · [Survey estimator](../src/survey/design.py). Result: `outputs/frequentist/headline/nhanes.identity_gay.adjusted.json`; complete fitted coefficients, covariance and standardization inputs: corresponding `.npz`.

## Bisexual versus heterosexual identity

Analysis `nhanes.identity_bi.adjusted`; N = 8,766, events = 137.

```sh
python -m analyses.nhanes.run --analysis nhanes.identity_bi.adjusted
```

Formula: `identity_bi ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[Specification](../config/analyses.json) · [Runner](../analyses/nhanes/run.py) · [Survey estimator](../src/survey/design.py). Result: `outputs/frequentist/headline/nhanes.identity_bi.adjusted.json`; complete fitted coefficients, covariance and standardization inputs: corresponding `.npz`.

## Figure inputs

The unchanged primary frequentist model gives OR 1.543297 (95% CI 1.162706–2.048467), p = 0.003125. Standardizing to the survey-weighted circumcised complete-case covariate distribution (n = 6,463) gives intact-reference probability 4.448015%, circumcised probability 6.680342%, and gap 2.232327 percentage points. Both figures use these same fitted coefficients and targets. They show point scenarios, without scenario confidence intervals.

[Coefficient export and hash verification](../src/frequentist/export.py) · [Figure checks](../validation/figures.py).

## Raw survey-weighted prevalence

These available-case descriptive prevalences use their own observed circumcision groups. They are not the counterfactual model-standardized figure probabilities.

| outcome | circ | n | events | prevalence | se | ci_low | ci_high | kish_n | design_df |
|---|---|---|---|---|---|---|---|---|---|
| identity_gb | 0 | 2608 | 68 | 0.0294817 | 0.00412448 | 0.0223075 | 0.0388715 | 1698.98 | 94 |
| identity_gb | 1 | 6362 | 265 | 0.0433765 | 0.00465166 | 0.0350239 | 0.0536104 | 4212.91 | 94 |
| msm_ever | 0 | 2702 | 97 | 0.0368974 | 0.00458041 | 0.028806 | 0.0471513 | 1766.21 | 94 |
| msm_ever | 1 | 6467 | 401 | 0.066746 | 0.00531213 | 0.0569413 | 0.0780991 | 4268.64 | 94 |

See [extension results](extension_results.md) for the retained sensitivity families.
