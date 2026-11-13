"""Direct proper-prior logistic pseudo-posterior, calibrated at its posterior mean.

Each registered analysis uses four independent importance batches. Unlike the
Gaussian-summary sensitivity, this fit does not require an unregularized MLE.
"""
from src.bayesian.logistic import *
import argparse,json,hashlib,subprocess

def run(analysis_id):
 spec=ANALYSES[analysis_id];outcome=spec['outcome'];oi=list(ANALYSES).index(analysis_id)
 X,y,w,codes,cols,z=dataset(outcome);j=cols.index('circ');sd=priors(cols,.5)
 U,inv=np.unique(X,axis=0,return_inverse=True);W=np.bincount(inv,weights=w);Y=np.bincount(inv,weights=w*y)/W
 b=np.zeros(len(cols));b[0]=np.log(np.average(y,weights=w)/(1-np.average(y,weights=w)))
 I=np.eye(len(b));draws=[];weights=[]
 for k in range(4):
  B,ww,mode,C=importance(U,Y,W,b,I,I,sd,'pseudo',20261113+100*oi+k)
  draws.append(B);weights.append(ww)
 B=np.concatenate(draws);ww=np.concatenate(weights)/4;mu=ww@B
 p=expit(X@mu);H=X.T@((w*p*(1-p))[:,None]*X);V=covariance(X,y,w,codes,mu,H);T=root(V)@root(H)
 np.testing.assert_allclose(T@np.linalg.inv(H)@T.T,V,rtol=1e-7,atol=1e-8)
 adjusted=mu+(B-mu)@T.T;summary=stats(adjusted,ww,j)
 batches=[stats(adjusted[k*32768:(k+1)*32768],weights[k],j) for k in range(4)]
 summary['probability_batch_range']=float(np.ptp([r['p_positive'] for r in batches]));summary['median_batch_range']=float(np.ptp([r['OR'] for r in batches]))
 assert summary['ess']>10000 and summary['max_weight']<.01 and summary['probability_batch_range']<.01 and summary['median_batch_range']<.03
 record=dict(analysis_id=analysis_id,outcome=outcome,method='posterior_plugin_pseudo',n=len(y),events=int(y.sum()),formula=spec['formula'],priors=dict(zip(cols,sd.tolist())),**{k:float(v) for k,v in summary.items()},code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),input_sha256=hashlib.sha256((REPO/'data/analysis.csv.gz').read_bytes()).hexdigest(),source_manifest_sha256=hashlib.sha256((ROOT/'config/sources.json').read_bytes()).hexdigest(),spec_sha256=hashlib.sha256((ROOT/'config/analyses.json').read_bytes()).hexdigest(),commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),batches=batches)
 out=ROOT/'outputs/bayesian/headline';out.mkdir(parents=True,exist_ok=True)
 (out/(analysis_id+'.json')).write_text(json.dumps(record,indent=2)+'\n')
 np.savez_compressed(out/(analysis_id+'.npz'),draws=adjusted,weights=ww,columns=cols)
 print(analysis_id,summary,flush=True);return record

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--analysis',choices=list(ANALYSES));args=parser.parse_args()
 for aid in ([args.analysis] if args.analysis else ANALYSES):run(aid)
if __name__=='__main__':main()
