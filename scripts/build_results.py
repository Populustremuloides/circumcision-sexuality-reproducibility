"""Generate tracked Markdown summaries from locally reproduced, validated records.

--check fails on stale documentation. --ref COMMIT produces immutable code links.
No datasets or machine-readable model outputs are added to Git.
"""
from pathlib import Path
import argparse,json,ast,re
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
from src.specification import ANALYSES
BASE='https://github.com/Populustremuloides/circumcision-sexuality-reproducibility'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--ref');a=p.parse_args()
 if a.ref is None:a.ref=json.loads((ROOT/'docs/code_reference.json').read_text())['ref']
 validation=json.loads((ROOT/'outputs/validation/release.json').read_text());assert validation['passed']
 def link(path,fn=None):
  line=1
  if fn and path.endswith('.json'):
   line=next(i for i,v in enumerate((ROOT/path).read_text().splitlines(),1) if '"id": '+json.dumps(fn) in v)
  elif fn:
   nodes=ast.walk(ast.parse((ROOT/path).read_text()));line=next(n.lineno for n in nodes if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==fn)
  return f'{BASE}/blob/{a.ref}/{path}#L{line}'
 header='| Question | Frequentist OR (95% CI) | Bayesian OR (95% calibrated interval) | P(OR > 1) | Specification and code |\n|---|---:|---:|---:|---|'
 rows=[];details=['# Results and reproducible questions','Generated from validated local result records. The two methods use identical participants and formulas for each headline question.','']
 for aid,spec in ANALYSES.items():
  f=json.loads((ROOT/f'outputs/frequentist/headline/{aid}.json').read_text());b=json.loads((ROOT/f'outputs/bayesian/headline/{aid}.json').read_text())
  orf=f.get('odds_ratio',f.get('or'));assert orf is not None
  links=f'[specification]({link("config/analyses.json",aid)}) · [frequentist]({link("analyses/nhanes/run.py","frequentist")}) · [Bayesian]({link("src/bayesian/headline.py","run")})'
  rows.append(f'| {spec["question"]} | {orf:.2f} ({f["ci_low"]:.2f}–{f["ci_high"]:.2f}) | {b["OR"]:.2f} ({b["low"]:.2f}–{b["high"]:.2f}) | {100*b["p_positive"]:.1f}% | {links} |')
  details += [f'## {spec["question"]}',f'Analysis ID: `{aid}`. N = {b["n"]:,}; events = {b["events"]:,}.',f'```sh\npython -m analyses.nhanes.run --analysis {aid}\n```',f'Formula: `{spec["formula"]}`.',f'{links}. The survey estimator is implemented in [Survey.model]({link("src/survey/design.py","model")}); the Bayesian likelihood and numerical integration are in [logistic.py]({link("src/bayesian/logistic.py","importance")}).',f'The command writes matching JSON result records to `outputs/frequentist/headline/{aid}.json` and `outputs/bayesian/headline/{aid}.json`. Records include the input/specification hashes, code hash, Git commit, sample size and uncertainty.','']
 table='\n'.join([header]+rows)
 details.insert(3,table)
 details += ['## Other questions', '| Question family | Frequentist implementation | Bayesian implementation | Scope |','|---|---|---|---|',
 '| Specific anal/oral behaviors | [behavior.py](../src/frequentist/behavior.py) | [approximation.py](../src/bayesian/approximation.py) | Gaussian/t approximation; not the directly fitted headline method |',
 '| Within-identity associations and interactions | [identity.py](../src/frequentist/identity.py) | [approximation.py](../src/bayesian/approximation.py) | Interaction conclusions remain sensitive to nuisance priors |',
 '| Explanatory contrasts | [explanations.py](../src/frequentist/explanations.py) | [approximation.py](../src/bayesian/approximation.py) | Some estimands are differences, not odds ratios; failed fits retained |',
 '| Maloney regret and self-concept | [maloney.py](../src/frequentist/maloney.py) | [maloney.py](../src/bayesian/maloney.py) | Separate unweighted sample; primary326 and sensitivity325 |',
 '| Later circumcision scenarios | [allocation fits](../analyses/timing/run_allocation.py) | [mixture scenarios](../analyses/timing/run_timing.py) | Conditional assumptions, not observed timing or infant causal effects |','',
 'Run all standard questions with `python scripts/reproduce.py`; add `--validation` for the full-likelihood comparisons and targeted simulations. Timing scenarios are separate opt-in commands documented [here](../analyses/timing/README.md). Full extension tables remain generated locally. No incompatible estimands are presented as interchangeable method comparisons.']
 extra=['# Extension results by scientific question','Generated from the same execution records as the headline comparison. Bayesian NHANES extensions below retain the original Gaussian approximation; they are not direct-posterior headline fits. These exploratory comparisons are not causal effects.']
 manifest={v['id']:v for v in json.loads((ROOT/'outputs/bayesian/approximation/model_manifest.json').read_text())}
 btab=pd.read_csv(ROOT/'outputs/bayesian/approximation/nhanes_results.csv')
 for family,module in [('behavior','src/frequentist/behavior.py'),('subgroup','src/frequentist/identity.py'),('interaction','src/frequentist/identity.py')]:
  extra += [f'## {family.title()}', '| Result ID and question | Frequentist OR (95% CI) | Bayesian OR (95% CrI) | P(positive) | Code |','|---|---:|---:|---:|---|']
  sub=btab[btab.family.eq(family)&btab.prior.eq('primary')&btab.likelihood.eq('normal')]
  for _,b in sub.iterrows():
   ref=manifest[b.id]['reference'];q='; '.join(str(ref[k]) for k in ['outcome','population','group','period'] if k in ref)
   extra.append(f'| `{b.id}` {q} | {ref["odds_ratio"]:.2f} ({ref["ci_low"]:.2f}–{ref["ci_high"]:.2f}) | {b.odds_ratio:.2f} ({b.ci_low:.2f}–{b.ci_high:.2f}) | {100*b.p_positive:.1f}% | [frequentist]({link(module)}) · [Bayesian]({link("src/bayesian/approximation.py","main")}) |')
 extra += ['Interaction rows estimate ratios of odds ratios. The interaction probabilities are sensitive to nuisance priors; see all generated prior-sensitivity rows before interpreting them. Row IDs identify the exact manifest entry in `outputs/bayesian/approximation/model_manifest.json`.', '## Explanatory contrasts', 'These mix prevalence differences and ratios; the scalar Bayesian implementation and each contrast orientation are in [approximation.py](../src/bayesian/approximation.py) and [explanations.py](../src/frequentist/explanations.py). Results are generated in `outputs/bayesian/approximation/explanatory_results.csv` and `outputs/frequentist/explanations/focal_tests.csv`. Failed contrasts remain explicitly unavailable.']
 bp=ROOT/'outputs/bayesian/maloney/maloney_results.csv';fp=ROOT/'outputs/frequentist/maloney/associations.csv'
 if bp.exists() and fp.exists():
  bm=pd.read_csv(bp);fm=pd.read_csv(fp);mapping={'masculinity_regret':'masculinity–regret','masculinity_visibility':'masculinity–visibility','both_neither_regret':'both versus neither–regret'}
  extra += ['## Maloney: separate sample', 'The first three frequentist rows use conditional exact ORs and intervals; the remaining rows use logistic Wald intervals. Bayesian estimates use the direct Bernoulli likelihood and proper priors. This comparison does not imply that conditional exact inference and Bayesian logistic inference are identical procedures.', '| Sample; question; coefficient | N | Frequentist OR (95% CI) | Bayesian OR (95% CrI) | P(OR > 1) | Code |','|---|---:|---:|---:|---:|---|']
  for _,b in bm[bm.prior.eq('primary')].iterrows():
   fs='primary' if b['sample']=='primary' else 'manuscript_sensitivity';name=mapping.get(b.model,('additive model: ' if b.model=='additive_regret' else 'interaction model: ')+b.term)
   f=fm[fm['sample'].eq(fs)&fm.comparison.eq(name)].iloc[0];assert int(f.n)==int(b.n)
   extra.append(f'| {b["sample"]}; {b.model}; {b.term} | {int(b.n)} | {f.odds_ratio:.2f} ({f.ci_low:.2f}–{f.ci_high:.2f}) | {b.odds_ratio:.2f} ({b.ci_low:.2f}–{b.ci_high:.2f}) | {100*b.p_positive:.1f}% | [frequentist]({link("src/frequentist/maloney.py","main")}) · [Bayesian]({link("src/bayesian/maloney.py","main")}) |')
 details += ['## Detailed extension comparisons','See [the generated extension results](extension_results.md) for behavior, identity subgroup/interaction and Maloney comparisons.']
 template=(ROOT/'docs/readme_template.md').read_text();readme=template.replace('<!-- RESULTS -->',table)

 for path,content in [(ROOT/'README.md',readme),(ROOT/'docs/results.md','\n\n'.join(details)+'\n'),(ROOT/'docs/extension_results.md',re.sub(r'(\|[^\n]*\|)\n\n(?=\|)',r'\1\n','\n\n'.join(extra))+'\n')]:
  if a.check:assert path.read_text()==content,f'Stale documentation: {path}'
  else:path.write_text(content)
 print('Result documentation checked.' if a.check else 'Result documentation generated.')
if __name__=='__main__':main()
