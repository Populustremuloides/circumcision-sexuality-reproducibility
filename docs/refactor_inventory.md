# Refactor inventory

The active workflow is frequentist-only. Historical implementations remain at `backup/pre-frequentist-only-20261114`. No history was rewritten.

## Retained analytical components

| Component | Purpose |
|---|---|
| `src/data/` | Checksum-verified source acquisition, XPT decoding and original harmonization. |
| `src/survey/design.py` | Original domain-aware survey logistic and descriptive estimators; optional complete-fit return does not alter inference. |
| `src/frequentist/nhanes.py` | Main adjustment sequence, identity comparisons, sensitivity models and descriptive prevalence. |
| `src/frequentist/behavior.py` | Original specific-practice analyses and multiplicity families. |
| `src/frequentist/identity.py` | Original identity subgroup and interaction analyses. |
| `src/frequentist/explanations.py` | Original explanatory contrasts, paired jackknife and explicit failed-model records. |
| `src/frequentist/maloney.py` | Optional separate supplement, primary 326 and sensitivity 325; retained pending editorial inclusion decision. |
| `src/frequentist/export.py` | Complete primary fit, sample IDs, standardization inputs and provenance checks. |
| `analyses/nhanes/`, `analyses/maloney/` | Minimal runnable model interfaces. |
| `analyses/timing/counts.py`, `endpoints.py` | Historical procedure-count arithmetic and infant-only/adult-only conditional endpoints. |
| `analyses/timing/sources*`, `source_values.json`, `references.bib` | Audited source locations, limitations and extracted assumptions. |
| `analyses/figures/` | Existing selected figure mathematics and rendering, fed by the frequentist export. |
| `validation/frequentist/` | Original numerical/coding checks and frozen aggregate regression targets. |
| `validation/release.py`, `validation/figures.py` | Regression preservation, export provenance and pointwise mixture checks. |
| `validation/r_survey/` | Independent optional R survey comparison. |
| `scripts/reproduce.py`, `build_results.py` | One workflow and generated numerical documentation. |

## Removed files

| File | Reason |
|---|---|
| `analyses/timing/extraction_addendum.txt` | Historical execution plan archived in backup tag; source facts retained in source_extraction.txt and current mixture methods retained in methods.md. |
| `analyses/timing/run_allocation.py` | Exploratory coefficient-draw/allocation framework; current conditional endpoints, source arithmetic and selected figures remain active. |
| `analyses/timing/run_conditional.py` | Exploratory coefficient-draw/allocation framework; current conditional endpoints, source arithmetic and selected figures remain active. |
| `analyses/timing/run_timing.py` | Exploratory coefficient-draw/allocation framework; current conditional endpoints, source arithmetic and selected figures remain active. |
| `docs/code_reference.json` | Replaced immutable references to obsolete code with checkout-relative result-to-code links. |
| `environment.yml` | Duplicate environment specification; pinned Python requirements plus optional R survey documented separately. |
| `scripts/analyze.py` | Obsolete wrapper; retained implementation is invoked directly. |
| `scripts/behavior_extension.py` | Obsolete wrapper; retained implementation is invoked directly. |
| `scripts/download.py` | Obsolete wrapper; retained implementation is invoked directly. |
| `scripts/explanation_analysis.py` | Obsolete wrapper; retained implementation is invoked directly. |
| `scripts/identity_subgroups.py` | Obsolete wrapper; retained implementation is invoked directly. |
| `scripts/maloney_supplement.py` | Obsolete wrapper; retained implementation is invoked directly. |
| `scripts/plot_main.py` | Obsolete wrapper; retained implementation is invoked directly. |
| `scripts/reproduce_survey.R` | Obsolete wrapper; retained implementation is invoked directly. |
| `scripts/validate.py` | Obsolete wrapper; retained implementation is invoked directly. |
| `scripts/validate_explanation_analysis.py` | Obsolete wrapper; retained implementation is invoked directly. |
| `src/bayesian/__init__.py` | Outside frequentist-only scope; historical implementation remains in backup tag. |
| `src/bayesian/approximation.py` | Outside frequentist-only scope; historical implementation remains in backup tag. |
| `src/bayesian/headline.py` | Outside frequentist-only scope; historical implementation remains in backup tag. |
| `src/bayesian/logistic.py` | Outside frequentist-only scope; historical implementation remains in backup tag. |
| `src/bayesian/maloney.py` | Outside frequentist-only scope; historical implementation remains in backup tag. |
| `src/frequentist/figure.py` | Obsolete summary figure/report; selected publication figures have their own preserved renderer. |
| `validation/bayesian/__init__.py` | Outside frequentist-only scope; historical implementation remains in backup tag. |
| `validation/bayesian/compare.py` | Outside frequentist-only scope; historical implementation remains in backup tag. |
| `validation/bayesian/sparse_data_addendum.txt` | Outside frequentist-only scope; historical implementation remains in backup tag. |
| `validation/bayesian/validation_plan.txt` | Outside frequentist-only scope; historical implementation remains in backup tag. |
| `validation/simulations/__init__.py` | Outside frequentist-only scope; historical implementation remains in backup tag. |
| `validation/simulations/informative_sampling.py` | Outside frequentist-only scope; historical implementation remains in backup tag. |
| `validation/simulations/targeted.py` | Outside frequentist-only scope; historical implementation remains in backup tag. |

## Current module dependency inventory

Direct imports are listed below; dynamically dispatched stages are enumerated in `scripts/reproduce.py` and `analyses/figures/reproduce.py`. No active module imports a Bayesian implementation.

| Module | Direct imports |
|---|---|
| `src/__init__.py` |  |
| `src/data/__init__.py` |  |
| `src/data/download.py` | `concurrent.futures`, `datetime`, `hashlib`, `json`, `pathlib`, `time`, `urllib.request`, `argparse` |
| `src/data/nhanes.py` | `json`, `platform`, `pathlib`, `numpy`, `pandas`, `patsy`, `pyreadstat`, `bs4`, `scipy.special`, `scipy.stats`, `scipy`, `statsmodels`, `statsmodels.api`, `src.specification` |
| `src/frequentist/__init__.py` |  |
| `src/frequentist/behavior.py` | `json`, `pathlib`, `numpy`, `pandas`, `pyreadstat`, `statsmodels.stats.multitest`, `src.frequentist.nhanes` |
| `src/frequentist/explanations.py` | `hashlib`, `json`, `warnings`, `datetime`, `numpy`, `pandas`, `patsy`, `pyreadstat`, `statsmodels.api`, `scipy.special`, `scipy.stats`, `statsmodels.stats.multitest`, `statsmodels.tools.sm_exceptions`, `src.frequentist.nhanes` |
| `src/frequentist/export.py` | `hashlib`, `json`, `subprocess`, `numpy`, `scipy.special`, `src.specification` |
| `src/frequentist/identity.py` | `json`, `pathlib`, `numpy`, `pandas`, `patsy`, `statsmodels.api`, `scipy.stats`, `statsmodels.stats.multitest`, `src.frequentist.nhanes` |
| `src/frequentist/maloney.py` | `hashlib`, `json`, `pathlib`, `numpy`, `pandas`, `scipy.stats`, `scipy.stats.contingency`, `statsmodels.api` |
| `src/frequentist/nhanes.py` | `json`, `platform`, `pathlib`, `numpy`, `pandas`, `patsy`, `pyreadstat`, `bs4`, `scipy.special`, `scipy.stats`, `scipy`, `statsmodels`, `statsmodels.api`, `src.specification`, `src.data.nhanes`, `src.survey.design` |
| `src/specification.py` | `json`, `pathlib` |
| `src/survey/__init__.py` |  |
| `src/survey/design.py` | `json`, `platform`, `pathlib`, `numpy`, `pandas`, `patsy`, `pyreadstat`, `bs4`, `scipy.special`, `scipy.stats`, `scipy`, `statsmodels`, `statsmodels.api`, `src.specification` |
| `analyses/__init__.py` |  |
| `analyses/figures/__init__.py` |  |
| `analyses/figures/confounding_plot.py` | `os`, `pathlib`, `json`, `numpy`, `pandas`, `matplotlib`, `matplotlib.pyplot`, `matplotlib.colors`, `matplotlib.patches`, `matplotlib.ticker` |
| `analyses/figures/reproduce.py` | `pathlib`, `subprocess`, `sys`, `json`, `src.frequentist.export` |
| `analyses/figures/timing_or_curves.py` | `os`, `pathlib`, `sys`, `json`, `hashlib`, `numpy`, `pandas`, `scipy.special`, `scipy.optimize`, `analyses.timing.endpoints`, `src.frequentist.export` |
| `analyses/figures/timing_plot.py` | `os`, `pathlib`, `json`, `numpy`, `pandas`, `matplotlib`, `matplotlib.pyplot`, `matplotlib.ticker`, `matplotlib.lines` |
| `analyses/figures/timing_probability_curves.py` | `os`, `pathlib`, `sys`, `json`, `numpy`, `pandas`, `scipy.special`, `scipy.optimize`, `analyses.timing.endpoints`, `src.frequentist.export` |
| `analyses/maloney/__init__.py` |  |
| `analyses/maloney/run.py` | `src.frequentist.maloney` |
| `analyses/nhanes/__init__.py` |  |
| `analyses/nhanes/run.py` | `argparse`, `pandas`, `src.specification`, `src.survey.design`, `src.frequentist.export` |
| `analyses/timing/__init__.py` |  |
| `analyses/timing/counts.py` | `json`, `pandas`, `numpy`, `src.specification`, `src.frequentist.export` |
| `analyses/timing/endpoints.py` | `json`, `numpy`, `pandas`, `scipy.special`, `scipy.optimize`, `src.specification`, `src.frequentist.export` |
| `analyses/timing/reproduce.py` | `analyses.timing.counts`, `analyses.timing.endpoints` |
| `validation/__init__.py` |  |
| `validation/figures.py` | `json`, `numpy`, `pandas`, `scipy.special`, `src.specification`, `src.frequentist.export` |
| `validation/frequentist/__init__.py` |  |
| `validation/frequentist/core.py` | `hashlib`, `json`, `pathlib`, `sys`, `numpy`, `pandas`, `bs4`, `src.frequentist.nhanes` |
| `validation/frequentist/explanations.py` | `hashlib`, `json`, `numpy`, `pandas`, `patsy`, `scipy.stats`, `statsmodels.stats.multitest`, `src.frequentist.explanations` |
| `validation/r_survey/__init__.py` |  |
| `validation/release.py` | `argparse`, `json`, `numpy`, `pandas`, `src.specification`, `src.frequentist.export` |
| `validation/repository.py` | `ast`, `re`, `pathlib`, `src.specification` |
| `scripts/build_results.py` | `argparse`, `json`, `pathlib`, `pandas`, `src.specification`, `src.frequentist.export` |
| `scripts/reproduce.py` | `argparse`, `json`, `os`, `shutil`, `subprocess`, `sys`, `time`, `datetime`, `pathlib` |

## Dependencies

Pinned Python dependencies remain unchanged: NumPy, pandas, SciPy, statsmodels and patsy support the original models; pyreadstat and BeautifulSoup support source decoding/audits; Matplotlib renders the selected figures; openpyxl supports the optional Maloney source. There are no Bayesian-only runtime dependencies. R and its survey package are optional locally and independently checked in CI.

## Figure design exception

The timing OR panel upper limit increases from 1.60 to 1.62 because the 10% adult-share curve begins at OR 1.605283 under the frequentist coefficients. Shading clipping follows the same ceiling. No palette, typography, line style, legend, panel order, margin or figure-size setting was changed. The confounding renderer is unchanged.
