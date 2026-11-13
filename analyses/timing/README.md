# Circumcision timing and two illustrative endpoints

This package documents the external evidence, assumptions and calculations used to ask whether the observed association could be confined to men circumcised in infancy or to men circumcised in adulthood. It keeps those two endpoints prominent while retaining the mixed scenarios for inspection.

**No precise infant share was identified for the NHANES participants.** Infant shares of 80%, 90% and 95%, and adult shares of 3%, 5% and 10%, are specified scenarios. The sources inform their interpretation and a separate adult-procedure-count benchmark. They do not turn those shares into measured facts.

## Start here

| Document | What it establishes |
|---|---|
| [Endpoint results](results.md) | Required behavioral prevalence relative to a matched baseline, and required OR, under each endpoint |
| [Methods](methods.md) | Denominators, mixture equations, adjustment, feasibility, uncertainty and distinctions between parameterizations |
| [Source register](sources.md) | All 14 audited sources, access levels, scope, quantitative use and reasons for exclusion |
| [Numerical extraction](source_values.json) | Source-linked values used by the code, with assumptions kept in a separate field |
| [Reporting guide](reporting.md) | Suggested wording for the paper and the boundaries of each interpretation |
| [Bibliography](references.bib) | Reusable references for the central sources |
| [Original execution addendum](extraction_addendum.txt) | Historical record of the choices made before the first timing calculations |

## Reproduce and verify

First run the shared repository pipeline to obtain verified NHANES inputs and the fitted headline Bayesian model. Then run the timing package.

```sh
python scripts/reproduce.py
python -m analyses.timing.reproduce
python -m analyses.timing.reproduce --check
```

The package generates the original timing models if needed, produces the endpoint tables from the existing fits, and verifies the source register, stock arithmetic, mixture reconstruction and agreement with the earlier endpoint estimates. All numerical files remain local under `outputs/timing/`. `package_validation.json` records checks and input hashes.

To rerun all original grids, mixed scenarios and synthetic-allocation checks as well, use

```sh
python -m analyses.timing.reproduce --full
```

The directly calibrated Bayesian endpoint table matches the main repository's inference method. Its minimum-budget interval propagates the existing weighted posterior draws. The original Gaussian-summary endpoints remain alongside it, with their U.S.-born restriction. Full historical grids and allocation analyses retain the original specification and are labeled accordingly. No manuscript is modified by these commands.

## Trace a result to its calculation

- [source_values.json](source_values.json) supplies the extracted newborn percentages and 1996 age-band procedure counts to [run_timing.py](run_timing.py).
- [endpoint()](endpoints.py) solves the infant-only or adult-only mixture, checks the fraction budget, and calculates a baseline standardized to the same constructed component.
- [main() in endpoints.py](endpoints.py) applies that calculation to the saved model coefficients, propagates posterior uncertainty in the minimum budget and generates [results.md](results.md).
- [run_allocation.py](run_allocation.py) implements the separate synthetic before 18/18+ sensitivity with survey replicates. Those categories do not isolate infancy.
- [run_conditional.py](run_conditional.py) preserves the original constant-fraction and mixed-component uncertainty calculations. Those are distinct from the common-OR endpoint table.

The annual-count benchmark is not a hard adult upper bound. The endpoint table does not estimate timing or causality. In particular, a model assigning all excess prevalence to infancy cannot independently establish that infancy produced the excess.
