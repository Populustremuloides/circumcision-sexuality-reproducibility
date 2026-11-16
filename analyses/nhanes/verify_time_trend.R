library(survey)
options(survey.lonely.psu='fail')
here<-'outputs/time_trend'
p<-read.csv(file.path(here,'tests.csv'));cc<-read.csv(file.path(here,'cycle_estimates.csv'));results<-list()
for(label in unique(p$period)) {
 d<-read.csv(gzfile(file.path(here,paste0(label,'_validation.csv.gz'))))
 d$complete<-tolower(as.character(d$complete))=='true'
 des<-svydesign(ids=~psu,strata=~stratum,weights=~weight,nest=TRUE,data=d)
 sd<-subset(des,complete)
 for(kind in c('linear','categorical')) {
 formula<-if(kind=='linear') msm_ever~circ+age10+I(age10^2)+factor(cycle)+factor(race)+factor(education)+foreign_born+circ:trend10 else msm_ever~circ+age10+I(age10^2)+factor(cycle)+factor(race)+factor(education)+foreign_born+circ:factor(cycle)
 fit<-svyglm(formula,design=sd,family=quasibinomial(),control=glm.control(epsilon=1e-12,maxit=100))
 df<-degf(sd)-fit$rank+1
 ref<-subset(p,period==label & test==if(kind=='linear') 'linear_trend' else 'categorical_heterogeneity')
 stopifnot(fit$converged,df==ref$df2,nobs(fit)==ref$n)
 if(kind=='linear') {
 b<-coef(fit)['circ:trend10'];se<-sqrt(vcov(fit)['circ:trend10','circ:trend10'])
 vals<-c(b,se,exp(b),exp(b-qt(.975,df)*se),exp(b+qt(.975,df)*se),2*pt(-abs(b/se),df))
 expected<-as.numeric(ref[,c('beta','se','ratio_OR_per_decade','low','high','p')])
 } else {
  test<-regTermTest(fit,~circ:factor(cycle),method='Wald',df=df)
  vals<-c(as.numeric(test$Ftest),as.numeric(test$p));expected<-as.numeric(ref[,c('statistic','p')])
  for(cy in levels(factor(d$cycle))) {
   a<-rep(0,length(coef(fit)));a[which(names(coef(fit))=='circ')]<-1
   term<-paste0('circ:factor(cycle)',cy);if(term %in% names(coef(fit))) a[which(names(coef(fit))==term)]<-1
   b<-sum(a*coef(fit));se<-sqrt(as.numeric(t(a)%*%vcov(fit)%*%a));row<-subset(cc,period==label & cycle==cy)
   stopifnot(max(abs(c(exp(b),exp(b-qt(.975,df)*se),exp(b+qt(.975,df)*se))-as.numeric(row[,c('OR','low','high')])))<1e-6)
  }
 }
 delta<-max(abs(vals-expected));stopifnot(delta<1e-6)
 results[[paste(label,kind)]]<-data.frame(period=label,model=kind,n=nobs(fit),df=df,max_difference=delta,passed=TRUE)
 }
}
z<-do.call(rbind,results);write.csv(z,file.path(here,'r_validation.csv'),row.names=FALSE);print(z)
capture.output(sessionInfo(),file=file.path(here,'r_session_info.txt'))
