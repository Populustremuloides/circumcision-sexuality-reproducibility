# Numerical validation

The default reproduction checks source checksums, independent XPT readers, questionnaire coding and routing, complete-case counts, model formulas, survey weights, strata/PSU nesting and domain variance. The survey fitter checks convergence, rank, conditioning, scores and agreement between two sandwich calculations. A hand-calculated example retains an empty-domain PSU. Common rescaling of weights must preserve coefficients and survey standard errors.

Selected behavior and identity models retain stratified delete-one-PSU jackknife comparisons. Explanatory contrasts preserve paired restandardization and their original Holm families, including explicit placeholders for failed tests. A failed fit is not a null result. The focal gay-only fit is retained, but no successful delete-PSU validation is claimed for every sparse identity specification.

`validation/frequentist/reference_results.json` freezes aggregate validation targets from the pre-refactor validated results. `validation.release` compares all retained tables, including sensitivities and multiplicity-adjusted results, with relative tolerance 1e-7 and absolute tolerance 1e-9. It also compares exported full-model focal estimates with the existing analysis outputs. These reference values are not used to fit models.

The optional R check independently fits eight core models with `survey::svyglm`, checking coefficients, standard errors, ORs, interval endpoints and p-values to absolute tolerance 1e-6. It reuses harmonized inputs; it does not independently validate their coding or every extension. Install R and its `survey` package, then run `python scripts/reproduce.py --r-check` or `Rscript validation/r_survey/reproduce.R` after the Python workflow.

The figure runner verifies artifact/input/code hashes, standardization targets and mixture reconstruction. Feasible conditional timing mixtures reconstruct the predicted probability within 1e-10; probability-space and confounding mixtures are checked to 1e-9 or tighter. The confounding plot checks every feasible color-grid sample. Scenario curves have no uncertainty bands.

Run `python scripts/reproduce.py`, `python -m analyses.figures.reproduce`, and `python -m scripts.build_results --check`. Local validation records are under `outputs/frequentist/`, `outputs/validation/`, `outputs/timing/` and `outputs/selected_figures/`. Add `--with-maloney` to include and verify the separate supplement.

These checks support computational correctness under the implemented model. They do not rule out confounding, reporting bias, selection, or a failure of the population association to replicate. No independent human statistical review is claimed.
