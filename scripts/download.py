"""Download public inputs and reject any mismatch with the pinned source hashes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def fetch(record, offline=False):
    path = ROOT / record['path']
    expected = record['sha256']
    if not path.exists():
        if offline:
            raise FileNotFoundError(f'Missing cached input: {path}. Run without --offline first.')
        path.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(3):
            try:
                request = urllib.request.Request(record['url'], headers={'User-Agent': 'research-reproduction/1.0'})
                with urllib.request.urlopen(request, timeout=90) as response:
                    content = response.read()
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
        actual = hashlib.sha256(content).hexdigest()
        if actual != expected:
            raise ValueError(f'Source changed or download was not the expected file: {record["url"]}; '
                             f'expected {expected}, got {actual}. No file was installed.')
        temporary = path.with_suffix(path.suffix + '.partial')
        temporary.write_bytes(content)
        temporary.replace(path)
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != expected:
        raise ValueError(f'Cached input checksum mismatch: {path}. Preserve it for review before retrying.')
    return dict(file=path.name, url=record['url'], bytes=len(content), sha256=expected,
                checked_utc=datetime.now(timezone.utc).isoformat())


def main(offline=False):
    specs = json.loads((ROOT / 'config/sources.json').read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(lambda spec: fetch(spec, offline), specs))
    nhanes = [record for spec, record in zip(specs, records) if spec['path'].startswith('data/raw/')]
    (ROOT / 'data/raw/manifest.json').write_text(json.dumps(nhanes, indent=2) + '\n')
    (ROOT / 'data/download_manifest.json').write_text(json.dumps(records, indent=2) + '\n')
    print(f'Verified {len(records)} public source files.', flush=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true')
    main(parser.parse_args().offline)
