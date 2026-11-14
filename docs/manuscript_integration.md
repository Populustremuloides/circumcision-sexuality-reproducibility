# Manuscript integration notes

The manuscript was not edited. Use the following frequentist descriptions and values when revising it.

The unchanged primary frequentist model gives OR 1.543297 (95% CI 1.162706–2.048467), p = 0.003125. Standardizing to the survey-weighted circumcised complete-case covariate distribution (n = 6,463) gives intact-reference probability 4.448015%, circumcised probability 6.680342%, and gap 2.232327 percentage points. Both figures use these same fitted coefficients and targets. They show point scenarios, without scenario confidence intervals.

## Methods wording

Survey-weighted logistic models used the existing NHANES examination weights, strata, PSUs and domain variance estimation, with two-sided t inference using residual design degrees of freedom. Figure inputs were calculated from the complete fitted coefficient vector of the primary model, standardized over the survey-weighted covariate distribution of circumcised complete cases. Sensitivity figures depict compatible point scenarios, not fitted timing-specific effects or uncertainty distributions.

## Timing caption

Compatible associations by assumed circumcision timing. Panel A shows component-weighted adjusted probabilities of lifetime male–male sexual behavior; panel B shows common conditional odds ratios relative to intact men. Curves fix the assumed adult share of circumcised men while allowing timing fractions to vary with covariates. Colors partition the modeled excess between timing components. Before age 18 includes infancy, childhood and adolescence. The starred 1.5% assumption extrapolates historical U.S. procedure counts (Owings and Kozak, 1998, Table 11); it is not an observed lifetime share or upper bound. Both component odds ratios are constrained to be at least one in the displayed region.

Adult-only feasibility threshold: 2.351725% of circumcised men, at a component outcome probability of 100%. See the endpoint table below for explicit infant-only scenarios; do not label the before-18 figure component as infant circumcision.

| Scenario | Assumed share (%) | Component baseline (%) | Required prevalence (%) | Prevalence ratio | Common conditional OR |
|---|---|---|---|---|---|
| adult_only | 3 | 4.93784 | 79.3487 | 16.0695 | 82.8357 |
| adult_only | 5 | 4.73585 | 49.3824 | 10.4274 | 21.0327 |
| adult_only | 10 | 4.58436 | 26.9076 | 5.86944 | 7.93647 |
| infant_only | 95 | 4.44881 | 6.79863 | 1.52819 | 1.57262 |
| infant_only | 90 | 4.4497 | 6.93006 | 1.55742 | 1.60528 |
| infant_only | 80 | 4.4518 | 7.24221 | 1.6268 | 1.68324 |

## Confounding caption

Hypothetical binary confounding sufficient to reconstruct the standardized association. Axes show characteristic prevalence in intact and circumcised men; colored bands show the required outcome-probability difference between those with and without the characteristic. Gray regions are infeasible under common component outcome probabilities and no residual circumcision association. This is a specified binary-mixture illustration, not a bound on every possible confounding structure.

The lowest band begins at the standardized gap, 2.23 percentage points.

## Descriptive prevalence

Raw survey-weighted prevalences are reproduced in [results](results.md#raw-survey-weighted-prevalence). They refer to observed groups and differ from the common-target standardized probabilities above.
