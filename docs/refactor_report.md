> Historical refactor report: the values below describe the earlier 2005–2016 analysis. For the current pooled result, see [results](results.md).

# Frequentist-only refactor verification — 14 November 2026

## Repository changes

The primary survey estimator, harmonization, model formulas, eligibility, weighting, variance calculations and original multiplicity families are unchanged. A complete-fit export now supplies both selected figures. The active workflow runs the retained frequentist analyses, source audit, timing endpoints, figure calculations and validations; numerical documentation is generated from their output records. Bayesian implementations and obsolete wrappers are removed from the active tree, recoverable from the backup tag. Maloney remains an explicit optional supplement pending an editorial inclusion decision.

The pre-refactor backup is `backup/pre-frequentist-only-20261114`, pointing to `f054058203e6d926b2017e1c2aee5f74bacecb73`. Work is isolated on `refactor/frequentist-only-20261114`; no history was rewritten and nothing was pushed to main.

The manuscript was not edited. Its SHA-256 remains `0701b7f6f8eb99ba510d1b24de62f55e8c7f2baa96c3d675750677bea8a4bf8d`.

## Numerical comparison

The former column describes the archived Bayesian coefficient-mean figure inputs, solely to audit this transition. Current calculations use the frequentist fit. Both versions standardize to circumcised complete cases; these are not raw group prevalences.

| Quantity | Former figure input | Frequentist replacement |
|---|---|---|
| Conditional OR | 1.48693 | 1.5433 |
| Intact-reference standardized probability (%) | 4.5378 | 4.44802 |
| Circumcised standardized probability (%) | 6.58213 | 6.68034 |
| Standardized gap (percentage points) | 2.04433 | 2.23233 |
| Minimum adult-only share (%) | 2.15547 | 2.35173 |

The unchanged primary model has N = 9,161, 498 events, OR 1.543297069879, 95% CI 1.162706294736–2.048467318601, p = 0.003125048206.

### Explicit infant-only and adult-only endpoints

| Scenario | Assumed share (%) | Former OR | New OR | Former component baseline (%) | New component baseline (%) | Former required prevalence (%) | New required prevalence (%) |
|---|---|---|---|---|---|---|---|
| adult_only | 3 | 57.4142 | 82.8357 | 4.97816 | 4.93784 | 73.1226 | 79.3487 |
| adult_only | 5 | 17.7491 | 21.0327 | 4.79657 | 4.73585 | 45.6833 | 49.3824 |
| adult_only | 10 | 7.07345 | 7.93647 | 4.66037 | 4.58436 | 25.1037 | 26.9076 |
| infant_only | 95 | 1.51315 | 1.57262 | 4.53851 | 4.44881 | 6.69045 | 6.79863 |
| infant_only | 90 | 1.54236 | 1.60528 | 4.53931 | 4.4497 | 6.81079 | 6.93006 |
| infant_only | 80 | 1.61203 | 1.68324 | 4.5412 | 4.4518 | 7.09662 | 7.24221 |

The other timing components are held at conditional intact-reference probability. Component baselines and required prevalences use the same constructed component weights. Shares are assumptions, not measured age distributions.

### Endpoints of the displayed timing curves

| Adult share (%) | Former before-18-only OR | New before-18-only OR | Former adult-only OR | New adult-only OR |
|---|---|---|---|---|
| 1 | 1.49196 | 1.54892 | inf | inf |
| 1.5 | 1.49451 | 1.55177 | inf | inf |
| 2.5 | 1.4997 | 1.55757 | 139.286 | 358.795 |
| 5 | 1.51315 | 1.57262 | 17.7491 | 21.0327 |
| 10 | 1.54236 | 1.60528 | 7.07345 | 7.93647 |

An infinite adult-only entry means no feasible finite adult-only explanation at that share; the curve still permits a positive before-18 component. The 2.5% adult-only OR now exceeds the retained horizontal maximum of 250, so the existing renderer correctly shows continuation. The minimum share is the weighted mean of individual conditional feasibility limits, not the gap divided by one minus the marginal baseline.

## Figure review

The final [timing PNG](../figures/timing.png), [PDF](../figures/timing.pdf), [SVG](../figures/timing.svg), and [confounding PNG](../figures/confounding.png), [PDF](../figures/confounding.pdf), [SVG](../figures/confounding.svg) were regenerated from the same verified fitted artifact. PNG and rendered PDF versions were visually inspected against archived originals. Both SVG canvases, font declarations and color palettes match the originals. PNG dimensions remain 3476×1276 and 2376×1540.

No palette, line style, typography, legend, panel ordering, margins or figure-size setting changed. The confounding renderer is byte-for-byte unchanged. The one necessary design adjustment is the timing OR ceiling, from 1.60 to 1.62, because the 10% adult-share curve starts at 1.605283. Shading clipping follows that ceiling. The confounding first legend band changes from 2.04–5 to 2.23–5 percentage points. Data-driven curve positions, boundaries and endpoints change as expected. No labels or legends were cropped in the inspected renders.

## Code inventory and manuscript integration

[File-by-file cleanup and dependency inventory](refactor_inventory.md) lists every removed file and each retained component’s role. [Manuscript integration notes](manuscript_integration.md) provide exact current numbers, proposed external captions and methods wording. Raw survey-weighted prevalences remain distinct from model-standardized probabilities.

## Executed checks

Commands were run with the repository’s pinned Python environment. The clean-source test used a separate Git-initialized snapshot with no data or generated output directories, then downloaded all 24 NHANES inputs. It reused the installed pinned Python environment; it did not install dependencies into a second fresh virtual environment. An initial sandbox DNS failure was resolved by allowing network access. A temporary-copy exclusion initially omitted `src/data`; that staging error was corrected before the successful clean run.

```sh
python scripts/reproduce.py --offline --with-maloney
Rscript validation/r_survey/reproduce.R
# In the isolated clean source tree, with an empty input cache:
python scripts/reproduce.py
python -m analyses.figures.reproduce
python -m scripts.build_results --check
python -m validation.repository
python -m pip check
git diff --check
```

All 15 retained reference tables matched (including Maloney); relative tolerance 1e-7, absolute tolerance 1e-9. Headline exports match the existing focal outputs to rtol 1e-9, atol 1e-10. Coding/routing, source checksums, domain variance, weight invariance, original convergence/conditioning and selected Taylor/jackknife checks passed. Failed sparse contrasts remain explicitly unavailable.

Independent R survey comparisons covered eight core models; tolerance 1e-6:

| field | max_absolute_difference | tolerance | passed |
|---|---|---|---|
| beta | 6.23279e-13 | 1e-06 | True |
| se | 4.55003e-09 | 1e-06 | True |
| odds_ratio | 1.16596e-12 | 1e-06 | True |
| ci_low | 1.05344e-08 | 1e-06 | True |
| ci_high | 1.85597e-08 | 1e-06 | True |
| p_value | 9.05205e-10 | 1e-06 | True |

Figure validation reconstructed 9,016 saved conditional OR-curve points with maximum absolute mixture error 8.33e-17, plus all saved probability curves, 3,500 confounding boundary points and 1,078,449 feasible color-grid cells. Timing reconstruction tolerance is 1e-10; probability-space checks are 1e-9 or tighter. Both figures share the same standardized targets.

Documentation checks passed; active Python modules have no Bayesian imports and relative file links resolve. Pinned dependencies passed `pip check`. Generated SVG coordinate trailing spaces are explicitly exempted in `.gitattributes`; the code/documentation diff passes whitespace checks. GitHub Actions now runs core reproduction, documentation checks and the independent R comparison. The remote CI run has not been executed for this unpushed branch.

## Limits

Timing and confounding curves remain assumption-based point scenarios; no scenario confidence intervals were computed. The 1.5% marker is a historical extrapolation, not a measured lifetime fraction, upper bound or best-supported probability. Before-18 is not infancy. The binary-confounder construction is not an exclusion of every possible bias structure. No independent human statistical review, new cohort replication or causal identification is implied.
