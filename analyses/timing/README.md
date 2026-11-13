# Circumcision timing sensitivity

These conditional association scenarios do not measure age at surgery or identify an infant causal effect. They retain the original Gaussian-summary Bayesian model; they have not been silently relabeled as results from the new direct implementation.

After reproducing NHANES, run:

```sh
python -m analyses.timing.run_timing
python -m analyses.timing.run_allocation
python -m analyses.timing.run_conditional
```

Outputs are generated under `outputs/timing/`. The [frozen extraction and implementation assumptions](extraction_addendum.txt) distinguish infant, childhood and adult timing, preserve infeasible scenarios, and explain the source-derived count benchmark. The simplex files are marginal feasibility screens, not certified covariate-level bounds. Missing model files must be explained by the failure log, not interpreted as null findings.

The historical counts are from [NHDS/NSAS 1996, Table 11, printed page 74](https://www.cdc.gov/nchs/data/series/sr_13/sr13_139.pdf). The [CDC newborn series](https://www.cdc.gov/nchs/data/hestat/circumcision_2013/circumcision_2013.htm) omits postdischarge procedures and begins in 1979. Neither source establishes a complete historical age-at-circumcision distribution or an all-setting adult upper bound. See [methods](../../docs/methods.md).
