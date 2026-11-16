# Historical earlier-period analysis

The fixed specification was committed as af1e2a0 before estimating associations. This historical subset now overlaps the pooled 1999–2016 primary analysis and is not independent confirmation.

| model | n | events | odds_ratio | ci_low | ci_high | p_value |
|---|---|---|---|---|---|---|
| unadjusted | 3816 | 165 | 1.52597 | 0.963523 | 2.41674 | 0.0706495 |
| adjusted | 3812 | 164 | 1.35315 | 0.813345 | 2.25121 | 0.234451 |
| exclude_1999_2000 | 2681 | 113 | 1.63607 | 0.805908 | 3.32136 | 0.160671 |

Both adjusted point estimates are positive but imprecise; their intervals include one and the original-period estimate. This does not establish replication or equivalence. The unadjusted association uses its own available cases. The predetermined exclusion of 1999–2000 addresses a wording difference. Sources, weights, routing and missingness are specified in [the fixed plan](../analyses/replication/specification.md). Run `python -m analyses.replication.run --estimate` and optionally `Rscript analyses/replication/verify.R`.
