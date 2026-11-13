"""Check matched headline samples, integration, and numerical release references."""
from pathlib import Path
import json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
from src.specification import ANALYSES
# Frozen validated direct-likelihood estimates, not raw data or fitted coefficients.
REFERENCE={'msm_ever':(1.4848844354,.9986919269,9161),'identity_gb':(1.2186433255,.8630321511,8962),'identity_gay':(1.3957251104,.9484696360,8825),'identity_bi':(.9428645436,.4211062549,8766)}
def main():
 checks=[]
 for aid,spec in ANALYSES.items():
  f=json.loads((ROOT/f'outputs/frequentist/headline/{aid}.json').read_text());b=json.loads((ROOT/f'outputs/bayesian/headline/{aid}.json').read_text());o,p,n=REFERENCE[spec['outcome']]
  assert f['n']==b['n']==n and f['events']==b['events']
  assert f['formula']==b['formula']==spec['formula'];assert f['input_sha256']==b['input_sha256'];assert f['spec_sha256']==b['spec_sha256']
  np.testing.assert_allclose(b['OR'],o,atol=.002,rtol=0);np.testing.assert_allclose(b['p_positive'],p,atol=.002,rtol=0)
  assert b['ess']>10000 and b['probability_batch_range']<.01
  checks.append(dict(analysis_id=aid,matched_samples_and_specification=True,validated_reference_match=True))
 out=ROOT/'outputs/validation';out.mkdir(parents=True,exist_ok=True);(out/'release.json').write_text(json.dumps({'passed':True,'checks':checks},indent=2)+'\n');print('Release checks passed.')
if __name__=='__main__':main()
