> Historical specification, preserved verbatim below. Superseded for the final primary behavior analysis on 16 November 2026 by pooled 1999–2016; this earlier subset is no longer independent of the primary sample.

# Fixed temporal replication specification

Frozen before calculating exposure–outcome cross-tabulations or regression associations, 15 November 2026. This is a retrospectively chosen independent-period test within NHANES, not a prospective registration or an independent survey system. The 2005–2016 analysis remains primary and the periods will not be pooled.

## Feasibility

Public DEMO and SXQ files for 1999–2000, 2001–2002 and 2003–2004 provide circumcision (SXQ280), lifetime male partner count (SXQ200), lifetime sex screening (SXQ020), age, race/ethnicity (RIDRETH1), adult education (DMDEDUC2), birth country (DMDBORN), examination weights and masked strata/PSUs. All required adjustment categories are harmonizable. Sources and checksums are recorded in sources.json.

| Cycle | Eligible men | Known circumcision | Known outcome | Both known | Complete cases |
|---|---:|---:|---:|---:|---:|
| 1999–2000 | 1273 | 1140 | 1174 | 1134 | 1131 |
| 2001–2002 | 1584 | 1436 | 1451 | 1425 | 1424 |
| 2003–2004 | 1425 | 1260 | 1264 | 1257 | 1257 |

These eligibility and missingness checks were performed before estimating the association. They establish 3,812 complete cases. No exposure-specific outcome count or odds ratio was inspected in this feasibility stage.

SXQ280 uses the same self-report circumcision categories with clinical sketches. SXQ020 introduces vaginal, oral or anal sex and routes never-sex respondents to circumcision. SXQ200 asks lifetime male partner count. The 1999 documentation cautions that some 1999 questions used “sexual intercourse” instead of “sex.” This may affect interpretation and recall, despite the broad screening definition. These earlier questions are closer to the 2005–2008 partner-history construction than the explicit 2009–2016 male–male behavior item. The result is an interpretable temporal replication with a measurement limitation, not an exact questionnaire replication. Sexual identity is outside this replication specification.

## Fixed execution

- Include respondents recorded male, ages 20–59, with positive MEC weights. Preserve all positive-weight participants in the survey design and estimate the eligible complete-case domain.
- Map SXQ280 1 to circumcised and 2 to intact; 7, 9 and missing remain unavailable.
- Valid SXQ200 integers 0–9999 define outcome 0 for none and 1 for at least one. Codes 77777/99999 and missing remain unavailable. Code SXQ020=2 as outcome zero after checking for contradictory positive counts. Screen refusals/unknowns do not imply zero.
- Use age10=(age−40)/10; RIDRETH1 categories 1–5; DMDEDUC2 categories 1–5; DMDBORN=1 as U.S.-born, 2/3 as born outside the 50 states/DC; other values unavailable. Retain cycle as a categorical adjustment. Model-specific complete cases, no imputation.
- Six-year examination weights: 2/3 × WTMEC4YR for 1999–2002 and 1/3 × WTMEC2YR for 2003–2004. Use public SDMVSTRA and SDMVPSU nested within stratum. The public stratum ranges are distinct across these cycles (1–43), so cycle-prefixing preserves their identities. The three-PSU stratum in 1999–2000 is retained.
- Primary replication formula: msm_ever ~ circ + age10 + I(age10**2) + C(cycle) + C(race) + C(education) + foreign_born. Use the existing Survey.model Taylor-linearized estimator, residual design degrees of freedom, two-sided nominal p-value and 95% confidence interval.
- Report the unadjusted circ-only association as descriptive context, not a second confirmatory endpoint. No subgroup interactions, model selection or significance-driven pooling.
- One predetermined measurement sensitivity excludes 1999–2000, uses WTMEC2YR/2 for 2001–2004 and otherwise retains the fully adjusted specification. Label its p-value exploratory and nominal.
- Independently verify these three models with R survey. Publish all results including null, opposite-direction and non-estimable results; do not equate a nonsignificant replication with equivalence. Compare estimates and uncertainty with the primary period without a new pooled test.

Sources: [1999 SXQ](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/1999/DataFiles/SXQ.htm), [2001 SXQ](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2001/DataFiles/SXQ_B.htm), [2003 SXQ](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2003/DataFiles/SXQ_C.htm), [CDC weighting instructions](https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx). The feasibility sample sizes are generated from the linked source files, not CDC's all-sex frequency totals.
