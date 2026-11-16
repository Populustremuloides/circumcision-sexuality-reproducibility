# Retained 2005–2016 sensitivity and extension results

Generated from local frequentist output tables. Unavailable estimates and failed fits remain visible. Interaction ORs are ratios of subgroup ORs. Explanatory contrasts retain their named scale, including differences; they must not all be read as odds ratios. Holm corrections cover only their original named families, not the entire exploratory search.

## Main model sequence

[Implementation](../src/frequentist/nhanes.py); exact local record: `outputs/frequentist/models.csv`.

| outcome | model | n | events | odds_ratio | ci_low | ci_high | p_value | sample |
|---|---|---|---|---|---|---|---|---|
| identity_gb | unadjusted | 8970 | 333 | 1.49267 | 1.07181 | 2.07879 | 0.0183142 | available_for_model |
| identity_gb | unadjusted | 8962 | 333 | 1.49227 | 1.07155 | 2.0782 | 0.0183812 | full_model_complete_cases |
| identity_gb | age_cycle | 8970 | 333 | 1.50279 | 1.08774 | 2.07622 | 0.0141241 | available_for_model |
| identity_gb | age_cycle | 8962 | 333 | 1.50209 | 1.08716 | 2.0754 | 0.0142503 | full_model_complete_cases |
| identity_gb | demographic | 8966 | 333 | 1.27251 | 0.889814 | 1.81981 | 0.183761 | available_for_model |
| identity_gb | demographic | 8962 | 333 | 1.27207 | 0.889686 | 1.8188 | 0.18414 | full_model_complete_cases |
| identity_gb | full | 8962 | 333 | 1.25175 | 0.853146 | 1.83658 | 0.247093 | available_for_model |
| identity_gb | full | 8962 | 333 | 1.25175 | 0.853146 | 1.83658 | 0.247093 | full_model_complete_cases |
| msm_ever | unadjusted | 9169 | 498 | 1.86682 | 1.41171 | 2.46864 | 2.50997e-05 | available_for_model |
| msm_ever | unadjusted | 9161 | 498 | 1.8664 | 1.41128 | 2.46828 | 2.53726e-05 | full_model_complete_cases |
| msm_ever | age_cycle | 9169 | 498 | 1.87046 | 1.41919 | 2.46522 | 2.04918e-05 | available_for_model |
| msm_ever | age_cycle | 9161 | 498 | 1.86955 | 1.41833 | 2.46431 | 2.09178e-05 | full_model_complete_cases |
| msm_ever | demographic | 9165 | 498 | 1.6466 | 1.22818 | 2.20757 | 0.00111122 | available_for_model |
| msm_ever | demographic | 9161 | 498 | 1.64595 | 1.22796 | 2.20621 | 0.00111196 | full_model_complete_cases |
| msm_ever | full | 9161 | 498 | 1.5433 | 1.16271 | 2.04847 | 0.00312505 | available_for_model |
| msm_ever | full | 9161 | 498 | 1.5433 | 1.16271 | 2.04847 | 0.00312505 | full_model_complete_cases |

## Sensitivity models

[Implementation](../src/frequentist/nhanes.py); exact local record: `outputs/frequentist/sensitivities.csv`.

| outcome | model | n | events | odds_ratio | ci_low | ci_high | p_value |
|---|---|---|---|---|---|---|---|
| identity_gb | exclude_2015_2016 | 7605 | 272 | 1.26088 | 0.802638 | 1.98074 | 0.30899 |
| identity_gb | direct_behavior_2009_2016 | 6088 | 224 | 1.08719 | 0.699913 | 1.68876 | 0.704393 |
| identity_gb | us_born_only | 6501 | 267 | 1.19086 | 0.739069 | 1.91884 | 0.468191 |
| identity_gb | add_income | 8355 | 319 | 1.20317 | 0.814333 | 1.77767 | 0.348303 |
| identity_gb | age_decade_categories | 8962 | 333 | 1.25317 | 0.857694 | 1.83099 | 0.239565 |
| identity_gb | identity_behavior_common_sample | 8936 | 332 | 1.25129 | 0.851551 | 1.83868 | 0.249696 |
| identity_gb | sexually_experienced | 8446 | 325 | 1.21281 | 0.822432 | 1.78848 | 0.32572 |
| identity_gb | leave_out_2005 | 7640 | 279 | 1.18439 | 0.773767 | 1.81291 | 0.429964 |
| identity_gb | cycle_2005 | 1322 | 54 | 2.56512 | 1.0375 | 6.34203 | 0.0426356 |
| identity_gb | leave_out_2007 | 7410 | 278 | 1.17875 | 0.797301 | 1.7427 | 0.403678 |
| identity_gb | cycle_2007 | 1553 | 55 | 1.51479 | 0.407467 | 5.63136 | 0.506446 |
| identity_gb | leave_out_2009 | 7292 | 281 | 1.16506 | 0.772083 | 1.75806 | 0.460735 |
| identity_gb | cycle_2009 | 1673 | 52 | 1.47958 | 0.549219 | 3.98597 | 0.408556 |
| identity_gb | leave_out_2011 | 7445 | 279 | 1.39939 | 0.923439 | 2.12065 | 0.111153 |
| identity_gb | cycle_2011 | 1519 | 54 | 1.35687 | 0.657817 | 2.7988 | 0.381256 |
| identity_gb | leave_out_2013 | 7418 | 276 | 1.34889 | 0.877122 | 2.07441 | 0.169544 |
| identity_gb | cycle_2013 | 1546 | 57 | 1.20891 | 0.601015 | 2.43166 | 0.565169 |
| identity_gb | leave_out_2015 | 7605 | 272 | 1.26088 | 0.802638 | 1.98074 | 0.30899 |
| identity_gb | cycle_2015 | 1357 | 61 | 1.3952 | 0.676755 | 2.87633 | 0.335678 |
| msm_ever | exclude_2015_2016 | 7718 | 413 | 1.44802 | 1.04848 | 1.99981 | 0.0252955 |
| msm_ever | direct_behavior_2009_2016 | 6261 | 336 | 1.42935 | 1.02253 | 1.99803 | 0.0370937 |
| msm_ever | us_born_only | 6562 | 405 | 1.64729 | 1.16227 | 2.33472 | 0.00560256 |
| msm_ever | add_income | 8526 | 473 | 1.56895 | 1.16199 | 2.11842 | 0.00378503 |
| msm_ever | age_decade_categories | 9161 | 498 | 1.5457 | 1.16628 | 2.04855 | 0.00288603 |
| msm_ever | identity_behavior_common_sample | 8936 | 471 | 1.49505 | 1.11829 | 1.99875 | 0.00726117 |
| msm_ever | sexually_experienced | 8617 | 498 | 1.5356 | 1.15234 | 2.04633 | 0.00391646 |
| msm_ever | leave_out_2005 | 7825 | 419 | 1.50693 | 1.09952 | 2.0653 | 0.0116044 |
| msm_ever | cycle_2005 | 1336 | 79 | 2.01969 | 0.94149 | 4.33266 | 0.0678527 |
| msm_ever | leave_out_2007 | 7597 | 415 | 1.48963 | 1.10831 | 2.00215 | 0.00906619 |
| msm_ever | cycle_2007 | 1565 | 83 | 1.682 | 0.784137 | 3.60796 | 0.164815 |
| msm_ever | leave_out_2009 | 7460 | 417 | 1.46547 | 1.0766 | 1.99481 | 0.015973 |
| msm_ever | cycle_2009 | 1704 | 81 | 2.29254 | 1.21239 | 4.33503 | 0.0146472 |
| msm_ever | leave_out_2011 | 7617 | 419 | 1.7545 | 1.30179 | 2.36464 | 0.00037476 |
| msm_ever | cycle_2011 | 1546 | 79 | 1.21069 | 0.596095 | 2.45895 | 0.571961 |
| msm_ever | leave_out_2013 | 7588 | 407 | 1.62831 | 1.18007 | 2.24681 | 0.0035855 |
| msm_ever | cycle_2013 | 1575 | 91 | 1.67105 | 0.990986 | 2.81782 | 0.0534902 |
| msm_ever | leave_out_2015 | 7718 | 413 | 1.44802 | 1.04848 | 1.99981 | 0.0252955 |
| msm_ever | cycle_2015 | 1443 | 85 | 2.93247 | 1.38846 | 6.19349 | 0.00860765 |
| identity_gay | unadjusted | 8833 | 196 | 1.87919 | 1.25016 | 2.8247 | 0.00277472 |
| identity_gay | full | 8825 | 196 | 1.5152 | 0.949944 | 2.41681 | 0.0803095 |
| identity_bi | unadjusted | 8774 | 137 | 1.04194 | 0.609028 | 1.78258 | 0.879564 |
| identity_bi | full | 8766 | 137 | 0.938696 | 0.493296 | 1.78625 | 0.845282 |

## Specific sexual practices

[Implementation](../src/frequentist/behavior.py); exact local record: `outputs/frequentist/behavior_extension/main_results.csv`.

| outcome | model | n | events | odds_ratio | ci_low | ci_high | p_value | status | population | sample | p_holm_family | p_holm_all_eight |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| anal_lifetime | full | 6259 | 253 | 1.56413 | 1.09436 | 2.23556 | 0.0151831 | estimated | all_men | available_for_model | 0.0607323 | 0.106282 |
| oral_lifetime | full | 6261 | 283 | 1.48566 | 1.02138 | 2.16099 | 0.0388359 | estimated | all_men | available_for_model | 0.116508 | 0.194179 |
| anal_year | full | 6261 | 124 | 2.15791 | 1.23439 | 3.77237 | 0.00797616 | estimated | all_men | available_for_model | 0.0319047 | 0.0638093 |
| oral_year | full | 6261 | 146 | 1.88024 | 1.12432 | 3.14438 | 0.0171672 | estimated | all_men | available_for_model | 0.0515016 | 0.106282 |
| anal_lifetime | full | 334 | 253 | 1.72596 | 0.634112 | 4.6978 | 0.275469 | estimated | lifetime_msm | available_for_model | 0.550938 | 0.550938 |
| oral_lifetime | full | 336 | 283 | 1.37403 | 0.538977 | 3.50287 | 0.494863 | estimated | lifetime_msm | available_for_model | 0.550938 | 0.550938 |
| anal_year | full | 336 | 124 | 2.54421 | 1.00624 | 6.43287 | 0.0485669 | estimated | lifetime_msm | available_for_model | 0.0971338 | 0.194268 |
| oral_year | full | 336 | 146 | 1.84995 | 0.778646 | 4.39522 | 0.157705 | estimated | lifetime_msm | available_for_model | 0.157705 | 0.473114 |

## Identity subgroups

[Implementation](../src/frequentist/identity.py); exact local record: `outputs/frequentist/identity_subgroups/models.csv`.

| outcome | model | n | events | odds_ratio | ci_low | ci_high | p_value | status | group | period | sample |
|---|---|---|---|---|---|---|---|---|---|---|---|
| msm_ever | unadjusted | 8612 | 184 | 1.87939 | 1.2218 | 2.8909 | 0.00452735 | estimated | heterosexual | 2005_2016 | available |
| msm_ever | age_cycle | 8612 | 184 | 1.8664 | 1.21586 | 2.86501 | 0.00481131 | estimated | heterosexual | 2005_2016 | available |
| msm_ever | demographic | 8608 | 184 | 1.84801 | 1.15895 | 2.94676 | 0.0105567 | estimated | heterosexual | 2005_2016 | available |
| msm_ever | full | 8604 | 184 | 1.7515 | 1.13958 | 2.69201 | 0.0112733 | estimated | heterosexual | 2005_2016 | available |
| msm_ever | unadjusted | 8604 | 184 | 1.87891 | 1.22123 | 2.89076 | 0.00456188 | estimated | heterosexual | 2005_2016 | fixed_complete |
| msm_ever | age_cycle | 8604 | 184 | 1.86573 | 1.21497 | 2.86504 | 0.0048697 | estimated | heterosexual | 2005_2016 | fixed_complete |
| msm_ever | demographic | 8604 | 184 | 1.84715 | 1.15818 | 2.94598 | 0.0106456 | estimated | heterosexual | 2005_2016 | fixed_complete |
| msm_ever | full | 8604 | 184 | 1.7515 | 1.13958 | 2.69201 | 0.0112733 | estimated | heterosexual | 2005_2016 | fixed_complete |
| msm_ever | unadjusted | 332 | 287 | 2.43859 | 1.10055 | 5.40341 | 0.0287831 | estimated | gay_bisexual | 2005_2016 | available |
| msm_ever | age_cycle | 332 | 287 | 2.07195 | 0.816942 | 5.25492 | 0.122096 | estimated | gay_bisexual | 2005_2016 | available |
| msm_ever | demographic | 332 | 287 | 1.73272 | 0.4637 | 6.4747 | 0.404359 | estimated | gay_bisexual | 2005_2016 | available |
| msm_ever | full | 332 | 287 | 1.48078 | 0.408319 | 5.3701 | 0.541235 | estimated | gay_bisexual | 2005_2016 | available |
| msm_ever | unadjusted | 332 | 287 | 2.43859 | 1.10055 | 5.40341 | 0.0287831 | estimated | gay_bisexual | 2005_2016 | fixed_complete |
| msm_ever | age_cycle | 332 | 287 | 2.07195 | 0.816942 | 5.25492 | 0.122096 | estimated | gay_bisexual | 2005_2016 | fixed_complete |
| msm_ever | demographic | 332 | 287 | 1.73272 | 0.4637 | 6.4747 | 0.404359 | estimated | gay_bisexual | 2005_2016 | fixed_complete |
| msm_ever | full | 332 | 287 | 1.48078 | 0.408319 | 5.3701 | 0.541235 | estimated | gay_bisexual | 2005_2016 | fixed_complete |
| msm_ever | unadjusted | 5866 | 126 | 1.97702 | 1.16814 | 3.34601 | 0.0119662 | estimated | heterosexual | 2009_2016 | available |
| msm_ever | age_cycle | 5866 | 126 | 1.93076 | 1.13583 | 3.28203 | 0.0159878 | estimated | heterosexual | 2009_2016 | available |
| msm_ever | demographic | 5863 | 126 | 1.68936 | 0.931764 | 3.06295 | 0.0828 | estimated | heterosexual | 2009_2016 | available |
| msm_ever | full | 5859 | 126 | 1.62358 | 0.948431 | 2.77934 | 0.0761493 | estimated | heterosexual | 2009_2016 | available |
| msm_ever | unadjusted | 5859 | 126 | 1.97568 | 1.16697 | 3.34483 | 0.012097 | estimated | heterosexual | 2009_2016 | fixed_complete |
| msm_ever | age_cycle | 5859 | 126 | 1.92915 | 1.13421 | 3.28122 | 0.0162277 | estimated | heterosexual | 2009_2016 | fixed_complete |
| msm_ever | demographic | 5859 | 126 | 1.68833 | 0.930982 | 3.06178 | 0.0832632 | estimated | heterosexual | 2009_2016 | fixed_complete |
| msm_ever | full | 5859 | 126 | 1.62358 | 0.948431 | 2.77934 | 0.0761493 | estimated | heterosexual | 2009_2016 | fixed_complete |
| msm_ever | unadjusted | 223 | 191 | 3.10408 | 1.21779 | 7.91213 | 0.0189722 | estimated | gay_bisexual | 2009_2016 | available |
| msm_ever | age_cycle | 223 | 191 | 2.7749 | 0.949793 | 8.10712 | 0.0613751 | estimated | gay_bisexual | 2009_2016 | available |
| msm_ever | demographic | 223 | 191 | 2.28254 | 0.536542 | 9.71032 | 0.25149 | estimated | gay_bisexual | 2009_2016 | available |
| msm_ever | full | 223 | 191 | 1.85749 | 0.457972 | 7.53377 | 0.370448 | estimated | gay_bisexual | 2009_2016 | available |
| msm_ever | unadjusted | 223 | 191 | 3.10408 | 1.21779 | 7.91213 | 0.0189722 | estimated | gay_bisexual | 2009_2016 | fixed_complete |
| msm_ever | age_cycle | 223 | 191 | 2.7749 | 0.949793 | 8.10712 | 0.0613751 | estimated | gay_bisexual | 2009_2016 | fixed_complete |
| msm_ever | demographic | 223 | 191 | 2.28254 | 0.536542 | 9.71032 | 0.25149 | estimated | gay_bisexual | 2009_2016 | fixed_complete |
| msm_ever | full | 223 | 191 | 1.85749 | 0.457972 | 7.53377 | 0.370448 | estimated | gay_bisexual | 2009_2016 | fixed_complete |

## Identity interactions

[Implementation](../src/frequentist/identity.py); exact local record: `outputs/frequentist/identity_subgroups/interactions.csv`.

| test | n | events | odds_ratio | ci_low | ci_high | p_value | status | period |
|---|---|---|---|---|---|---|---|---|
| interaction_GB_vs_heterosexual | 8936 | 471 | 1.31695 | 0.506236 | 3.42601 | 0.567909 | estimated | 2005_2016 |
| interaction_GB_vs_heterosexual | 6082 | 317 | 1.68726 | 0.563712 | 5.05019 | 0.34185 | estimated | 2009_2016 |

## Identity focal family

[Implementation](../src/frequentist/identity.py); exact local record: `outputs/frequentist/identity_subgroups/focal_tests.csv`.

| outcome | model | n | events | odds_ratio | ci_low | ci_high | p_value | status | group | period | sample | test | p_holm_three |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| msm_ever | full | 8604 | 184 | 1.7515 | 1.13958 | 2.69201 | 0.0112733 | estimated | heterosexual | 2005_2016 | available | heterosexual | 0.0338199 |
| msm_ever | full | 332 | 287 | 1.48078 | 0.408319 | 5.3701 | 0.541235 | estimated | gay_bisexual | 2005_2016 | available | gay_bisexual | 1 |
| msm_ever | full | 5859 | 126 | 1.62358 | 0.948431 | 2.77934 | 0.0761493 | estimated | heterosexual | 2009_2016 | available | heterosexual | 0.228448 |
| msm_ever | full | 223 | 191 | 1.85749 | 0.457972 | 7.53377 | 0.370448 | estimated | gay_bisexual | 2009_2016 | available | gay_bisexual | 0.6837 |
| unavailable | unavailable | 8936 | 471 | 1.31695 | 0.506236 | 3.42601 | 0.567909 | estimated | unavailable | 2005_2016 | unavailable | interaction_GB_vs_heterosexual | 1 |
| unavailable | unavailable | 6082 | 317 | 1.68726 | 0.563712 | 5.05019 | 0.34185 | estimated | unavailable | 2009_2016 | unavailable | interaction_GB_vs_heterosexual | 0.6837 |

## Explanatory contrasts

[Implementation](../src/frequentist/explanations.py); exact local record: `outputs/frequentist/explanations/focal_tests.csv`.

| era | test | comparison | status | scale | n | estimate | p_value | ci_low | ci_high | p_holm | failed_test_placeholder_for_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2009-2016 | 1 | Reduction in adjusted prevalence difference | estimated | identity | 6178 | 0.000510631 | 0.192141 | -0.00026586 | 0.00128712 | 0.384607 | False |
| 2009-2016 | 2 | Male versus female oral prevalence-ratio contrast | estimated | ratio | 5844 | 1.76267 | 0.128202 | 0.84415 | 3.68064 | 0.384607 | False |
| 2009-2016 | 3 | female_multiple | estimated | ratio | 5819 | 1.33102 | 0.0220496 | 1.04392 | 1.69709 | 0.110248 | False |
| 2009-2016 | 4 | male_multiple_conditional | estimated | ratio | 126 | 4.95468 | 0.0835922 | 0.765314 | 32.0768 | 0.334369 | False |
| 2009-2016 | 5 | male_recent_conditional | not_estimable | ratio | 126 | 1.61717 | unavailable | unavailable | unavailable | 1 | True |
| 2009-2014 | 1 | Reduction in adjusted prevalence difference | estimated | identity | 4754 | 0.0015396 | 0.0789972 | -0.000188803 | 0.003268 | 0.315989 | False |
| 2009-2014 | 2 | Male versus female oral prevalence-ratio contrast | estimated | ratio | 4549 | 1.15853 | 0.697817 | 0.539808 | 2.4864 | 1 | False |
| 2009-2014 | 3 | female_multiple | estimated | ratio | 4526 | 1.44402 | 0.0116994 | 1.09112 | 1.91105 | 0.058497 | False |
| 2009-2014 | 4 | male_multiple_conditional | estimated | ratio | 95 | 5.10933 | 0.198503 | 0.21778 | 119.87 | 0.595508 | False |
| 2009-2014 | 5 | male_recent_conditional | not_estimable | ratio | 95 | unavailable | unavailable | unavailable | unavailable | 1 | True |

## Optional Maloney supplement

The separate unweighted Maloney analysis is retained as a separate research artifact outside the NHANES manuscript. Run `python scripts/reproduce.py --with-maloney`. Its primary eligible sample and manuscript-exclusion sensitivity are both validated against frozen pre-refactor records. Results are written to `outputs/frequentist/maloney/`; [implementation](../src/frequentist/maloney.py), [methods](methods.md#separate-maloney-supplement). It is not pooled with NHANES.
