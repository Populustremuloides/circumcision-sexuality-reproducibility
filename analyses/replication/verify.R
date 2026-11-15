library(survey)
options(survey.lonely.psu='fail')
d <- read.csv(gzfile('outputs/replication/harmonized.csv.gz'))
d$eligible <- tolower(as.character(d$eligible))=='true'
p <- read.csv('outputs/replication/models.csv')
rows <- list()
for (name in p$model) {
 z <- d
 if(name=='exclude_1999_2000') { z <- subset(z,year>=2001); z$weight <- z$WTMEC2YR/2 }
 f <- if(name=='unadjusted') msm_ever ~ circ else msm_ever ~ circ + age10 + I(age10^2) + factor(cycle) + factor(race) + factor(education) + foreign_born
 ok <- z$eligible & complete.cases(z[,all.vars(f)])
 des <- svydesign(ids=~psu,strata=~stratum,weights=~weight,nest=TRUE,data=z)
 sd <- subset(des,ok)
 fit <- svyglm(f,design=sd,family=quasibinomial(),control=glm.control(epsilon=1e-12,maxit=100))
 b <- coef(fit)['circ'];se <- sqrt(vcov(fit)['circ','circ']);df <- degf(sd)-fit$rank+1
 vals <- c(beta=b,se=se,odds_ratio=exp(b),ci_low=exp(b-qt(.975,df)*se),ci_high=exp(b+qt(.975,df)*se),p_value=2*pt(-abs(b/se),df))
 names(vals)<-c('beta','se','odds_ratio','ci_low','ci_high','p_value')
 ref<-p[p$model==name,];stopifnot(sum(ok)==ref$n,df==ref$residual_df,fit$converged)
 delta <- max(abs(vals-as.numeric(ref[,names(vals)])));stopifnot(delta<1e-6)
 rows[[name]]<-data.frame(model=name,n=sum(ok),max_difference=delta,passed=TRUE)
}
write.csv(do.call(rbind,rows),'outputs/replication/r_checks.csv',row.names=FALSE)
print(do.call(rbind,rows))
