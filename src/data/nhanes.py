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

def codebook_audit(frame, name, variables):
    soup = BeautifulSoup((RAW / f'{name}.htm').read_text(), 'html.parser')
    rows, extracts = [], []
    for var in variables:
        tag = soup.find(id=var)
        assert tag is not None, (name, var)
        section = tag.parent
        extracts.append(section.get_text(' ', strip=True))
        for tr in section.select('table tbody tr'):
            cells = [td.get_text(' ', strip=True) for td in tr.find_all('td')]
            if len(cells) < 3:
                continue
            value, label, count = cells[:3]
            expected = int(count.replace(',', ''))
            if value == '.':
                observed = int(frame[var].isna().sum())
            elif ' to ' in value:
                lo, hi = map(float, value.split(' to '))
                observed = int(frame[var].between(lo, hi).sum())
            else:
                observed = int(frame[var].eq(float(value)).sum())
            rows.append(dict(file=name, variable=var, code=value, label=label,
                             expected=expected, observed=observed, passed=expected == observed))
            # Record discrepancies rather than silently editing source microdata.
            # Check analysis-critical discrepancies after all files are audited.
    return rows, extracts


def harmonize():
    frames, audit, extracts, routing, parser_checks = [], [], [], [], []
    for year, suffix in CYCLES:
        imported = {}
        for component in ['DEMO','SXQ']:
            path = RAW / f'{component}_{suffix}.XPT'
            frame, _ = pyreadstat.read_xport(str(path))
            alternate = pd.read_sas(path)
            assert list(frame.columns) == list(alternate.columns)
            # pandas' XPORT reader in this runtime decodes IBM floating zero
            # as 16**(-65). ReadStat reads the original bytes correctly.
            # Verify agreement after canonicalizing ONLY these tiny values.
            tiny = alternate.abs().lt(1e-70) & alternate.ne(0)
            canonical = alternate.mask(tiny,0.)
            np.testing.assert_allclose(frame.to_numpy(),canonical.to_numpy(),equal_nan=True,rtol=1e-12,atol=1e-12)
            parser_checks.append(dict(file=path.name,pandas_tiny_zeros=int(tiny.sum().sum()),
                                      agreement_after_zero_correction=True))
            imported[component] = frame
        demo, sxq = imported['DEMO'], imported['SXQ']
        assert demo.SEQN.is_unique and sxq.SEQN.is_unique
        assert set(sxq.SEQN).issubset(set(demo.SEQN))
        identity = 'SXQ296' if suffix == 'I' else 'SXQ292'
        birthplace = 'DMDBORN' if suffix == 'D' else ('DMDBORN2' if suffix in 'EF' else 'DMDBORN4')
        sv = ['SXQ280', identity, 'SXQ410', 'SXQ021' if suffix in 'DE' else 'SXQ809']
        av, ex = codebook_audit(sxq, f'SXQ_{suffix}', sv)
        audit += av
        extracts += [f'\n{year} SEXUAL BEHAVIOR\n'] + ex
        av, ex = codebook_audit(demo, f'DEMO_{suffix}', [birthplace, 'DMDEDUC2', 'RIDRETH1'])
        audit += av
        extracts += [f'\n{year} DEMOGRAPHICS\n'] + ex
        d = demo.merge(sxq, on='SEQN', how='left', validate='one_to_one', indicator=True)
        d['sxq_record'] = d['_merge'].eq('both')
        d['cycle'] = f'{year}-{year+1}'
        d['year'] = year
        d['weight'] = d.WTMEC2YR / 6
        d['stratum'] = d.cycle + '_' + d.SDMVSTRA.astype(int).astype(str)
        d['psu'] = d.stratum + '_' + d.SDMVPSU.astype(int).astype(str)
        d['eligible'] = d.RIAGENDR.eq(1) & d.RIDAGEYR.between(20, 59) & d.weight.gt(0)
        d['circ'] = d.SXQ280.map({1: 1., 2: 0.})
        gaycode, straightcode = (1, 2) if suffix == 'I' else (2, 1)
        d['identity_raw'] = d[identity]
        d['identity_gb'] = d[identity].map({straightcode: 0., gaycode: 1., 3: 1.})
        d['identity_gay'] = d[identity].map({straightcode: 0., gaycode: 1.})
        d['identity_bi'] = d[identity].map({straightcode: 0., 3: 1.})
        d['sex_ever'] = d['SXQ021' if suffix in 'DE' else 'SXD021'].map({1: 1., 2: 0.})
        if suffix in 'DE':
            count = d.SXQ410.where(d.SXQ410.between(0, 2000))
            assert (count.dropna() == count.dropna().round()).all()
            d['msm_ever'] = (count >= 1).astype(float).where(count.notna())
            conflict = d.sex_ever.eq(0) & count.gt(0)
            assert not conflict.any()
            d.loc[d.sex_ever.eq(0), 'msm_ever'] = 0.
            routing.append(dict(cycle=d.cycle.iloc[0], never_sex_coded_no=int((d.eligible & d.sex_ever.eq(0)).sum()),
                                inconsistent_never_sex_positive_count=int(conflict.sum())))
        else:
            d['msm_ever'] = d.SXQ809.map({1: 1., 2: 0.})
            conflict = d.SXQ809.eq(2) & d.SXQ410.between(1, 2000)
            assert not conflict.any()
            routing.append(dict(cycle=d.cycle.iloc[0], never_sex_coded_no=0,
                                inconsistent_no_msm_positive_count=int(conflict.sum())))
        d['age10'] = (d.RIDAGEYR - 40) / 10
        d['race'] = d.RIDRETH1.where(d.RIDRETH1.between(1, 5))
        d['education'] = d.DMDEDUC2.where(d.DMDEDUC2.between(1, 5))
        valid_born = [1, 2, 3] if suffix == 'D' else ([1, 2, 4, 5] if suffix in 'EF' else [1, 2])
        d['foreign_born'] = d[birthplace].ne(1).astype(float).where(d[birthplace].isin(valid_born))
        d['pir'] = d.INDFMPIR
        d['age_group'] = pd.cut(d.RIDAGEYR, [19, 29, 39, 49, 59], labels=False).astype(float)
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    assert d.SEQN.is_unique
    d = d[d.weight > 0].reset_index(drop=True)
    audits = pd.DataFrame(audit)
    audits.to_csv(OUT / 'codebook_frequency_audit.csv', index=False)
    discrepancies = audits[~audits.passed]
    print('Codebook discrepancies:', discrepancies.to_dict('records'), flush=True)
    critical = discrepancies[~((discrepancies.variable == 'SXQ410') & discrepancies.file.isin(['SXQ_F','SXQ_G','SXQ_H','SXQ_I']))]
    assert critical.empty, critical.to_dict('records')
    (OUT / 'codebook_extracts.txt').write_text('\n\n'.join(extracts))
    pd.DataFrame(routing).to_csv(OUT / 'routing_audit.csv', index=False)
    pd.DataFrame(parser_checks).to_csv(OUT / 'reader_crosscheck.csv', index=False)
    keep = ['SEQN','cycle','year','weight','stratum','psu','eligible','sxq_record','RIAGENDR',
            'RIDAGEYR','circ','identity_raw','identity_gb','identity_gay','identity_bi','sex_ever',
            'msm_ever','age10','race','education','foreign_born','pir','age_group','SXQ280']
    d[keep].to_csv(ROOT / 'data/analysis.csv.gz', index=False)
    return d

