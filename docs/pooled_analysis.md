# Pooled primary behavior analysis and questionnaire audit

The final primary behavior window is 1999–2016, selected retrospectively on 16 November 2026. Earlier-period comparisons now overlap the primary sample and are not independent replication. Identity and practice/subgroup extensions retain their documented original periods.

[Assembly and audit](../analyses/nhanes/pooled.py) · [Export](../analyses/nhanes/run.py) · [Table 1](../analyses/nhanes/descriptive.py) · [Independent R verification](../analyses/nhanes/verify_pooled.R).

## Questionnaire skips

1999–2004 uses valid SXQ200 counts (0–9999), coding SXQ020=2 as zero. 2005–2008 uses SXQ410 (0–2000), coding SXQ021=2 as zero. 2009–2016 uses direct SXQ809 yes/no responses. Unknown, refused and unspecified missing remain unavailable. The audit reopens all raw sexual-behavior and demographic files and checks contradictory responses and marital history.

CDC documents confusing earlier screening wording and never-sex responses among married respondents. Marriage does not establish male–male experience, so no positive outcome is invented. Two sensitivity checks exclude negative-screen respondents reporting marriage/former marriage/cohabitation (DMDMARTL 1,2,3,4,6), then exclude all earlier negative-screen zeros. Pregnancy-based guidance does not apply to this male domain. Exclusions change the target population and do not establish which reports were accurate.

All cycles have zero negative-screen/direct-answer versus positive male-partner contradictions. There are 615 eligible earlier screen negatives, of whom 399 report marriage/former marriage/cohabitation. The corresponding complete-case exclusions remove 566 and 364 men. Cycle-level counts and missingness are in `outputs/pooled/skip_audit.csv`.

| Specification | N | Adjusted OR (95% CI) | Nominal p |
|---|---:|---:|---:|
| Pooled 1999–2016 | 12,973 | 1.47 (1.15–1.88) | .0023 |
| Exclude 1999–2000 | 11,842 | 1.55 (1.19–2.02) | .0013 |
| Original 2005–2016 | 9,161 | 1.54 (1.16–2.05) | .0031 |
| Direct question 2009–2016 | 6,261 | 1.43 (1.02–2.00) | .0371 |
| Exclude ambiguous screening zeros | 12,609 | 1.46 (1.14–1.87) | .0027 |
| Exclude all earlier screening zeros | 12,407 | 1.47 (1.15–1.88) | .0026 |

Exact results: `outputs/pooled/models.csv`. Models use the same demographic adjustments and survey-domain inference. Primary weights are WTMEC4YR × 2/9 for 1999–2002, WTMEC2YR / 9 thereafter; excluding 1999 uses the available two-year 2001–2002 weight.

## Tables and figures

Table 1 now describes the pooled exported complete-case sample. Raw prevalence tables retain their actual available-case denominators. Figure standardization, timing endpoints and confounding bands all use the pooled fitted coefficients and common circumcised complete-case target. Historical extensions remain labeled with their original periods.

Historical procedure counts now use unscaled population weights instead of the old hard-coded six-cycle multiplier. For each 1999–2002 two-year cycle, the illustration uses twice WTMEC4YR to undo its half-period contribution; these cycle-level denominators still inherit the limitation of combined-period weight calibration. The 1.5% marker remains an illustrative extrapolation, not an estimated or preferred share. Both timing component ORs are constrained to at least one in the displayed region. Confounding remains a specified binary-mixture illustration, not a general bound. No scenario uncertainty intervals are claimed.

[CDC screening guidance](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/SXQ_E.htm) · [Direct-question codebook](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2009/DataFiles/SXQ_F.htm) · [Historical earlier coding](../analyses/replication/specification.md).
