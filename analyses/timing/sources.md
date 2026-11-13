# Source register

This register separates evidence about procedures from assumptions about timing among surviving adults. None of the audited sources identifies the infant share of the circumcised NHANES participants. The audit was targeted and structured, not an exhaustive systematic review.

The numerical inputs and denominators are recorded in [source_values.json](source_values.json). The original access classifications are preserved in [sources.json](sources.json). S01 and S07 are the only external numerical anchors in the executed timing code. The other studies inform interpretation or document why a source was not used.

## S01 — Owings, Uddin, and Williams, 2013, CDC/NCHS

Trends in Circumcision for Male Newborns in U.S. Hospitals, 1979–2010.

[Source 1](https://www.cdc.gov/nchs/data/hestat/circumcision_2013/circumcision_2013.htm)

**Access.** Official report and methods reviewed.

**Evidence.** National probability sample of birth hospitalizations. Published annual newborn rates cover 1979–2010. The series excludes procedures after discharge and outside the sampled hospital setting.

**Role in this analysis.** Birth-cohort coverage and descriptive newborn-rate extract only; no infant-share estimate.

**Decision and limits.** Primary historical birth-hospitalization anchor for overlapping birth years, with sampling uncertainty and explicit missing-setting adjustments. It leaves older birth cohorts uncovered. The denominator is male newborn birth hospitalizations, not circumcised adult men. Birthplace and survival/migration comparability must be addressed before combining with adult prevalence.

## S02 — Earlier NCHS newborn trends, 1979–1999



[Source 1](https://www.cdc.gov/nchs/data/hestat/circumcisions/circumcisions.htm)

**Access.** Official text and indexed table reviewed.

**Evidence.** Older NHDS tabulations include race and region. Some annual national values differ from the later report.

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Definition and version audit only until denominator, newborn identification, and coding differences are reconciled. Do not average the two versions or count them as independent datasets. Race categories are not automatically comparable to NHANES race/ethnicity categories.

## S03 — El Bcheraoui et al., 2014, JAMA Pediatrics



[Source 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC4578797/)

**Access.** Full text, methods, and age counts reviewed.

**Evidence.** SDI medical claims, 2001–2010. Of 1,400,920 circumcised males, 93.3% were newborns and 95.3% were infants. The article reports 28,197 aged 1–9 and 37,543 aged at least 10, including 8,590 aged 10–18. Age definitions must follow the tables because the abstract contains inconsistent inequality rendering.

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Context and age-pattern sensitivity. The data combine convenience-sampled inpatient encounters and outpatient providers, with differing dates and ascertainment. These counts are neither national annual totals nor cohort-specific lifetime timing proportions. Do not convert the large sample size into a narrowly concentrated timing prior for NHANES.

## S04 — Hart-Cooper et al., 2014, Pediatrics

Circumcision of Privately Insured Males Aged 0 to 18 Years in the United States.

[Source 1](https://pubmed.ncbi.nlm.nih.gov/25332502/) · [Source 2](https://publications.aap.org/pediatrics/article-abstract/134/5/950/75981/Circumcision-of-Privately-Insured-Males-Aged-0-to)

**Access.** Indexed publisher abstract and PubMed abstract, not the complete methods/tables.

**Evidence.** MarketScan 2010. Of 156,247 pediatric procedures, 93.6% were neonatal and 6.4% postneonatal. The birth cohort component reports 6.1% of uncircumcised neonates circumcised by their first birthday.

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Useful distinction between neonatal and later infancy. Privately insured children and contemporary cohorts limit transportability. No adult operations are included. Complete follow-up and enrollment definitions must be verified before quantitative use.

## S05 — Wiswell et al., 1993, Pediatrics

Circumcision in children beyond the neonatal period.

[Source 1](https://pubmed.ncbi.nlm.nih.gov/8233738/)

**Access.** Abstract reviewed.

**Evidence.** U.S. Army hospital births during 1985–1992, with detailed records for 476 postneonatal procedures. Mean age in that selected group was 2.92 years. The abstract also describes 32,072 boys not circumcised during neonatal hospitalization.

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Historical childhood timing and indications. Do not divide 476 by 32,072 to estimate cumulative incidence because the detailed records represent only a portion of later procedures. Military-system selection and follow-up require full-text verification before calibration.

## S06 — Nabavizadeh et al., 2022, PLOS ONE

Incidence of circumcision among insured adults in the United States.

[Source 1](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0275207)

**Access.** Full text and denominator construction reviewed.

**Evidence.** MarketScan commercial claims, men 18–64, 2015–2018, with 12,298 circumcision claims. Almost all were outpatient. The authors estimate the uncircumcised population at risk using historical newborn circumcision rates.

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Adult age/setting patterns and a modern rate benchmark, with coverage and historical extrapolation scenarios. The published rate is not based on directly observed uncircumcised person-time and is not independent of newborn-rate assumptions. Claims denominators must be reconstructed before extrapolation. Raw commercial claims are not openly available from the article. Diagnostic labels do not establish voluntary choice, sexual motivation, or chronology relative to sexual behavior.

## S07 — Owings and Kozak, 1998, NCHS Series 13 No. 139

Ambulatory and inpatient procedures in the United States, 1996.

[Source 1](https://www.cdc.gov/nchs/data/series/sr_13/sr13_139.pdf)

**Access.** Official PDF downloaded. Table 11, printed page 74 / PDF page 80, code 64.0 and headers checked in extracted layout text. Methods checked.

**Evidence.** Combined NHDS and NSAS national estimates, with separate inpatient and ambulatory components. Circumcision counts are given for under 15, 15–44, 45–64, and 65+. Units are thousands. Newborn inpatient records are excluded, but the under-15 category is not equivalent to adult or even postinfancy surgery. Some cells are flagged unreliable.

**Role in this analysis.** 1996 annual procedure-count anchor for conditional stock scenarios.

**Decision and limits.** Promising historical anchor for counts with age bands. Includes hospital and freestanding ambulatory surgery centers, but excludes some office, federal, and other settings. It cannot independently furnish a hard upper bound on all procedures. Never treat suppressed cells as zero. Published 1994–1995 companion reports are follow-up extraction candidates.

## S08 — Graves, 1995, NCHS Series 13 No. 122

Detailed diagnoses and procedures, NHDS 1993.

[Source 1](https://www.cdc.gov/nchs/data/series/sr_13/sr13_122.pdf)

**Access.** Official report scope and coding inspected. No age-specific numerical circumcision estimate extracted for this audit.

**Evidence.** Inpatient procedures, not comprehensive outpatient surgery.

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Historical component only. This is the source cited by Laumann et al. for the rarity of nonnewborn circumcision. That citation does not demonstrate a complete count of later procedures across settings.

## S09 — Laumann, Masi, and Zuckerman, 1997, JAMA

Circumcision in the United States.

[Source 1](https://jamanetwork.com/journals/jama/article-abstract/414922) · [Source 2](https://cirp.org/library/general/laumann/)

**Access.** Publisher abstract and article methods in a third-party transcription. Host editorial notes were excluded from the evidence.

**Evidence.** NHSLS 1992 national probability survey. The article explicitly states that respondents were not asked whether circumcision occurred as newborns or later.

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Adult prevalence/background only, not direct timing evidence. Its neonatal interpretation is an assumption supported partly by S08, not a measured timing distribution. No timing prior will be estimated from this study.

## S10 — NCHS questionnaire compendium, NHIS 1980–1984



[Source 1](https://www.cdc.gov/nchs/data/series/sr_01/sr01_024acc.pdf)

**Access.** Official PDF downloaded, all 213 pages searched. One circumcision item found at PDF page 93 / printed page 87 in the sample-child birth section.

**Evidence.** The item asks whether the child was ever circumcised. No age-at-procedure follow-up appears with that item.

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Does not establish timing. The placement within a birth section must not be interpreted as a neonatal-only question. This search was confined to this compendium and does not prove that no other NHIS instrument ever asked about timing.

## S11 — NCHS National Survey of Ambulatory Surgery products



[Source 1](https://archive.cdc.gov/www_cdc_gov/nchs/nsas/nsas_products.htm) · [Source 2](https://www.cdc.gov/nchs/data/nhsr/nhsr011.pdf)

**Access.** Official products page and 2006 report inspected. Circumcision was not located by text search in the 2006 published report.

**Evidence.** Public reports cover 1994, 1995, 1996, and 2006 ambulatory surgery. Availability of a survey does not establish an extractable, reliable circumcision-specific estimate.

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Data/codebook extraction route for adult count coverage. Verify procedure code detail, age, design variables, and cell reliability before adding numerical anchors.

## S12 — Contemporary freestanding children's-hospital study, 2020



[Source 1](https://pubmed.ncbi.nlm.nih.gov/32199703/)

**Access.** Abstract reviewed.

**Evidence.** PHIS, 2010–2017, selected pediatric hospitals and circumcisions without additional procedures.

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Illustrates setting selection in age distributions. Exclude from national timing calibration and adult totals. It cannot resolve historical adult timing.

## S13 — Begley et al., 2008, adult-circumcision willingness among U.S. MSM



[Source 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC2443289/) · [Source 2](https://stacks.cdc.gov/view/cdc/4256/cdc_4256_DS1.pdf)

**Access.** Indexed methods/results and abstract-level material reviewed; PMC access intermittently returned a browser challenge.

**Evidence.** Gay-pride-event survey of willingness to undergo adult circumcision, not a national count of procedures actually performed.

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Exclude from quantitative timing calibration. Willingness is not uptake. No verified estimate of differential lifetime timing by male–male behavior was obtained from this source.

## S14 — Introcaso et al., 2013, NHANES adult prevalence



[Source 1](https://pubmed.ncbi.nlm.nih.gov/23965763/)

**Access.** Abstract reviewed.

**Evidence.** 

**Role in this analysis.** Context or excluded from quantitative calibration.

**Decision and limits.** Context and possible prevalence cross-check. It overlaps the study's NHANES source and is not independent timing evidence. Do not use it as an external prior and then count NHANES prevalence again as independent information.

## From the sources to the scenarios

The newborn series overlaps only some birth cohorts and excludes procedures after birth discharge. Its percentages therefore cannot be assigned directly to the adult sample. A cohort-matched infant prevalence divided by adult circumcision prevalence could inform an infant share only with additional assumptions about ascertainment, survival and migration. We did not perform or claim such an identified reconstruction.

The modern claims percentages describe the age mix of recorded procedures. They do not supply the probability that a currently circumcised adult was circumcised in infancy. In particular, the 95.3% SDI infant procedure share was not used to set a 95% infant-share prior.

The 1996 procedure counts enter an age-compatible stock calculation. Constant historical rates, missing-setting multipliers, retention and age-band allocations are assumptions recorded separately from extracted numbers. This construction supplies a conditional benchmark, not an all-setting upper bound.

Follow-up leads such as the 1994–1995 NSAS reports were not extracted into this calculation. Their mention in the source audit must not be read as evidence that their counts were included.
