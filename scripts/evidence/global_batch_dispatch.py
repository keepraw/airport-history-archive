"""Validate global research proposals in slim Git checkouts without altering fingerprinted global_batch.py."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SLIMMED_INPUT_MANIFESTS = {
    'reference/triage/groups.jsonl.gz': ('reference/triage/manifest.json', 'groups.jsonl.gz'),
    'research/discovery/generated/verification-queue.jsonl.gz': (
        'research/discovery/generated/manifest.json',
        'verification-queue.jsonl.gz',
    ),
}


def validate_slim():
    import global_batch as gb
    output = gb.OUT
    manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
    for p, h in manifest['inputs'].items():
        if p in SLIMMED_INPUT_MANIFESTS and not (ROOT / p).is_file():
            work_copy = ROOT / 'work' / p
            if work_copy.is_file():
                if gb.digest(work_copy) != h:
                    raise ValueError('Changed work research input: ' + p)
                continue
            lock_rel, key = SLIMMED_INPUT_MANIFESTS[p]
            lock_doc = json.loads((ROOT / lock_rel).read_text(encoding='utf-8'))
            if lock_doc['files'][key]['sha256'] != h:
                raise ValueError('Detached slimmed research input hash: ' + p)
            continue
        if gb.digest(ROOT / p) != h:
            raise ValueError('Research input changed: ' + p)
    for p, h in manifest['outputs'].items():
        if gb.digest(output / p) != h:
            raise ValueError('Research output changed: ' + p)
    assessment = json.loads((gb.BASE / 'assessments.json').read_text(encoding='utf-8'))
    proposed = json.loads((output / 'proposed-data.json').read_text(encoding='utf-8'))
    base = json.loads((ROOT / 'test/curated-0.8.0.json').read_text(encoding='utf-8'))
    dossiers = json.loads((output / 'dossier.json').read_text(encoding='utf-8'))
    loaded = {s['sourceId']: (s, t) for s, t in gb.locked(ROOT / manifest['sourceDirectory'])}
    for f in json.loads((output / 'facts.json').read_text(encoding='utf-8')):
        if f['citation'] != gb.citation(f, loaded):
            raise ValueError('Unreproducible citation')
    fresh = {}
    for f in assessment['facts']:
        sid = f['sourceId']
        s, _ = loaded[sid]
        if s.get('retention') == 'metadata_and_cited_excerpts':
            continue
        if sid not in fresh:
            raw = gb.gzip.decompress((ROOT / manifest['sourceDirectory'] / s['inputPath']).read_bytes())
            fresh[sid] = (s, gb.extract(raw, s.get('encoding', 'utf-8')))
        if gb.citation(f, fresh)['page'] != gb.citation(f, loaded)['page']:
            raise ValueError('Citation page differs in independent extraction')
    for collection, field in [('airports', 'airportId'), ('assignments', 'assignmentId'),
                              ('sources', 'sourceId'), ('names', 'nameId')]:
        old = {r[field]: r for r in base[collection]}
        new = {r[field]: r for r in proposed[collection]}
        if len(new) != len(proposed[collection]) or any(new.get(k) != v for k, v in old.items()):
            raise ValueError('Changed permanent record or duplicate identity')
        if collection in ('assignments', 'sources') and any(
                new[k]['verificationStatus'] != 'pending' for k in new.keys() - old.keys()):
            raise ValueError('Research impersonates verified history')
    if any(d['decision'] != 'pending' or d['reviewer'] is not None for d in dossiers):
        raise ValueError('Research impersonates human approval')
    batches = list(gb.read_jsonl(output / 'review-packets.jsonl.gz'))
    earlier = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'research/discovery/batches').glob('*.json'))]
    gb.validate_batch_series([*earlier, *batches])
    try:
        gb.validate_admission(base, proposed, batches, dossiers)
    except ValueError as e:
        if 'explicit claim review' not in str(e):
            raise
    else:
        raise ValueError('Unauthorized proposal passed admission')
    report = json.loads((output / 'query-coverage.json').read_text(encoding='utf-8'))
    if report['formalNewResolvedQueries'] or report['changedPublishedResolvedQueries'] or report['changedPendingResolvedQueries']:
        raise ValueError('Published query history changed')
    print('Validated global originals, citations, current-baseline deduplication, pending records and unchanged admission rejection.')


if __name__ == '__main__':
    if sys.argv[1:] == ['validate']:
        validate_slim()
    else:
        subprocess.run([sys.executable, 'scripts/evidence/global_batch.py', *sys.argv[1:]], cwd=ROOT, check=True)
