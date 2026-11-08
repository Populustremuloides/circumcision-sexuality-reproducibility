"""Additional domain-variance, weight-scale, endpoint, and deliverable checks."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from analyze import ROOT, OUT, Survey, ADJUST

d = pd.read_csv(ROOT/'data/analysis.csv.gz')
s = Survey(d)
models = pd.read_csv(OUT/'models.csv')

# A hand-computed two-stratum example includes an empty domain PSU. Dropping
# that PSU would change the answer; retaining its zero contribution yields 25.
toy = pd.DataFrame({'stratum':['a','a','b','b'], 'psu':['a1','a2','b1','b2']})
np.testing.assert_allclose(Survey(toy).covariance(np.array([3.,0.,5.,1.])), [[25.]])

# Common rescaling of weights must change neither estimate nor survey SE.
scaled = d.copy()
scaled['weight'] *= 6
for out in ['identity_gb','msm_ever']:
    row,_ = Survey(scaled).model(out,ADJUST['full'],scaled.eligible,'full')
    ref = models.query('outcome == @out and model == "full" and sample == "available_for_model"').iloc[0]
    np.testing.assert_allclose([row['beta'],row['se']],[ref.beta,ref.se],rtol=1e-9)

# Check the identity-code reversal and mutually exclusive identity submodels.
early = d.year.lt(2015) & d.eligible
late = d.year.eq(2015) & d.eligible
assert d.loc[early & d.identity_raw.eq(1),'identity_gb'].eq(0).all()
assert d.loc[late & d.identity_raw.eq(1),'identity_gb'].eq(1).all()
assert d.loc[late & d.identity_raw.eq(2),'identity_gb'].eq(0).all()
assert d.loc[d.identity_raw.eq(3) & d.eligible,'identity_gb'].eq(1).all()
assert d.loc[d.year.lt(2009) & d.sex_ever.eq(0),'msm_ever'].eq(0).all()
assert d.weight.gt(0).all() and d.weight.min() > 1
assert set(d.loc[d.eligible,'RIDAGEYR']).issubset(set(range(20,60)))

manifest = json.loads((ROOT/'data/raw/manifest.json').read_text())
for item in manifest:
    assert hashlib.sha256((ROOT/'data/raw'/item['file']).read_bytes()).hexdigest() == item['sha256']

print('PASS: domain variance, weight invariance, endpoint coding, ages, weights, and source hashes.')
record = json.loads((OUT/'validation.json').read_text())
record['additional_validation'] = dict(domain_variance_hand_calculation=True,weight_scale_invariance=True,
    identity_reversal_and_skip_checks=True,source_hashes_24_verified=True,numerical_checks_only=True)
(OUT/'validation.json').write_text(json.dumps(record,indent=2))
