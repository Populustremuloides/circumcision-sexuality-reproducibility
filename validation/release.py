"""Compare retained results against the validated pre-refactor reference tables."""
import argparse,json
import numpy as np,pandas as pd
from src.specification import ROOT,ANALYSES
from src.frequentist.export import load_primary

def main():
    p=argparse.ArgumentParser();p.add_argument('--with-maloney',action='store_true');args=p.parse_args()
    reference=json.loads((ROOT/'validation/frequentist/reference_results.json').read_text());checks=[]
    for name,table in reference['tables'].items():
        if name.startswith('maloney/') and not args.with_maloney:continue
        expected=pd.DataFrame(table['data'],columns=table['columns']);actual=pd.read_csv(ROOT/'outputs/frequentist'/name)
        assert list(actual.columns)==list(expected.columns),name
        assert len(actual)==len(expected),name
        for col in actual:
            if pd.api.types.is_numeric_dtype(actual[col]):
                np.testing.assert_allclose(actual[col].astype(float),pd.to_numeric(expected[col]).astype(float),rtol=1e-7,atol=1e-9,equal_nan=True,err_msg=f'{name}: {col}')
            else:assert actual[col].fillna('<NA>').astype(str).tolist()==expected[col].fillna('<NA>').astype(str).tolist(),(name,col)
        checks.append(dict(table=name,rows=len(actual),matched=True))
    models=pd.read_csv(ROOT/'outputs/frequentist/models.csv');sens=pd.read_csv(ROOT/'outputs/frequentist/sensitivities.csv')
    for aid,spec in ANALYSES.items():
        r=json.loads((ROOT/f'outputs/frequentist/headline/{aid}.json').read_text())
        source=models[(models.outcome==spec['outcome'])&(models.model=='full')&(models['sample']=='available_for_model')]
        if source.empty:source=sens[(sens.outcome==spec['outcome'])&(sens.model=='full')]
        assert len(source)==1
        for k in ['n','events','beta','se','odds_ratio','ci_low','ci_high','p_value','residual_df']:np.testing.assert_allclose(r[k],source.iloc[0][k],rtol=1e-9,atol=1e-10)
        assert r['formula']==spec['formula']
    cache,meta=load_primary();assert meta['n']==9161 and meta['events']==498
    result=dict(passed=True,reference_commit=reference['baseline_commit'],rtol=1e-7,atol=1e-9,checks=checks,export_matches_original=True,standardization_verified=True)
    out=ROOT/'outputs/validation';out.mkdir(exist_ok=True,parents=True);(out/'release.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Frequentist reference, export and standardization checks passed.')
if __name__=='__main__':main()
