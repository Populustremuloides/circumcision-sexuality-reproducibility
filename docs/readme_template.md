# Circumcision status and reported male–male sexual behavior

## Research question

Is circumcision status associated with reported lifetime male–male sexual behavior in U.S. men? This repository reproduces an exploratory observational analysis. It does not establish a causal or developmental mechanism.

## Dataset and eligible population

NHANES 2005–2016, six two-year cycles; respondents recorded as male, ages 20–59, with positive examination weights. Each model uses its required complete cases. Public source files are downloaded and checksum-verified.

## Outcome, exposure and covariates

The primary outcome is reported lifetime male–male sexual behavior, harmonized across questionnaire changes. Exposure is self-reported circumcision, with intact men as reference. Adjustment includes linear and quadratic age, survey cycle, race/ethnicity, education and nativity. Survey-weighted logistic regression uses Taylor-linearized standard errors and finite design degrees of freedom, preserving examination weights, strata, PSUs and domain estimation. [Methods](docs/methods.md) · [Executable specifications](config/analyses.json).

## Primary frequentist estimate

<!-- RESULTS -->

Intervals are 95% confidence intervals; primary p-values are nominal and two-sided. Identity is distinct from behavior. [Result-to-code guide](docs/results.md).

## Sensitivity analyses

Retained analyses cover alternate populations and periods, income and age specifications, specific sexual practices, identity-defined subgroups and explanatory contrasts. Their original multiplicity corrections and failed-model records are preserved. [Results and code](docs/extension_results.md).

## Figures and assumptions

[View/download the two selected figures](figures/README.md): timing mixtures and hypothetical binary confounding. Both use the same model-standardized probabilities over circumcised complete cases. These are point scenarios with assumed shares, not observed timing-specific effects or probabilities that a mechanism is true. The [timing source audit](analyses/timing/sources.md) and [methods](analyses/timing/methods.md) distinguish historical counts from assumptions. The before-18 figure component is not infant-specific.

## Reproduction

Python 3.10 or 3.11 is required. From a checkout of this repository:

```sh
python -m pip install -r requirements.txt
python scripts/reproduce.py
python -m analyses.figures.reproduce
python -m scripts.build_results --check
```

The first reproduction command downloads 24 NHANES source files, runs the retained models and validation, exports fitted coefficients, generates timing scenarios and both figures, and rebuilds numerical documentation. The separate figure command is also available for rerendering without refitting. Generated figures are under `outputs/selected_figures/`; committed publication copies are under `figures/`. Data and full model artifacts remain local and ignored by Git. Initial downloading requires internet access.

Use `python scripts/reproduce.py --offline` for verified cached inputs. The [optional Maloney supplement](docs/methods.md#separate-maloney-supplement) is preserved pending an editorial inclusion decision; add `--with-maloney` to download its additional source, run it and validate it. It is not pooled with NHANES. Add `--r-check` for independent R `survey` comparisons; R is not required for routine reproduction.

To rerun a single registered model after harmonization:

```sh
python -m analyses.nhanes.run --analysis nhanes.msm_ever.adjusted
```

## Validation and limitations

[Validation](docs/validation.md) covers coding, source hashes, samples, weights, domain variance, numerical stability, Taylor/jackknife consistency, frozen regression references, fitted-model exports and mixture reconstruction. [GitHub Actions](.github/workflows/reproduce.yml) runs the core workflow and optional R checks. Numerical agreement is not independent replication.

The broader analytical search was not preregistered; the primary p-value is nominal. [Analytical history](docs/analytical_history.md) records methodological development. Unmeasured childhood context, timing, geography, reporting and selection remain unresolved. Model-standardized associations do not identify causal effects. The manuscript itself is not included or modified by this pipeline.
