# Results and reproducible questions

Generated from validated local result records. The two methods use identical participants and formulas for each headline question.



| Question | Frequentist OR (95% CI) | Bayesian OR (95% calibrated interval) | P(OR > 1) | Specification and code |
|---|---:|---:|---:|---|
| Lifetime male–male behavior | 1.54 (1.16–2.05) | 1.48 (1.14–1.95) | 99.9% | [specification](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/config/analyses.json#L10) · [frequentist](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/analyses/nhanes/run.py#L8) · [Bayesian](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/headline.py#L9) |
| Gay/bisexual versus heterosexual identity | 1.25 (0.85–1.84) | 1.22 (0.86–1.75) | 86.3% | [specification](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/config/analyses.json#L19) · [frequentist](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/analyses/nhanes/run.py#L8) · [Bayesian](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/headline.py#L9) |
| Gay versus heterosexual identity | 1.52 (0.95–2.42) | 1.40 (0.94–2.12) | 94.8% | [specification](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/config/analyses.json#L28) · [frequentist](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/analyses/nhanes/run.py#L8) · [Bayesian](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/headline.py#L9) |
| Bisexual versus heterosexual identity | 0.94 (0.49–1.79) | 0.94 (0.54–1.70) | 42.1% | [specification](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/config/analyses.json#L37) · [frequentist](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/analyses/nhanes/run.py#L8) · [Bayesian](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/headline.py#L9) |

## Lifetime male–male behavior

Analysis ID: `nhanes.msm_ever.adjusted`. N = 9,161; events = 498.

```sh
python -m analyses.nhanes.run --analysis nhanes.msm_ever.adjusted
```

Formula: `msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[specification](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/config/analyses.json#L10) · [frequentist](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/analyses/nhanes/run.py#L8) · [Bayesian](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/headline.py#L9). The survey estimator is implemented in [Survey.model](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/survey/design.py#L53); the Bayesian likelihood and numerical integration are in [logistic.py](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/logistic.py#L57).

The command writes matching JSON result records to `outputs/frequentist/headline/nhanes.msm_ever.adjusted.json` and `outputs/bayesian/headline/nhanes.msm_ever.adjusted.json`. Records include the input/specification hashes, code hash, Git commit, sample size and uncertainty.



## Gay/bisexual versus heterosexual identity

Analysis ID: `nhanes.identity_gb.adjusted`. N = 8,962; events = 333.

```sh
python -m analyses.nhanes.run --analysis nhanes.identity_gb.adjusted
```

Formula: `identity_gb ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[specification](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/config/analyses.json#L19) · [frequentist](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/analyses/nhanes/run.py#L8) · [Bayesian](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/headline.py#L9). The survey estimator is implemented in [Survey.model](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/survey/design.py#L53); the Bayesian likelihood and numerical integration are in [logistic.py](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/logistic.py#L57).

The command writes matching JSON result records to `outputs/frequentist/headline/nhanes.identity_gb.adjusted.json` and `outputs/bayesian/headline/nhanes.identity_gb.adjusted.json`. Records include the input/specification hashes, code hash, Git commit, sample size and uncertainty.



## Gay versus heterosexual identity

Analysis ID: `nhanes.identity_gay.adjusted`. N = 8,825; events = 196.

```sh
python -m analyses.nhanes.run --analysis nhanes.identity_gay.adjusted
```

Formula: `identity_gay ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[specification](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/config/analyses.json#L28) · [frequentist](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/analyses/nhanes/run.py#L8) · [Bayesian](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/headline.py#L9). The survey estimator is implemented in [Survey.model](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/survey/design.py#L53); the Bayesian likelihood and numerical integration are in [logistic.py](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/logistic.py#L57).

The command writes matching JSON result records to `outputs/frequentist/headline/nhanes.identity_gay.adjusted.json` and `outputs/bayesian/headline/nhanes.identity_gay.adjusted.json`. Records include the input/specification hashes, code hash, Git commit, sample size and uncertainty.



## Bisexual versus heterosexual identity

Analysis ID: `nhanes.identity_bi.adjusted`. N = 8,766; events = 137.

```sh
python -m analyses.nhanes.run --analysis nhanes.identity_bi.adjusted
```

Formula: `identity_bi ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born`.

[specification](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/config/analyses.json#L37) · [frequentist](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/analyses/nhanes/run.py#L8) · [Bayesian](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/headline.py#L9). The survey estimator is implemented in [Survey.model](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/survey/design.py#L53); the Bayesian likelihood and numerical integration are in [logistic.py](https://github.com/Populustremuloides/circumcision-sexuality-reproducibility/blob/ec2405ca423fc6518324ffe09a2cc89674457c45/src/bayesian/logistic.py#L57).

The command writes matching JSON result records to `outputs/frequentist/headline/nhanes.identity_bi.adjusted.json` and `outputs/bayesian/headline/nhanes.identity_bi.adjusted.json`. Records include the input/specification hashes, code hash, Git commit, sample size and uncertainty.



## Other questions

| Question family | Frequentist implementation | Bayesian implementation | Scope |

|---|---|---|---|

| Specific anal/oral behaviors | [behavior.py](../src/frequentist/behavior.py) | [approximation.py](../src/bayesian/approximation.py) | Gaussian/t approximation; not the directly fitted headline method |

| Within-identity associations and interactions | [identity.py](../src/frequentist/identity.py) | [approximation.py](../src/bayesian/approximation.py) | Interaction conclusions remain sensitive to nuisance priors |

| Explanatory contrasts | [explanations.py](../src/frequentist/explanations.py) | [approximation.py](../src/bayesian/approximation.py) | Some estimands are differences, not odds ratios; failed fits retained |

| Maloney regret and self-concept | [maloney.py](../src/frequentist/maloney.py) | [maloney.py](../src/bayesian/maloney.py) | Separate unweighted sample; primary326 and sensitivity325 |

| Later circumcision scenarios | [allocation fits](../analyses/timing/run_allocation.py) | [mixture scenarios](../analyses/timing/run_timing.py) | Conditional assumptions, not observed timing or infant causal effects |



Run all standard questions with `python scripts/reproduce.py`; add `--validation` for the full-likelihood comparisons and targeted simulations. Timing scenarios are separate opt-in commands documented [here](../analyses/timing/README.md). Full extension tables remain generated locally. No incompatible estimands are presented as interchangeable method comparisons.

## Detailed extension comparisons

See [the generated extension results](extension_results.md) for behavior, identity subgroup/interaction and Maloney comparisons.
