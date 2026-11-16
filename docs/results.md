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

| model | n | events | odds_ratio | ci_low | ci_high | p_value |
|---|---|---|---|---|---|---|
| full | 12973 | 662 | 1.47226 | 1.1518 | 1.88189 | 0.00227122 |
| exclude_1999_2000 | 11842 | 611 | 1.55139 | 1.1914 | 2.02016 | 0.00132971 |
| original_2005_2016 | 9161 | 498 | 1.5433 | 1.16271 | 2.04847 | 0.00312505 |
| direct_2009_2016 | 6261 | 336 | 1.42935 | 1.02253 | 1.99803 | 0.0370937 |
| exclude_ambiguous_screen_zeros | 12609 | 662 | 1.46431 | 1.14487 | 1.87288 | 0.00266546 |
| exclude_all_earlier_screen_zeros | 12407 | 662 | 1.4667 | 1.14613 | 1.87692 | 0.00261219 |

## Pooled adjustment sequence

| model | sample | n | odds_ratio | ci_low | ci_high | p_value |
|---|---|---|---|---|---|---|
| unadjusted | available | 12985 | 1.76336 | 1.39026 | 2.23658 | 5.80056e-06 |
| unadjusted | common_complete | 12973 | 1.78108 | 1.40286 | 2.26128 | 4.43102e-06 |
| age_cycle | available | 12985 | 1.7705 | 1.39815 | 2.24201 | 4.6151e-06 |
| age_cycle | common_complete | 12973 | 1.78771 | 1.41032 | 2.26609 | 3.57333e-06 |
| demographic | available | 12978 | 1.5646 | 1.21484 | 2.01505 | 0.000648541 |
| demographic | common_complete | 12973 | 1.58371 | 1.22789 | 2.04264 | 0.000502612 |
| full | available | 12973 | 1.47226 | 1.1518 | 1.88189 | 0.00227122 |
| full | common_complete | 12973 | 1.47226 | 1.1518 | 1.88189 | 0.00227122 |

[Questionnaire skip audit](pooled_analysis.md)

## Exploratory temporal interaction tests

| period | test | n | events | beta | se | ratio_OR_per_decade | low | high | statistic | df1 | df2 | p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| direct_2009_2016 | linear_trend | 6261 | 336 | 0.936101 | 0.662522 | 2.55002 | 0.672522 | 9.66898 | 1.41294 | 1 | 47 | 0.164263 |
| direct_2009_2016 | categorical_heterogeneity | 6261 | 336 | unavailable | unavailable | unavailable | unavailable | unavailable | 1.49923 | 3 | 45 | 0.227614 |
| harmonized_2001_2016 | linear_trend | 11842 | 611 | 0.161693 | 0.257848 | 1.1755 | 0.704949 | 1.96014 | 0.627085 | 1 | 104 | 0.531978 |
| harmonized_2001_2016 | categorical_heterogeneity | 11842 | 611 | unavailable | unavailable | unavailable | unavailable | unavailable | 0.660214 | 7 | 98 | 0.705044 |
| harmonized_1999_2016 | linear_trend | 12973 | 662 | 0.246178 | 0.21906 | 1.27913 | 0.828898 | 1.97391 | 1.12379 | 1 | 117 | 0.263401 |
| harmonized_1999_2016 | categorical_heterogeneity | 12973 | 662 | unavailable | unavailable | unavailable | unavailable | unavailable | 0.717509 | 8 | 110 | 0.675643 |
| partner_history_2001_2008 | linear_trend | 5581 | 275 | -0.243772 | 0.819459 | 0.783666 | 0.150432 | 4.08247 | -0.297479 | 1 | 45 | 0.76747 |
| partner_history_2001_2008 | categorical_heterogeneity | 5581 | 275 | unavailable | unavailable | unavailable | unavailable | unavailable | 0.034655 | 3 | 43 | 0.991226 |

[Plan](../analyses/nhanes/time_trend_plan.md) · [Code](../analyses/nhanes/time_trend.py). Direct-question 2009–2016 is the main comparability test. Longer windows mix question regimes. No clear trend was established; these are nominal exploratory tests, not evidence of temporal equivalence.
