# Circumcision and sexual behavior: reproducible analyses

Code to reproduce the NHANES 2005–2016 analyses of circumcision status and reported male–male sexual behavior, with a separate Maloney supplement examining regret, masculinity, and comfort with penile visibility among circumcised respondents.

This is a standalone code release. Public source files are downloaded when the pipeline runs; data, generated tables, figures, and manuscript files are not distributed here. The analyses are observational and exploratory. This consolidated specification is not a preregistration, and associations should not be interpreted as causal effects.

## Quick start

Install Python 3.10 or 3.11 and Git, then run:

```sh
git clone https://github.com/Populustremuloides/circumcision-sexuality-reproducibility.git
cd circumcision-sexuality-reproducibility
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/reproduce.py
```

On Windows, activate with `.venv\Scripts\activate` instead. An internet connection is required for installation and the initial source download. Allow several minutes for the survey replication calculations. Commands run from the repository root; the runner itself can also be invoked by absolute path.

The runner downloads and verifies 25 public source files, harmonizes variables, fits the NHANES analyses, checks numerical results, generates the main figure, and runs the separate Maloney supplement. A failed download, checksum, model check, or validation stops the run with a nonzero exit status. No credentials or private files are needed.

## Independent R survey verification

For a complete environment including R, use Conda or Mamba:

```sh
conda env create -f environment.yml
conda activate circumcision-reproduction
python scripts/reproduce.py --r-check
```

Alternatively, add R and the `survey` package to your Python setup and ensure `Rscript` is on `PATH`. The reference check uses R 4.5.3 and survey 4.5. It compares eight core NHANES models with the Python implementation, including coefficients, standard errors, confidence limits, p-values, sample sizes, and degrees of freedom. It uses the same harmonized records; it is an independent estimation check, not an independent re-extraction or validation of every extension model.

## Re-running and finding results

```sh
python scripts/reproduce.py --offline --r-check  # verify cached inputs and run everything
python scripts/reproduce.py --nhanes-only       # omit the Maloney analysis
```

`data/` contains downloaded and harmonized inputs. `outputs/` contains generated estimates, validation records, and figures. Both directories are ignored by Git. The runner records stage status and timing in `outputs/run.json` and individual logs in `outputs/logs/`. A successful run ends with `status: passed`.

Core estimates are in `outputs/models.csv`, with prevalence and sensitivity estimates beside them. Extensions write to `outputs/behavior_extension/`, `outputs/identity_subgroups/`, and `outputs/explanations/`. Maloney results are in `outputs/maloney/`. R comparisons are in `outputs/r_survey_*.csv`, with environment details in `outputs/r_survey_reference_session.txt`.

## Maloney sample clarification

The primary supplement and corrected manuscript use all 326 eligible respondents with the three required responses. The previous manuscript's 325-person sample is reproduced separately as `manuscript_sensitivity`: it additionally excludes a respondent missing partner-visibility comfort, although these models use general-visibility comfort. Both samples are generated and labeled. The corrected manuscript reports the 326-person primary analysis; see [methods](docs/methods.md).

A manually triggered GitHub Actions workflow (`Reproduce analyses`) also runs the Python pipeline on Linux with Python 3.11. It does not upload data or results. The local release check used Python 3.10.14, R 4.5.3, and survey 4.5.

## Repository guide

- `scripts/reproduce.py`: entry point and logged stage orchestration.
- `scripts/download.py` and `config/sources.json`: public URLs and SHA-256 checksums.
- `scripts/analyze.py`: source audits, harmonization, survey estimation, core outcomes.
- `scripts/behavior_extension.py`, `identity_subgroups.py`, `explanation_analysis.py`: NHANES extensions.
- `scripts/validate.py`, `validate_explanation_analysis.py`, `reproduce_survey.R`: numerical verification.
- `scripts/maloney_supplement.py`: separate circumcised-only supplement.
- `config/analysis.json` and [methods](docs/methods.md): analysis scope and interpretation.

The source manifest pins the actual downloaded bytes, including a commit-specific public Maloney workbook URL. If a provider changes a source, the downloader fails rather than silently accepting a different dataset. Investigate that change before updating a checksum. The original studies' data terms and attribution requirements continue to apply to downloaded files.
