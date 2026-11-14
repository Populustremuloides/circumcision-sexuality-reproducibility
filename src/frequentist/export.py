"""Export and verify an existing Survey.model fit for point-scenario standardization.

NPZ records stay local: complete coefficient vector/covariance, predictor names,
analytic participant IDs, and the intact-reference design matrix and normalized
survey weights of circumcised complete cases. JSON records contain provenance.
No independent plotting regression is fitted. Predicted probabilities are point
calculations, not confidence limits or causal intervention estimates.
"""
import hashlib,json,subprocess
import numpy as np
from scipy.special import expit
from src.specification import ROOT,ANALYSES
PRIMARY='nhanes.msm_ever.adjusted'
CODE=['src/survey/design.py','src/frequentist/export.py','analyses/nhanes/run.py','src/data/nhanes.py','src/specification.py']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write_fit(aid,data,row,details):
    out=ROOT/'outputs/frequentist/headline';out.mkdir(parents=True,exist_ok=True)
    path=out/(aid+'.npz');idx=details['indices'];z=data.loc[idx];keep=z.circ.eq(1).to_numpy()
    X0=details['X'][keep].copy();j=details['columns'].index('circ');X0[:,j]=0
    weights=z.loc[keep,'weight'].to_numpy();weights=weights/weights.sum()
    beta=details['coefficients'];p0=expit(X0@beta);p1=expit(X0@beta+beta[j])
    assert np.all((p0>0)&(p1<1));np.testing.assert_allclose(np.exp(beta[j]),row['odds_ratio'],rtol=1e-13)
    np.savez_compressed(path,coefficients=beta,covariance=details['covariance'],columns=details['columns'],
        analytic_seqn=z.SEQN.to_numpy(),target_seqn=z.loc[keep,'SEQN'].to_numpy(),X0=X0,target_weights=weights,circ_index=j)
    meta=dict(row,analysis_id=aid,method='survey_logistic_t',sample=ANALYSES[aid]['sample'],
        input_sha256=sha(ROOT/'data/analysis.csv.gz'),spec_sha256=sha(ROOT/'config/analyses.json'),
        code_hashes={f:sha(ROOT/f) for f in CODE},commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        artifact_sha256=sha(path),columns=details['columns'],coefficients=beta.tolist(),
        analytic_ids_sha256=hashlib.sha256(z.SEQN.to_numpy().tobytes()).hexdigest(),
        standardization=dict(target='survey-weighted circumcised complete-case covariate distribution',n=int(keep.sum()),
            intact_probability=float(weights@p0),circumcised_probability=float(weights@p1),gap=float(weights@(p1-p0))))
    path.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n');return meta

def load_primary():
    path=ROOT/'outputs/frequentist/headline'/f'{PRIMARY}.npz'
    meta=json.loads(path.with_suffix('.json').read_text())
    assert meta['input_sha256']==sha(ROOT/'data/analysis.csv.gz'),'Stale data: rerun reproduction.'
    assert meta['spec_sha256']==sha(ROOT/'config/analyses.json'),'Stale specification.'
    assert meta['artifact_sha256']==sha(path),'Fitted artifact changed.'
    for f,h in meta['code_hashes'].items():assert sha(ROOT/f)==h,f'Stale fit code: {f}'
    with np.load(path,allow_pickle=False) as archive:cache={k:archive[k] for k in archive.files}
    assert list(cache['columns'])==meta['columns'];np.testing.assert_array_equal(cache['coefficients'],meta['coefficients'])
    assert len(cache['analytic_seqn'])==meta['n'];assert len(cache['target_seqn'])==meta['standardization']['n']
    w=cache['target_weights'];np.testing.assert_allclose(w.sum(),1,atol=1e-14);assert (w>0).all()
    eta=cache['X0']@cache['coefficients'];p0=w@expit(eta);p1=w@expit(eta+cache['coefficients'][int(cache['circ_index'])])
    np.testing.assert_allclose([p0,p1,p1-p0],[meta['standardization'][k] for k in ['intact_probability','circumcised_probability','gap']],atol=1e-14)
    return cache,meta
