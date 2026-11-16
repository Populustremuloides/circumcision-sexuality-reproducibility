library(survey)
options(survey.lonely.psu='fail')
here<-'outputs/pooled';p<-read.csv(file.path(here,'models.csv'));out<-list()
for(label in p$model){
 d<-read.csv(gzfile(file.path(here,paste0(label,'_validation.csv.gz'))));d$complete<-tolower(as.character(d$complete))=='true'
 des<-svydesign(ids=~psu,strata=~stratum,weights=~weight,nest=TRUE,data=d);sd<-subset(des,complete)
 fit<-svyglm(msm_ever~circ+age10+I(age10^2)+factor(cycle)+factor(race)+factor(education)+foreign_born,design=sd,family=quasibinomial(),control=glm.control(epsilon=1e-12,maxit=100))
 b<-coef(fit)['circ'];se<-sqrt(vcov(fit)['circ','circ']);df<-degf(sd)-fit$rank+1
 vals<-c(b,se,exp(b),exp(b-qt(.975,df)*se),exp(b+qt(.975,df)*se),2*pt(-abs(b/se),df))
 ref<-p[p$model==label,];delta<-max(abs(vals-as.numeric(ref[,c('beta','se','odds_ratio','ci_low','ci_high','p_value')])));stopifnot(delta<1e-6,nobs(fit)==ref$n,df==ref$residual_df)
 out[[label]]<-data.frame(model=label,max_difference=delta,passed=TRUE)
}
write.csv(do.call(rbind,out),file.path(here,'pooled_r_validation.csv'),row.names=FALSE);print(do.call(rbind,out))
