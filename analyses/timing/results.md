# Timing endpoint results

The pooled 1999–2016 primary frequentist model gives OR 1.472262 (95% CI 1.151797–1.881889), p = 0.002271. Standardizing to the survey-weighted circumcised complete-case covariate distribution (n = 9,167) gives intact-reference probability 4.225805%, circumcised probability 6.079274%, and gap 1.853469 percentage points. Both figures use these same fitted coefficients and targets. They show point scenarios, without scenario confidence intervals.

The minimum adult share under the adult-only scenario is 1.950066%, attained only at 100% behavioral probability in that component. Smaller adult shares cannot account for the entire modeled gap under these assumptions.

| Scenario | Assumed share (%) | Component baseline (%) | Required prevalence (%) | Prevalence ratio | Common conditional OR |
|---|---|---|---|---|---|
| adult_only | 3 | 4.69378 | 66.4761 | 14.1626 | 45.103 |
| adult_only | 5 | 4.5008 | 41.5702 | 9.23617 | 16.1824 |
| adult_only | 10 | 4.35607 | 22.8908 | 5.25491 | 6.75225 |
| infant_only | 95 | 4.22657 | 6.17759 | 1.46161 | 1.49764 |
| infant_only | 90 | 4.22741 | 6.28682 | 1.48716 | 1.5259 |
| infant_only | 80 | 4.22942 | 6.54626 | 1.54779 | 1.59328 |

Infant-only rows are explicitly hypothetical infant shares; the displayed timing figure instead separates before age 18 from age 18 onward. When the association is assigned entirely to one component, the other component is held at the intact-reference probability conditional on covariates. Component-weighted baseline probabilities differ because the constructed timing fractions vary with covariates. No timing distribution is observed.

[Endpoint solver](endpoints.py) · [Methods](methods.md) · [Source audit](sources.md).

## Historical count extrapolations

These procedure stocks are assumption-driven scenarios, not estimates with sampling uncertainty. The 1.5% marker is a historical extrapolation, not a measured lifetime share or a hard upper limit. Complete grids are in `outputs/timing/count_envelopes.csv`.

| cycle | threshold | missing_multiplier | historical_multiplier | stock | circ_population | fraction | fraction_foreign_unresolved |
|---|---|---|---|---|---|---|---|
| 1999 | 18 | 1 | 1 | 853000 | 5.01977e+07 | 0.0169928 | 0.121739 |
| 2001 | 18 | 1 | 1 | 853000 | 5.9678e+07 | 0.0142934 | 0.0771844 |
| 2003 | 18 | 1 | 1 | 853000 | 5.55396e+07 | 0.0153584 | 0.107264 |
| 2005 | 18 | 1 | 1 | 853000 | 5.94712e+07 | 0.0143431 | 0.0968983 |
| 2007 | 18 | 1 | 1 | 853000 | 5.71239e+07 | 0.0149325 | 0.118671 |
| 2009 | 18 | 1 | 1 | 853000 | 5.7572e+07 | 0.0148162 | 0.140631 |
| 2011 | 18 | 1 | 1 | 853000 | 5.53504e+07 | 0.0154109 | 0.120424 |
| 2013 | 18 | 1 | 1 | 853000 | 5.71907e+07 | 0.014915 | 0.101736 |
| 2015 | 18 | 1 | 1 | 853000 | 5.59891e+07 | 0.0152351 | 0.120279 |
