# Exploratory NHANES time-trend analysis
Specified 16 November 2026 before running new temporal interaction models. Earlier period and cycle-specific findings have already been examined; this is not preregistration.

Outcome: lifetime male–male sexual behavior, using the validated repository coding. Eligible respondents: men aged 20–59 with positive examination weights; outcome-specific complete cases. Circumcision self-report and adjustment set unchanged: age centered/scaled per decade, age squared, categorical survey cycle, five-category race/ethnicity, five-category education, and nativity.

Primary temporal test: 2009–2016, consistent direct SXQ809 behavior item. Add circ × (cycle start year − 2009)/10, retaining cycle main effects. Report ratio of circumcision ORs per decade with 95% t interval and two-sided nominal p-value. Per-decade scaling is a coefficient interpretation, not an observed decade-long follow-up.

Companion test: joint Wald F test of all circ × categorical-cycle interactions, allowing nonmonotonic changes; report adjusted cycle-specific ORs from this joint model with common adjustment slopes. No separate cycle-specific significance claims.

Secondary checks, reported in full: (1) 2001–2016 harmonized behavior, excludes documented 1999 wording issue; (2) 1999–2016 including that cycle; (3) 2001–2008 partner-history era alone. The longer series mixes question/routing regimes and cannot isolate period from measurement changes. The earlier-era question also changed in 2005/2007, so it is not exact wording equivalence. No search for cutpoints. No internet mechanism or age/cohort effect will be inferred from survey year.

Survey design: full positive-weight design with zero score contributions outside complete-case domains; cycle-nested public strata and PSUs; Taylor covariance and residual design df. For start>=2001, recover original WTMEC2YR and divide by number of cycles. For 1999–2016, WTMEC4YR*2/9 for 1999–2002, WTMEC2YR/9 subsequently. All subgroup/period comparisons use their own stated complete-case samples; within each period the trend and categorical models have identical observations.

Validation: existing validated Survey estimator including independent sandwich algebra check; independent R survey verification if available. Input and script hashes retained. All p-values exploratory and nominal, with main linear test distinguished from companion and sensitivity tests. No manuscript or public repo changes.

Sources: existing data coding and replication specification at repository commit 8ff1d6e01727de5bd743ea7cf0386755979f6430; CDC SXQ_E and SXQ_F codebooks (question/routing changes), plus archived cycle codebooks. This new pooled trend analysis extends the prior separate-period replication plan under the user's explicit request.
