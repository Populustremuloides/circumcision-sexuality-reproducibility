# Independent R survey implementation for reproducing the executed Python models.
# Executed verification is recorded in outputs/r_survey_reference_*.
# Run from the project directory after python scripts/reproduce.py generates data/analysis.csv.gz.
library(survey)
options(survey.lonely.psu = 'fail')
d <- read.csv(gzfile('data/analysis.csv.gz'), na.strings=c('', 'NA'))
d$eligible <- tolower(as.character(d$eligible)) == 'true'
des <- svydesign(ids=~psu, strata=~stratum, weights=~weight, nest=TRUE, data=d)
formulas <- c(
  unadjusted='circ',
  age_cycle='circ + age10 + I(age10^2) + factor(cycle)',
  demographic='circ + age10 + I(age10^2) + factor(cycle) + factor(race) + factor(education)',
  full='circ + age10 + I(age10^2) + factor(cycle) + factor(race) + factor(education) + foreign_born'
)
results <- list()
for (outcome in c('identity_gb','msm_ever')) {
  for (name in names(formulas)) {
    f <- as.formula(paste(outcome, '~', formulas[[name]]))
    ok <- d$eligible & complete.cases(d[,all.vars(f)])
    subdes <- subset(des, ok)
    # Tight convergence keeps the final IRLS weights accurate enough for the
    # existing 1e-6 cross-software covariance tolerance; do not relax that check.
    fit <- svyglm(f, design=subdes, family=quasibinomial(),
                  control=glm.control(epsilon=1e-12, maxit=100))
    stopifnot(fit$converged)
    b <- coef(fit)['circ']
    se <- sqrt(vcov(fit)['circ','circ'])
    df <- degf(subdes)-fit$rank+1
    results[[length(results)+1]] <- data.frame(
      outcome=outcome,model=name,n=sum(ok),beta=b,se=se,
      odds_ratio=exp(b),ci_low=exp(b-qt(.975,df)*se),
      ci_high=exp(b+qt(.975,df)*se),p_value=2*pt(-abs(b/se),df),residual_df=df)
  }
}
result <- do.call(rbind,results)
write.csv(result,'outputs/frequentist/r_survey_reference_results.csv',row.names=FALSE)
python <- subset(read.csv('outputs/frequentist/models.csv'), sample == 'available_for_model')
comparison <- merge(result,python,by=c('outcome','model'),suffixes=c('_r','_python'))
stopifnot(nrow(result) == 8L, nrow(comparison) == 8L,
          !anyDuplicated(comparison[c('outcome','model')]))
stopifnot(all(comparison$n_r == comparison$n_python),
          all(comparison$residual_df_r == comparison$residual_df_python))
stopifnot(max(abs(comparison$beta_r-comparison$beta_python)) < 1e-6)
stopifnot(max(abs(comparison$se_r-comparison$se_python)) < 1e-6)
fields <- c('beta','se','odds_ratio','ci_low','ci_high','p_value')
checks <- do.call(rbind, lapply(fields, function(field) {
  delta <- abs(comparison[[paste0(field,'_r')]] - comparison[[paste0(field,'_python')]])
  stopifnot(all(is.finite(delta)), max(delta) < 1e-6)
  data.frame(field=field,max_absolute_difference=max(delta),tolerance=1e-6,passed=TRUE)
}))
write.csv(comparison,'outputs/frequentist/r_survey_reference_comparison.csv',row.names=FALSE)
write.csv(checks,'outputs/frequentist/r_survey_reference_checks.csv',row.names=FALSE)
capture.output(sessionInfo(), file='outputs/frequentist/r_survey_reference_session.txt')
print(result)
print(checks)
