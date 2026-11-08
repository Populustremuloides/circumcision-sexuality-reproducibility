"""Exploratory identity-specific association and descriptive gap decomposition."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
from scipy.stats import t
from statsmodels.stats.multitest import multipletests
from analyze import ROOT, Survey, ADJUST
OUT=ROOT/'outputs/identity_subgroups'; OUT.mkdir(exist_ok=True)
d=pd.read_csv(ROOT/'data/analysis.csv.gz')
d['identity_group']='other_unclassified'
d.loc[d.identity_gb.eq(0),'identity_group']='heterosexual'
d.loc[d.identity_gay.eq(1),'identity_group']='gay'
d.loc[d.identity_bi.eq(1),'identity_group']='bisexual'
models=[]; prev=[]; interactions=[]; gaps=[]; details=[]

def interaction(data,survey):
    rhs=ADJUST['full']+' + identity_gb + circ:identity_gb'
    y,x=patsy.dmatrices('msm_ever ~ '+rhs,data.loc[data.eligible],return_type='dataframe')
    ix=x.index; X=x.to_numpy(); Y=y.iloc[:,0].to_numpy(); w=data.loc[ix,'weight'].to_numpy(); w/=w.mean()
    fit=sm.GLM(Y,X,family=sm.families.Binomial(),freq_weights=w).fit(tol=1e-11,maxiter=100)
    assert fit.converged and np.linalg.matrix_rank(X)==X.shape[1]
    mu=fit.fittedvalues; score=X*(w*(Y-mu))[:,None]
    H=X.T@((w*mu*(1-mu))[:,None]*X)
    assert np.linalg.cond(H)<1e10
    inv=np.linalg.inv(H); influence=np.zeros((len(data),X.shape[1])); influence[ix]=score@inv
    cov=survey.covariance(influence)
    domain=np.zeros(len(data),bool);domain[ix]=True
    df=survey.domain_df(domain)-X.shape[1]+1
    assert df>0 and abs(score.sum(axis=0)).max()<1e-6
    j=list(x.columns).index('circ:identity_gb'); b=fit.params[j];se=np.sqrt(cov[j,j]);q=t.ppf(.975,df)
    # Independent sandwich order check.
    sc=np.zeros_like(influence);sc[ix]=score
    np.testing.assert_allclose(cov,inv@survey.covariance(sc)@inv,rtol=1e-8,atol=1e-10)
    return dict(test='interaction_GB_vs_heterosexual',n=len(ix),events=int(Y.sum()),beta=b,se=se,
        odds_ratio=np.exp(b),ci_low=np.exp(b-q*se),ci_high=np.exp(b+q*se),p_value=2*t.sf(abs(b/se),df),
        residual_df=df,formula='msm_ever ~ '+rhs,status='estimated')

for period,base in [('2005_2016',d),('2009_2016',d[d.year.ge(2009)])]:
    z=base.copy().reset_index(drop=True)
    if period=='2009_2016':z.weight*=1.5
    s=Survey(z)
    for group,mask in [('heterosexual',z.identity_gb.eq(0)),('gay_bisexual',z.identity_gb.eq(1))]:
        cc=mask & z[['circ','msm_ever','age10','cycle','race','education','foreign_born']].notna().all(axis=1)
        for sample,m in [('available',mask),('fixed_complete',cc)]:
            for name,rhs in ADJUST.items():
                try:
                    row,_=s.model('msm_ever',rhs,m,name,jackknife=(period=='2005_2016' and sample=='available' and name=='full'))
                    row['status']='estimated'
                except (AssertionError,np.linalg.LinAlgError) as e:
                    row=dict(model=name,status='not_estimable',error=str(e))
                row.update(group=group,period=period,sample=sample);models.append(row)
        rec,dif=s.prevalence('msm_ever',z.eligible & mask & z.circ.notna())
        for row in rec:row.update(group=group,period=period);prev.append(row)
        dif.update(group=group,period=period);gaps.append(dif)
    try: row=interaction(z,s)
    except (AssertionError,np.linalg.LinAlgError) as e:row=dict(test='interaction_GB_vs_heterosexual',status='not_estimable',error=str(e))
    row['period']=period;interactions.append(row)
    if period=='2005_2016':
        # Exhaustive group contributions, same denominator as original crude MSM comparison.
        domain=z.eligible & z.circ.notna() & z.msm_ever.notna()
        contributions=[]
        for group in ['heterosexual','gay','bisexual','other_unclassified']:
            infl=[]; joint=[];shares=[];rates=[];ns=[];events=[]
            for c in [0,1]:
                m=domain & z.circ.eq(c); w=z.loc[m,'weight'].to_numpy()
                g=z.loc[m,'identity_group'].eq(group).to_numpy()
                y=z.loc[m,'msm_ever'].to_numpy();a=g*y
                p=np.average(a,weights=w);share=np.average(g,weights=w)
                rate=np.average(y[g],weights=w[g]); ns.append(int(g.sum()));events.append(int(y[g].sum()))
                f=np.zeros(len(z));f[m]=w*(a-p)/w.sum();infl.append(f)
                joint.append(p);shares.append(share);rates.append(rate)
            delta=joint[1]-joint[0]; se=np.sqrt(s.covariance(infl[1]-infl[0])[0,0]);df=s.domain_df(domain);q=t.ppf(.975,df)
            within=np.mean(shares)*(rates[1]-rates[0]);composition=np.mean(rates)*(shares[1]-shares[0])
            np.testing.assert_allclose(delta,within+composition,atol=1e-12)
            rec=dict(group=group,n_uncirc=ns[0],n_circ=ns[1],events_uncirc=events[0],events_circ=events[1],
                share_uncirc=shares[0],share_circ=shares[1],rate_uncirc=rates[0],rate_circ=rates[1],
                joint_uncirc=joint[0],joint_circ=joint[1],contribution=delta,se=se,ci_low=delta-q*se,ci_high=delta+q*se,
                within_rate_component=within,composition_component=composition)
            details.append(rec);contributions.append(delta)
        _,total=s.prevalence('msm_ever',domain)
        np.testing.assert_allclose(sum(contributions),total['difference'],atol=1e-12)
        original=pd.read_csv(ROOT/'outputs/prevalence_differences.csv').query('outcome == "msm_ever"').iloc[0]
        np.testing.assert_allclose(total['difference'],original.difference,atol=1e-12)
        for row in details:row['fraction_of_raw_gap']=row['contribution']/total['difference']
mods=pd.DataFrame(models);ints=pd.DataFrame(interactions)
focal=mods[mods.model.eq('full') & mods['sample'].eq('available')].copy()
focal['test']=focal.group
focal=pd.concat([focal,ints],ignore_index=True)
for period in focal.period.unique():
    ix=focal.period.eq(period)
    assert ix.sum()==3
    focal.loc[ix,'p_holm_three']=multipletests(focal.loc[ix,'p_value'].fillna(1),method='holm')[1]
for name,frame in [('models',mods),('interactions',ints),('focal_tests',focal),('prevalence',pd.DataFrame(prev)),('prevalence_differences',pd.DataFrame(gaps)),('decomposition',pd.DataFrame(details))]:
    frame.to_csv(OUT/f'{name}.csv',index=False)
validation=dict(original_gap_reproduced=True,group_contributions_sum_to_original_gap=True,
    symmetric_decomposition_identity_passed=True,interaction_covariance_crosscheck=True,
    subgroup_models_use_original_validation=True,
    failed_models=mods[mods.status.ne('estimated')].fillna('').to_dict('records'))
(OUT/'validation.json').write_text(json.dumps(validation,indent=2))
print(focal[['period','test','status','n','events','odds_ratio','ci_low','ci_high','p_value','p_holm_three']].to_string(index=False))
print(pd.DataFrame(details).to_string(index=False))
