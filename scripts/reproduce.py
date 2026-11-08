"""Download inputs, regenerate estimates, and run numerical verification."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='Require checksum-verified cached inputs.')
    parser.add_argument('--nhanes-only', action='store_true', help='Omit the separate Maloney supplement.')
    parser.add_argument('--r-check', action='store_true', help='Also verify core estimates with R survey.')
    args = parser.parse_args()
    if args.r_check and not shutil.which('Rscript'):
        parser.error('--r-check requires Rscript on PATH and the R survey package; see README.md.')
    out = ROOT / 'outputs'
    logs = out / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               VECLIB_MAXIMUM_THREADS='1', MKL_NUM_THREADS='1', MPLBACKEND='Agg',
               MPLCONFIGDIR=str(out / '.matplotlib'))
    scripts = ['download.py', 'analyze.py', 'behavior_extension.py', 'identity_subgroups.py',
               'explanation_analysis.py', 'validate_explanation_analysis.py', 'validate.py', 'plot_main.py']
    if not args.nhanes_only:
        scripts += ['maloney_supplement.py']
    if args.r_check:
        scripts += ['reproduce_survey.R']
    status = dict(status='running', started_utc=datetime.now(timezone.utc).isoformat(),
                  python=sys.version, stages=[], arguments=vars(args),
                  source_specification_sha256=hashlib.sha256((ROOT/'config/sources.json').read_bytes()).hexdigest())
    status_path = out / 'run.json'
    status_path.write_text(json.dumps(status, indent=2) + '\n')
    for script in scripts:
        print(f'Running {script} ...', flush=True)
        command = ['Rscript' if script.endswith('.R') else sys.executable, str(ROOT/'scripts'/script)]
        if script == 'download.py' and args.offline:
            command += ['--offline']
        start = time.monotonic()
        with (logs/(script+'.log')).open('w') as log:
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        status['stages'].append(dict(script=script, exit_code=result.returncode,
                                     elapsed_seconds=round(time.monotonic()-start, 2)))
        if result.returncode:
            status.update(status='failed', failed_stage=script)
            status_path.write_text(json.dumps(status, indent=2)+'\n')
            print((logs/(script+'.log')).read_text()[-6000:])
            raise SystemExit(result.returncode)
        status_path.write_text(json.dumps(status, indent=2)+'\n')
    status.update(status='passed', completed_utc=datetime.now(timezone.utc).isoformat())
    status_path.write_text(json.dumps(status, indent=2)+'\n')
    print('Reproduction and checks passed. Generated results are in outputs/.', flush=True)


if __name__ == '__main__':
    main()
