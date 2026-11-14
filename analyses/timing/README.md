# Circumcision timing sensitivity

NHANES records current circumcision status, not age at surgery. These point scenarios ask how the fitted association could be distributed across unobserved timing groups. Infant and adult shares are assumptions, not measured age distributions.

- [Results](results.md): infant-only and adult-only component associations, standardized to the constructed component.
- [Methods](methods.md): mixture restrictions, feasibility, standardization and procedure-count extrapolation.
- [Sources](sources.md), [numerical inputs](source_values.json) and [bibliography](references.bib): extracted observations and separate assumptions.
- [Reporting notes](reporting.md): manuscript integration and interpretation.
- [Source extraction record](source_extraction.txt): original source facts and count assumptions; the full historical execution plan remains in the backup tag.

After `python scripts/reproduce.py`, this package has already run. Rerun it with `python -m analyses.timing.reproduce`. Results stay in `outputs/timing/`; rebuild documentation with `python -m scripts.build_results`.

[Counts](counts.py) preserves the historical source arithmetic and cohort coverage. [Endpoints](endpoints.py) uses the exported frequentist primary model. The [paired figure](../../figures/timing.pdf) instead splits timing before 18 versus adulthood. Before 18 must not be relabeled infancy. The infant-only endpoint fixes both childhood/adolescent and adult components to baseline, while the adult-only endpoint fixes infant and childhood/adolescent components to baseline.

The starred adult-share scenario is an extrapolation from historical counts. It is neither a measured share nor a hard upper bound. Timing-specific effects are not identified by these calculations.
