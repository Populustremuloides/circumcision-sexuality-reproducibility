"""NHANES 2005–2016 circumcision, sexual identity, and male–male behavior.

GLM point estimates use statsmodels. Its model-based covariance is NOT used.
Survey variance is calculated explicitly from stratified PSU score totals with
zero contributions for observations outside the analysis domain.
"""
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import pyreadstat
from bs4 import BeautifulSoup
from scipy.special import expit, logit
from scipy.stats import t
import scipy
import statsmodels
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
RAW, OUT = ROOT / 'data/raw', ROOT / 'outputs/frequentist'
OUT.mkdir(exist_ok=True)
CYCLES = list(zip(range(2005, 2017, 2), 'DEFGHI'))
from src.specification import ADJUST

class Survey:
    def __init__(self, data):
        self.data = data
        self.units = data[['stratum', 'psu']].drop_duplicates().sort_values(['stratum','psu']).reset_index(drop=True)
        self.codes = pd.Categorical(data.psu, categories=self.units.psu).codes
        self.strata = list(self.units.groupby('stratum').indices.values())
        assert min(map(len, self.strata)) >= 2
        self.design_df = len(self.units) - len(self.strata)

    def covariance(self, influence):
        influence = np.asarray(influence)
        if influence.ndim == 1:
            influence = influence[:,None]
        totals = np.zeros((len(self.units), influence.shape[1]))
        np.add.at(totals, self.codes, influence)
        covariance = np.zeros((influence.shape[1], influence.shape[1]))
        for ids in self.strata:
            centered = totals[ids] - totals[ids].mean(axis=0)
            covariance += len(ids) / (len(ids)-1) * centered.T @ centered
        return covariance

    def domain_df(self, mask):
        units = self.data.loc[mask, ['stratum','psu']].drop_duplicates()
        return len(units) - units.stratum.nunique()

    def model(self, outcome, rhs, mask, label, jackknife=False):
        mask = np.asarray(mask) & self.data.eligible.to_numpy()
        y, x = patsy.dmatrices(f'{outcome} ~ {rhs}', self.data.loc[mask], return_type='dataframe')
        idx = x.index.to_numpy()
        w = self.data.loc[idx,'weight'].to_numpy()
        w = w / w.mean()
        X, Y = x.to_numpy(), y.iloc[:,0].to_numpy()
        fit = sm.GLM(Y, X, family=sm.families.Binomial(), freq_weights=w).fit(tol=1e-11, maxiter=100)
        assert fit.converged and np.linalg.matrix_rank(X) == X.shape[1]
        residual_score = X * (w * (Y-fit.fittedvalues))[:,None]
        bread = X.T @ ((w * fit.fittedvalues * (1-fit.fittedvalues))[:,None] * X)
        assert np.linalg.cond(bread) < 1e10, (label, 'unstable information matrix', np.linalg.cond(bread))
        inv = np.linalg.inv(bread)
        influence = np.zeros((len(self.data), X.shape[1]))
        influence[idx] = residual_score @ inv
        covariance = self.covariance(influence)
        j = list(x.columns).index('circ')
        beta, se = fit.params[j], np.sqrt(covariance[j,j])
        domain = np.zeros(len(self.data), dtype=bool)
        domain[idx] = True
        ddf = self.domain_df(domain)
        df = ddf - X.shape[1] + 1
        assert df > 0
        critical = t.ppf(.975, df)
        row = dict(outcome=outcome, model=label, n=len(idx), events=int(Y.sum()),
                   n_circ=int(self.data.loc[idx,'circ'].eq(1).sum()),
                   n_uncirc=int(self.data.loc[idx,'circ'].eq(0).sum()),
                   events_circ=int(Y[self.data.loc[idx,'circ'].eq(1)].sum()),
                   events_uncirc=int(Y[self.data.loc[idx,'circ'].eq(0)].sum()),
                   beta=beta, se=se, odds_ratio=np.exp(beta),
                   ci_low=np.exp(beta-critical*se), ci_high=np.exp(beta+critical*se),
                   p_value=2*t.sf(abs(beta/se),df), design_df=ddf, residual_df=df,
                   parameters=X.shape[1], max_abs_score=float(np.max(abs(residual_score.sum(axis=0)))),
                   kish_n=float(w.sum()**2/(w*w).sum()), formula=f'{outcome} ~ {rhs}')
        assert row['max_abs_score'] < 1e-6
        # Independent survey sandwich using PSU score totals before the bread.
        score_frame = pd.DataFrame(residual_score, index=idx)
        score_frame['psu'] = self.data.loc[idx,'psu']
        totals = score_frame.groupby('psu').sum().reindex(self.units.psu, fill_value=0).to_numpy()
        meat = np.zeros_like(bread)
        for ids in self.strata:
            a = totals[ids]
            meat += len(ids)/(len(ids)-1) * (a.T@a - np.outer(a.sum(axis=0), a.sum(axis=0))/len(ids))
        np.testing.assert_allclose(covariance, inv @ meat @ inv, rtol=1e-8, atol=1e-11)
        if label == 'unadjusted':
            c = self.data.loc[idx,'circ'].to_numpy()
            cells = [w[(c==a) & (Y==b)].sum() for a,b in [(1,1),(1,0),(0,1),(0,0)]]
            direct = cells[0]*cells[3]/(cells[1]*cells[2])
            np.testing.assert_allclose(row['odds_ratio'],direct,rtol=1e-8)
        if jackknife:
            # JKn deletes each PSU and upweights other PSUs within its stratum.
            # Center on the full estimate (mse=TRUE), retaining all other strata.
            codes = self.codes[idx]
            variance = 0.
            for ids in self.strata:
                h = np.isin(codes, ids)
                for deleted in ids:
                    rw = w.copy()
                    rw[h] *= len(ids)/(len(ids)-1)
                    rw[codes == deleted] = 0
                    rf = sm.GLM(Y, X, family=sm.families.Binomial(), freq_weights=rw).fit(
                        start_params=fit.params, tol=1e-10, maxiter=80)
                    assert rf.converged
                    variance += (len(ids)-1)/len(ids) * (rf.params[j]-beta)**2
            row['jackknife_se'] = np.sqrt(variance)
            row['jackknife_taylor_se_ratio'] = np.sqrt(variance)/se
        return row, domain

    def prevalence(self, outcome, mask):
        records, influences = [], []
        for c in [0,1]:
            m = mask & self.data.circ.eq(c) & self.data[outcome].notna()
            w = self.data.loc[m,'weight'].to_numpy()
            y = self.data.loc[m,outcome].to_numpy()
            p = np.average(y,weights=w)
            influence = np.zeros(len(self.data))
            influence[m] = w*(y-p)/w.sum()
            se = np.sqrt(self.covariance(influence)[0,0])
            df = self.domain_df(m)
            limits = expit(logit(p) + np.array([-1,1])*t.ppf(.975,df)*se/(p*(1-p)))
            records.append(dict(outcome=outcome, circ=c, n=len(y), events=int(y.sum()),
                                prevalence=p, se=se, ci_low=limits[0], ci_high=limits[1],
                                kish_n=w.sum()**2/(w*w).sum(), design_df=df))
            influences.append(influence)
        delta = records[1]['prevalence'] - records[0]['prevalence']
        se = np.sqrt(self.covariance(influences[1]-influences[0])[0,0])
        df = self.domain_df(mask & self.data[outcome].notna() & self.data.circ.notna())
        diff = dict(outcome=outcome, difference=delta, se=se,
                    ci_low=delta-t.ppf(.975,df)*se,ci_high=delta+t.ppf(.975,df)*se,
                    p_value=2*t.sf(abs(delta/se),df))
        return records, diff

