# Methods for the two timing endpoints

## Question and interpretation

The analysis asks how the observed association could be distributed across circumcisions performed in infancy, childhood and adulthood. NHANES measures current circumcision status but does not identify these timing groups. We therefore calculate two illustrative endpoints. One assigns the entire conditional association to adult-circumcised men, and the other assigns it to infant-circumcised men. Both are restrictions on unobserved subgroup associations. They do not identify which explanation is true.

The fractions in the endpoint tables are assumptions. The source audit did not establish that 80%, 90% or 95% of the circumcised participants underwent surgery in infancy. In particular, a high proportion of infant procedures in a contemporary claims dataset cannot be substituted for a lifetime timing distribution among the adults sampled by NHANES. The [source register](sources.md) explains this distinction for each study.

## Population, outcome and baseline

The principal outcome is reported lifetime male–male sexual behavior among the original eligible NHANES 2005–2016 male participants aged 20–59. The primary all-men model has 9,161 complete cases and 498 events. The common adjustment set includes linear and quadratic age, survey cycle, race/ethnicity, education and nativity. Survey weights, strata and PSUs remain those of the main analysis.

For timing calculations, standardization uses the empirical covariate distribution of currently circumcised complete cases. All infant and adult shares therefore have **circumcised men** as their denominator. This differs from the full-sample target distribution used in some earlier prevalence summaries. Weighted complete-case totals describe the represented domain, not a new nonresponse-adjusted population estimate.

Let X denote the measured covariates, p_U(X) the modeled prevalence if current status is uncircumcised and p_C(X) the modeled prevalence if current status is circumcised. These are adjusted associational predictions. Their contrast is not automatically a causal intervention effect. The endpoint presentation uses the posterior coefficient mean to obtain these probabilities. A probability evaluated at the coefficient mean need not equal the median of probabilities evaluated across posterior draws.

The generated endpoint tables now include the direct calibrated Bayesian implementation used in the repository's headline results. They also reproduce the original Gaussian-summary calculation and its U.S.-born restriction. The older full timing grids and allocation analyses retain their original Gaussian-summary specification. Model labels identify these versions throughout.

## Three timing components

Define I as surgery before age 1, K as surgery at ages 1–17 and A as surgery at age 18 or later. Let f_I(X), f_K(X) and f_A(X) be their shares among circumcised men at each covariate pattern. Then

\[
p_C(X)=f_I(X)p_I(X)+f_K(X)p_K(X)+f_A(X)p_A(X),\qquad
f_I(X)+f_K(X)+f_A(X)=1.
\]

A procedure before adulthood is not necessarily an infant procedure. To interpret the residual association specifically as an infancy association, the childhood component must also be assigned an association or restricted to baseline.

## Endpoint assigning the association to adulthood

Impose p_I(X)=p_K(X)=p_U(X). For a specified positive adult fraction,

\[
p_A(X)=p_U(X)+\frac{p_C(X)-p_U(X)}{f_A(X)}.
\]

The required probability must lie between 0 and 1. For a positive gap, the smallest feasible adult fraction at X is

\[
f_{A,\min}(X)=\frac{p_C(X)-p_U(X)}{1-p_U(X)}.
\]

At this limit every adult-circumcised man has the outcome. With covariate-varying fractions, the minimum total budget is the survey-weighted mean of these local minima over circumcised complete cases. It is a bound within the fitted mixture assumptions, not a bound covering arbitrary unmeasured confounding or every alternative regression model.

If only a fraction v of adult procedures can contribute to the proposed selection mechanism, replace f_A by v f_A. Allowing v=1 includes every adult indication. Medical or routine/ritual codes do not establish sexual motivation, voluntary choice or whether behavior preceded surgery.

## Endpoint assigning the association to infancy

Impose p_K(X)=p_A(X)=p_U(X). Then

\[
p_I(X)=p_U(X)+\frac{p_C(X)-p_U(X)}{f_I(X)}.
\]

This assigns all excess prevalence to the infant component. When f_I is below 1, the required infant prevalence difference is larger than the current-status difference. If only adulthood is restricted to baseline, the remaining component is **preadult circumcision**, which includes childhood. It must not be relabeled infancy.

A study finding no behavioral change after adult surgery does not establish the stronger restriction p_A(X)=p_U(X). Men receiving adult procedures could already differ in behavior before surgery. This distinction determines how the endpoint may be discussed alongside adult intervention studies.

## How the displayed odds ratios and prevalences are calculated

The short tables use one common adjusted component odds ratio R, with covariate-varying component fractions. For component G, either I or A, define

\[
p_G(X;R)=\operatorname{expit}\{\operatorname{logit}(p_U(X))+\log R\},\qquad
f_G(X;R)=\frac{p_C(X)-p_U(X)}{p_G(X;R)-p_U(X)}.
\]

For each assumed total share f, numerical root finding chooses R such that the weighted mean of f_G(X;R) is f. The program checks that every fraction is admissible and reconstructs p_C(X) from the mixture. It does not obtain R by dividing an adjusted OR by a fraction. Odds ratios do not mix linearly.

Within the constructed component, weights are proportional to the original circumcised weights multiplied by f_G(X;R). Both the required behavioral prevalence and its comparison baseline are averaged with those same component weights. Their ratio is a prevalence ratio. It is distinct from the common conditional odds ratio R. This matching avoids comparing a selected component's prevalence with an unrelated unadjusted baseline.

The full timing grid also contains a different construction that holds the component fraction constant across covariates and calculates varying component probabilities. Those results are retained separately in `constant_fraction.csv`. Their marginal ORs and intervals should not be combined with the common-OR construction as if they were the same estimand.

## External procedure-count benchmark

Source S07 reports approximately 15,000 procedures at ages 15–44 and 13,000 at ages 45–64 in 1996, combining inpatient and ambulatory settings. The [extraction record](source_values.json) preserves the published age bands, units, source location and rounding. It does not relabel the 15–44 category as an observed adult-only count.

For a deliberately permissive adult-stock scenario, allocate an entire age-band count to adult procedures whenever that band contains an adult age compatible with the interview-age range. Retain all procedures without mortality or emigration discounts, count interview year as a full year, and extrapolate the 1996 annual counts over compatible prior years. Allowing integer current ages 20–60 conservatively accommodates age rounding at the upper edge. Each year's disjoint age-band budget is used only once within the national stock.

This yields 43 compatible calendar years for the younger band and 16 for the older band, or 43×15,000+16×13,000=853,000 procedures. Each NHANES cycle represents an overlapping population, so stocks are averaged across cycles rather than summed as six disjoint groups. Assigning the entire national count to the complete-case domain is itself a generous allocation.

These are survey point estimates with incomplete settings and uncertain historical transport. No age-cell covariance was extracted, and no confidence upper limit was constructed. Setting multipliers of 1,2,5 and 10 and historical multipliers of 0.5,1,2 and 5 are assumption-based sensitivity factors. They are not probabilities or evidence-supported hard limits. Procedures abroad remain unresolved, including among U.S.-born men.

Source S01 supplies birth-hospitalization rates for 1979 onward, covering only some participants' birth cohorts and omitting later infant procedures. Its extracted percentages are retained for transparency but are not used to estimate the assumed infant shares. Sources S03–S06 inform interpretation of age patterns and coverage, without supplying an independent historical timing prior.

## Uncertainty and reproducibility

For the direct calibrated Bayesian model, the endpoint program propagates all 131,072 existing importance proposals with their posterior weights through the minimum-budget formula. It retains draws that have no positive excess as a zero minimum positive budget, rather than discarding them. It reports the resulting weighted interval separately from the illustrative component-OR point calculations. External count uncertainty and timing shares are not integrated using an invented probability distribution.

The original Gaussian-summary analysis propagates 4,000 coefficient draws and records infeasible scenarios without silently renormalizing their posterior mass. Detailed constant-fraction and mixed scenarios are available separately. The complementing synthetic allocation analysis retains original respondents/PSUs and recalibrates assignments inside selected jackknife replicates. It is not a certified global worst-case optimization under all historical cohort budgets.

The [endpoint generator](endpoints.py) checks the mixture identities, weighted fraction targets and agreement with the previous Gaussian endpoint results. It records hashes of the fitted draws, data, source register, numerical extraction and generator. The [one-command runner](reproduce.py) checks source-derived inputs and produces a validation record. Model failures remain visible. Neither endpoint estimates the probability that infant circumcision caused the association.
