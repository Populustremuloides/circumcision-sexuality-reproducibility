# Timing endpoint results

The unchanged primary frequentist model gives OR 1.543297 (95% CI 1.162706–2.048467), p = 0.003125. Standardizing to the survey-weighted circumcised complete-case covariate distribution (n = 6,463) gives intact-reference probability 4.448015%, circumcised probability 6.680342%, and gap 2.232327 percentage points. Both figures use these same fitted coefficients and targets. They show point scenarios, without scenario confidence intervals.

The minimum adult share under the adult-only scenario is 2.351725%, attained only at 100% behavioral probability in that component. Smaller adult shares cannot account for the entire modeled gap under these assumptions.

| Scenario | Assumed share (%) | Component baseline (%) | Required prevalence (%) | Prevalence ratio | Common conditional OR |
|---|---|---|---|---|---|
| adult_only | 3 | 4.93784 | 79.3487 | 16.0695 | 82.8357 |
| adult_only | 5 | 4.73585 | 49.3824 | 10.4274 | 21.0327 |
| adult_only | 10 | 4.58436 | 26.9076 | 5.86944 | 7.93647 |
| infant_only | 95 | 4.44881 | 6.79863 | 1.52819 | 1.57262 |
| infant_only | 90 | 4.4497 | 6.93006 | 1.55742 | 1.60528 |
| infant_only | 80 | 4.4518 | 7.24221 | 1.6268 | 1.68324 |

Infant-only rows are explicitly hypothetical infant shares; the displayed timing figure instead separates before age 18 from age 18 onward. When the association is assigned entirely to one component, the other component is held at the intact-reference probability conditional on covariates. Component-weighted baseline probabilities differ because the constructed timing fractions vary with covariates. No timing distribution is observed.

[Endpoint solver](endpoints.py) · [Methods](methods.md) · [Source audit](sources.md).

## Historical count extrapolations

These procedure stocks are assumption-driven scenarios, not estimates with sampling uncertainty. The 1.5% marker is a historical extrapolation, not a measured lifetime share or a hard upper limit. Complete grids are in `outputs/timing/count_envelopes.csv`.

| cycle | threshold | missing_multiplier | historical_multiplier | stock | circ_population | fraction | fraction_foreign_unresolved |
|---|---|---|---|---|---|---|---|
| 2005 | 18 | 1 | 1 | 853000 | 5.94712e+07 | 0.0143431 | 0.0968983 |
| 2007 | 18 | 1 | 1 | 853000 | 5.71239e+07 | 0.0149325 | 0.118671 |
| 2009 | 18 | 1 | 1 | 853000 | 5.7572e+07 | 0.0148162 | 0.140631 |
| 2011 | 18 | 1 | 1 | 853000 | 5.53504e+07 | 0.0154109 | 0.120424 |
| 2013 | 18 | 1 | 1 | 853000 | 5.71907e+07 | 0.014915 | 0.101736 |
| 2015 | 18 | 1 | 1 | 853000 | 5.59891e+07 | 0.0152351 | 0.120279 |
