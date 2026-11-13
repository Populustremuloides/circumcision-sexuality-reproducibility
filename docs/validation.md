# Validation and practical limits

The headline behavior conclusion was stable across the original Gaussian approximation, the full logistic pseudo-posterior with survey calibration, and a curvature-adjusted logistic likelihood. Identity intervals continued to include 1; gay-only directional probabilities varied by implementation. Full results are generated in `outputs/validation/bayesian/`.

The documented comparison used 131,072 independent importance proposals per target. Numerical checks cover gradients, curvature transformations, effective sample size, maximum importance weight, independent-batch stability, and a known Normal target. These are not MCMC chains; chain R-hat does not apply.

Across 4,000 targeted simulations using the actual outcome-specific covariates and survey structure, the proper-prior fit with posterior-based calibration completed all 4,000. MLE-dependent approaches failed in 576, including 566 gay-only cases with sparse education categories. One actual-data gay-only delete-PSU replicate also failed; its variance was not calculated by silently dropping that replicate. For behavior, gay/bisexual and bisexual outcomes, delete-PSU standard errors differed from Taylor estimates by less than 0.4%.

Behavioral 95% interval coverage in non-null simulations was approximately90–92% for both approaches. Fixed-truth coverage of a proper-prior credible interval need not equal95%, and simulation Monte Carlo error is material, but these checks do not establish universally calibrated intervals or probabilities. Simulation alternatives use a Laplace approximation; actual-data headline estimates use full importance integration. The simulations condition on the observed design/covariates, rather than reproducing every aspect of population sampling.

## Re-run checks

```sh
python scripts/reproduce.py --validation
python -m validation.simulations.informative_sampling
python -m scripts.build_results --check
```

The second command runs the earlier complementary 8,000-repetition informative-sampling experiment. R survey verification is available via `--r-check`. The matched-headline release checks verify sample sizes, events, formulas, input hashes, numerical integration, and agreement with frozen validated estimates. Neither a code check nor agreement between estimators is independent replication or evidence excluding confounding. No independent human statistical review is claimed.
