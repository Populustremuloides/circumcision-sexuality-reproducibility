# Results and code

Generated from validated frequentist records. All p-values are nominal and two-sided unless a named Holm family is displayed.

## Lifetime male–male behavior (1999–2016)

Analysis `nhanes.msm_ever.adjusted`; N = 12,973, events = 662.

```sh
python -m analyses.nhanes.run --analysis nhanes.msm_ever.adjusted
```

Formula: `msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[Specification](../config/analyses.json) · [Runner](../analyses/nhanes/run.py) · [Survey estimator](../src/survey/design.py). Result: `outputs/frequentist/headline/nhanes.msm_ever.adjusted.json`; complete fitted coefficients, covariance and standardization inputs: corresponding `.npz`.

## Gay/bisexual versus heterosexual identity (2005–2016)

Analysis `nhanes.identity_gb.adjusted`; N = 8,962, events = 333.

```sh
python -m analyses.nhanes.run --analysis nhanes.identity_gb.adjusted
```

Formula: `identity_gb ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[Specification](../config/analyses.json) · [Runner](../analyses/nhanes/run.py) · [Survey estimator](../src/survey/design.py). Result: `outputs/frequentist/headline/nhanes.identity_gb.adjusted.json`; complete fitted coefficients, covariance and standardization inputs: corresponding `.npz`.

## Gay versus heterosexual identity (2005–2016)

Analysis `nhanes.identity_gay.adjusted`; N = 8,825, events = 196.

```sh
python -m analyses.nhanes.run --analysis nhanes.identity_gay.adjusted
```

Formula: `identity_gay ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[Specification](../config/analyses.json) · [Runner](../analyses/nhanes/run.py) · [Survey estimator](../src/survey/design.py). Result: `outputs/frequentist/headline/nhanes.identity_gay.adjusted.json`; complete fitted coefficients, covariance and standardization inputs: corresponding `.npz`.

## Bisexual versus heterosexual identity (2005–2016)

Analysis `nhanes.identity_bi.adjusted`; N = 8,766, events = 137.

```sh
python -m analyses.nhanes.run --analysis nhanes.identity_bi.adjusted
```

Formula: `identity_bi ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[Specification](../config/analyses.json) · [Runner](../analyses/nhanes/run.py) · [Survey estimator](../src/survey/design.py). Result: `outputs/frequentist/headline/nhanes.identity_bi.adjusted.json`; complete fitted coefficients, covariance and standardization inputs: corresponding `.npz`.

## Figure inputs

The pooled 1999–2016 primary frequentist model gives OR 1.472262 (95% CI 1.151797–1.881889), p = 0.002271. Standardizing to the survey-weighted circumcised complete-case covariate distribution (n = 9,167) gives intact-reference probability 4.225805%, circumcised probability 6.079274%, and gap 1.853469 percentage points. Both figures use these same fitted coefficients and targets. They show point scenarios, without scenario confidence intervals.

[Coefficient export and hash verification](../src/frequentist/export.py) · [Figure checks](../validation/figures.py).

## Raw survey-weighted prevalence

These available-case descriptive prevalences use their own observed circumcision groups. They are not the counterfactual model-standardized figure probabilities.

| outcome | circ | n | events | prevalence | se | ci_low | ci_high | kish_n | design_df |
|---|---|---|---|---|---|---|---|---|---|
| msm_ever | 0 | 3812 | 136 | 0.0353715 | 0.00368416 | 0.0287671 | 0.0434245 | 2477.24 | 138 |
| msm_ever | 1 | 9173 | 527 | 0.0607328 | 0.00400798 | 0.0532749 | 0.0691584 | 6375.09 | 138 |

See [extension results](extension_results.md) for the retained sensitivity families.

## Pooled model sensitivities

| outcome | model | n | events | n_circ | n_uncirc | events_circ | events_uncirc | beta | se | odds_ratio | ci_low | ci_high | p_value | design_df | residual_df | parameters | max_abs_score | kish_n | formula |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| msm_ever | full | 12973 | 662 | 9167 | 3806 | 527 | 135 | 0.3868 | 0.123961 | 1.47226 | 1.1518 | 1.88189 | 0.00227122 | 138 | 118 | 21 | 3.6805e-12 | 8620.47 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born |
| msm_ever | exclude_1999_2000 | 11842 | 611 | 8405 | 3437 | 490 | 121 | 0.43915 | 0.133156 | 1.55139 | 1.1914 | 2.02016 | 0.00132971 | 124 | 105 | 20 | 6.3417e-12 | 7810.01 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born |
| msm_ever | original_2005_2016 | 9161 | 498 | 6463 | 2698 | 401 | 97 | 0.433921 | 0.142207 | 1.5433 | 1.16271 | 2.04847 | 0.00312505 | 94 | 77 | 18 | 3.8719e-12 | 5828.46 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born |
| msm_ever | direct_2009_2016 | 6261 | 336 | 4335 | 1926 | 266 | 70 | 0.35722 | 0.166584 | 1.42935 | 1.02253 | 1.99803 | 0.0370937 | 63 | 48 | 16 | 5.67268e-12 | 3794.63 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born |
| msm_ever | exclude_ambiguous_screen_zeros | 12609 | 662 | 8986 | 3623 | 527 | 135 | 0.381385 | 0.124272 | 1.46431 | 1.14487 | 1.87288 | 0.00266546 | 138 | 118 | 21 | 1.15435e-12 | 8407.61 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born |
| msm_ever | exclude_all_earlier_screen_zeros | 12407 | 662 | 8856 | 3551 | 527 | 135 | 0.383013 | 0.124538 | 1.4667 | 1.14613 | 1.87692 | 0.00261219 | 138 | 118 | 21 | 3.63964e-12 | 8265.42 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born |

## Pooled adjustment sequence

| outcome | model | n | events | n_circ | n_uncirc | events_circ | events_uncirc | beta | se | odds_ratio | ci_low | ci_high | p_value | design_df | residual_df | parameters | max_abs_score | kish_n | formula | sample |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| msm_ever | unadjusted | 12985 | 663 | 9173 | 3812 | 527 | 136 | 0.567219 | 0.120221 | 1.76336 | 1.39026 | 2.23658 | 5.80056e-06 | 138 | 137 | 2 | 5.38411e-12 | 8629.08 | msm_ever ~ circ | available |
| msm_ever | unadjusted | 12973 | 662 | 9167 | 3806 | 527 | 135 | 0.577221 | 0.120717 | 1.78108 | 1.40286 | 2.26128 | 4.43102e-06 | 138 | 137 | 2 | 4.40675e-13 | 8620.47 | msm_ever ~ circ | common_complete |
| msm_ever | age_cycle | 12985 | 663 | 9173 | 3812 | 527 | 136 | 0.571261 | 0.11932 | 1.7705 | 1.39815 | 2.24201 | 4.6151e-06 | 138 | 127 | 12 | 1.56325e-12 | 8629.08 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) | available |
| msm_ever | age_cycle | 12973 | 662 | 9167 | 3806 | 527 | 135 | 0.580936 | 0.119829 | 1.78771 | 1.41032 | 2.26609 | 3.57333e-06 | 138 | 127 | 12 | 1.60938e-12 | 8620.47 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) | common_complete |
| msm_ever | demographic | 12978 | 663 | 9168 | 3810 | 527 | 136 | 0.447629 | 0.127778 | 1.5646 | 1.21484 | 2.01505 | 0.000648541 | 138 | 119 | 20 | 4.28702e-12 | 8623.77 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) | available |
| msm_ever | demographic | 12973 | 662 | 9167 | 3806 | 527 | 135 | 0.459771 | 0.128514 | 1.58371 | 1.22789 | 2.04264 | 0.000502612 | 138 | 119 | 20 | 2.04298e-12 | 8620.47 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) | common_complete |
| msm_ever | full | 12973 | 662 | 9167 | 3806 | 527 | 135 | 0.3868 | 0.123961 | 1.47226 | 1.1518 | 1.88189 | 0.00227122 | 138 | 118 | 21 | 3.6805e-12 | 8620.47 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born | available |
| msm_ever | full | 12973 | 662 | 9167 | 3806 | 527 | 135 | 0.3868 | 0.123961 | 1.47226 | 1.1518 | 1.88189 | 0.00227122 | 138 | 118 | 21 | 3.6805e-12 | 8620.47 | msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born | common_complete |

[Questionnaire skip audit](pooled_analysis.md)
