# Circumcision and sexual behavior: reproducible analyses

Code for NHANES 2005–2016 and the separate Maloney regret/self-concept supplement. Each headline question has a shared sample and model specification, separate frequentist and Bayesian estimators, and a runnable analysis ID.

These observational, exploratory associations are not causal effects. The Bayesian reanalysis followed examination of the frequentist results. The repository excludes source data, generated datasets, model-output files and manuscript files; the concise documentation tables below are generated from validated local runs. No cross-study meta-analysis is included.

## Headline questions: side-by-side results

<!-- RESULTS -->

Frequentist intervals use the survey-design t reference. Bayesian results use a direct, proper-prior weighted logistic pseudo-posterior with uncertainty calibrated for strata and PSUs at the posterior mean. They are not the earlier Gaussian-summary approximation, which remains available as a sensitivity analysis. Directional probabilities concern adjusted associations under the stated model and priors, not causation. See [each question and its runnable command](docs/results.md), [extension and Maloney comparisons](docs/extension_results.md), [methods](docs/methods.md), and [validation findings](docs/validation.md).

## Reproduce

Python 3.10 or 3.11 and Git are required. From the repository root:

```sh
git clone https://github.com/Populustremuloides/circumcision-sexuality-reproducibility.git
cd circumcision-sexuality-reproducibility
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/reproduce.py
```

On Windows, activate with `.venv\Scripts\activate`. Initial downloads require internet access. The runner verifies 25 pinned public source files, harmonizes records, runs frequentist analyses and their numerical checks, fits the Bayesian headline models and approximation sensitivities, runs both Maloney implementations, verifies the paired results, and generates this comparison. Allow several minutes; extensive validation takes longer. Data, outputs and draws remain local in ignored directories. A failure stops the pipeline and is recorded in `outputs/run.json` with logs under `outputs/logs/`.

```sh
python scripts/reproduce.py --offline                 # verified cached sources
python scripts/reproduce.py --nhanes-only             # omit Maloney
python scripts/reproduce.py --frequentist-only        # original analyses only
python scripts/reproduce.py --validation              # alternative implementations + 4,000 targeted simulations
python -m analyses.nhanes.run --analysis nhanes.identity_gay.adjusted
python -m scripts.build_results --check               # detect stale comparison text
```

The single-question command requires the harmonized data from the full runner. Add `--method frequentist` or `--method bayesian` to run one estimator. Bayesian numerical integration uses four independent importance-sampling batches; no MCMC installation is required.

## Repository map

| Location | Purpose |
|---|---|
| [config/analyses.json](config/analyses.json) | Executable headline IDs, outcomes, formulas and shared adjustment sets |
| [src/data](src/data) | Source download, audits and NHANES harmonization |
| [src/survey](src/survey) | Shared design-based covariance and survey estimation |
| [src/frequentist](src/frequentist) | Frequentist NHANES, extensions and Maloney |
| [src/bayesian](src/bayesian) | Direct headline model, Gaussian/t sensitivities and direct Maloney integration |
| [analyses](analyses) | Question-level entry points and optional timing scenarios |
| [validation](validation) | Independent R checks, numerical comparisons and simulations |
| [docs/results.md](docs/results.md) | Result-to-code links and individual commands |

Outputs are separated into `outputs/frequentist/`, `outputs/bayesian/`, `outputs/validation/`, and optional `outputs/timing/`. Earlier script names remain as compatibility entry points; numerical implementations live in the directories above.

## Independent R verification

```sh
conda env create -f environment.yml
conda activate circumcision-reproduction
python scripts/reproduce.py --r-check
```

Alternatively install R and `survey` and put `Rscript` on PATH. The reference comparison checks eight core models on shared harmonized records; it is not an independent data extraction or validation of every extension. The reference versions are R 4.5.3 and survey 4.5. The manually triggered GitHub Actions workflow runs the standard pipeline without uploading data or generated outputs.

## Scope and transparency

The Maloney primary sample includes all 326 eligible men with the three required responses. The former 325-person exclusion is retained as an explicitly labeled sensitivity check. This sample is not pooled with NHANES.

Timing sensitivity scenarios retain the earlier Gaussian approximation and are not silently relabeled as direct-posterior results. They cannot identify the probability that infant circumcision caused the association. [Timing evidence and endpoint package](analyses/timing/README.md) contains the 14-source register, numerical extraction, derivations, generated endpoint tables and a reporting guide.

The release preserves the clean public-code history without importing exploratory development commits. Its [analytical history](docs/analytical_history.md) documents methodological development and limitations. Sparse gay-identity fits and imperfect simulation coverage are retained in the [validation report](docs/validation.md).
