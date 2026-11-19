"""Validate shipped research manifests, summaries and review overrides offline.

When regenerable JSONL shards exist in work/discovery/generated (or OUT), full
stream counts/hashes are verified. In slim Git checkouts where large JSONL shards
are omitted from Git, manifest hashes, coverage accounting, curated baselines and
reviewed-observations.json are verified instead.
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

from core import apply_review, read_candidates, read_jsonl, stable_id
from review import REVIEW_STATUSES as STATUSES, batch_summaries, validate_review_overrides

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/evidence'))
from default_continuity import inherited_assignment_view
OUT = ROOT / 'research/discovery/generated'
WORK_OUT = ROOT / 'work/discovery/generated'
COMPANION_FILES = {'manifest.json', 'reviewed-observations.json'}
SLIMMED_SCRIPTS = {'scripts/discovery/validate.py', 'scripts/discovery/query.py'}


def require(test, message):
    if not test:
        raise ValueError(message)


def shard_path(name):
    if (WORK_OUT / name).is_file():
        return WORK_OUT / name
    if (OUT / name).is_file():
        return OUT / name
    return None


def main():
    manifest_raw = (OUT / 'manifest.json').read_bytes()
    lock = json.loads(manifest_raw)
    present_in_out = {p.name for p in OUT.iterdir() if p.is_file() and p.name not in COMPANION_FILES}
    require(present_in_out <= set(lock['files']), 'Unmanifested artifact')
    missing_shards = []
    for name, expected in lock['files'].items():
        path = shard_path(name)
        if path is None:
            require(name.endswith('.jsonl.gz'), f'Missing required summary/coverage file: {name}')
            missing_shards.append(name)
            continue
        require(path.stat().st_size == expected['bytes'], f'Wrong size: {name}')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected['sha256'], f'Wrong hash: {name}')
    for name, digest in {**lock['inputs'], **lock.get('reviewInputs', {})}.items():
        if name in SLIMMED_SCRIPTS:
            require((ROOT / name).is_file(), f'Missing script: {name}')
            continue
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, f'Changed generation input: {name}; regenerate report')
    baseline = json.loads((ROOT / 'research/discovery/curated-baseline.json').read_text())
    frozen_path = ROOT / f"test/curated-{baseline['dataVersion']}.json"
    require(hashlib.sha256(frozen_path.read_bytes()).hexdigest() == baseline['sha256'], 'Curated historical facts changed')
    frozen = json.loads(frozen_path.read_text())
    dataset = json.loads((ROOT / 'data/airports.json').read_text())
    preserved = inherited_assignment_view(dataset)
    require(all(baseline[k] == len(frozen[k]) for k in ('airports', 'assignments', 'names', 'sources')) and
            baseline['dataVersion'] == frozen['dataVersion'], 'Curated baseline counts/version are stale')
    for key, id_key in (('airports', 'airportId'), ('assignments', 'assignmentId'), ('names', 'nameId'), ('sources', 'sourceId')):
        current = {r[id_key]: r for r in preserved[key]}
        require(all(current.get(r[id_key]) == r for r in frozen[key]), f'Frozen research baseline {key} changed')
    for previous in baseline['preservedBaselines']:
        raw = (ROOT / previous['record']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == previous['sha256'], f"Preserved curated record changed: {previous['record']}")
        frozen = json.loads(raw)
        for key, id_key in (('airports', 'airportId'), ('assignments', 'assignmentId'), ('names', 'nameId'), ('sources', 'sourceId')):
            current = {r[id_key]: r for r in preserved[key]}
            require(all(current.get(r[id_key]) == r for r in frozen[key]),
                    f"Pre-{dataset['dataVersion']} curated {key} changed or removed (baseline {previous['dataVersion']})")
    airports = {r['airportId'] for r in dataset['airports']}
    assignments = {r['assignmentId'] for r in dataset['assignments']}
    names = {r['nameId'] for r in dataset['names']}
    config = json.loads((ROOT / 'research/discovery/sources.json').read_text())
    reviews = json.loads((ROOT / 'research/discovery/reviews.json').read_text())
    review_ids = set(reviews)
    summary = json.loads((OUT / 'summary.json').read_text())
    legacy = json.loads((ROOT / 'research/discovery/legacy.json').read_text())
    require(sum(r['status'] == 'insufficient_evidence' for r in legacy) >= 8, 'Lost deferred leads')
    batches = [{**entry, 'path': entry['path'].replace('\\', '/')} for entry in batch_summaries(ROOT)]
    require(summary.get('reviewBatches', []) == batches, 'Stale batch review summary')
    batch_records = [(entry['path'], json.loads((ROOT / entry['path']).read_text(encoding='utf-8'))) for entry in batches]
    validate_review_overrides(reviews, batch_records)
    require(set(lock.get('reviewInputs', {})) == {'research/discovery/reviews.json', *(r['path'] for r in batches)}, 'Unmanifested review evidence')

    if not missing_shards:
        corpus_dir = WORK_OUT if (WORK_OUT / 'duplicate-groups.jsonl.gz').is_file() else OUT
        seen_reviews = set()
        reviewed_rows = {}
        grand_total = 0
        all_ids = set()
        for source in config['sources']:
            sid = source['id']
            report = json.loads((OUT / (sid + '.coverage.json')).read_text())
            require(report['sourceId'] == sid and report['revision'] == source['revision'] and report['path'] == source['path'], f'Stale source coverage: {sid}; run research:scan')
            ids = set()
            counts, types, countries, years = Counter(), Counter(), Counter(), Counter()
            observations = 0
            for row in read_candidates(corpus_dir, sid):
                cid = row['candidateId']
                require(cid not in ids, f'Duplicate candidate {cid}')
                ids.add(cid)
                if cid in review_ids:
                    seen_reviews.add(cid)
                    reviewed_rows[cid] = row
                    reviewed = apply_review(row, reviews)['review']
                    require(reviewed['status'] in STATUSES, 'Unknown live review status')
                    require(reviewed.get('nextAction') and reviewed.get('evidenceGaps'), 'Incomplete live review')
                    if reviewed['status'] == 'excluded':
                        require(reviewed.get('exclusionReason'), 'Missing live exclusion reason')
                extra = 'baseline_closed_record' if row['types'] == ['baseline_closed_record'] else None
                require(cid == stable_id('cand_', [sid, row['sourceEntityId'], row['changes'], extra]), f'Unstable ID {cid}')
                require(row['sourceId'] == sid, 'Wrong source')
                require(row['review']['status'] in STATUSES, 'Unknown review status')
                require(row['time']['eventDate'] is None and row['time']['eventDatePrecision'] == 'unknown', 'Machine revision promoted to event date')
                require(row['evidence']['evidenceType'] == 'indirect' and row['evidence']['verificationStatus'] == 'pending', 'Machine revision promoted to verified fact')
                for observation in row['observations']:
                    require(all(re.fullmatch('[a-f0-9]{40}', observation[k]) for k in ('commit', 'beforeBlob', 'afterBlob')), 'Unpinned observation')
                require(set(row['matches']['airportIds']) <= airports, 'Missing airport match')
                require(set(row['matches']['assignmentIds']) <= assignments, 'Missing assignment match')
                require(set(row['matches']['nameIds']) <= names, 'Missing name match')
                if row['review']['status'] == 'excluded':
                    require(bool(row['review']['exclusionReason']), 'Missing exclusion reason')
                observations += len(row['observations'])
                counts[row['review']['status']] += 1
                types.update(row['types'])
                countries[row['context']['country']] += 1
                years[row['time']['firstObservedRevisionAt'][:4]] += 1
            d = report['discovery']
            require(len(ids) == d['candidates'] and observations == d['rawCandidateObservations'], f'Wrong totals: {sid}')
            for actual, key in [(counts, 'byStatus'), (types, 'byType'), (countries, 'byCountry'), (years, 'byObservationYear')]:
                require(dict(actual) == d[key], f'Wrong {key}: {sid}')
            versions = list(read_jsonl(shard_path(sid + '.versions.jsonl.gz')))
            require(len(versions) == report['history']['parentDiffs'], f'Wrong version edge count: {sid}')
            require(len({v['commit'] for v in versions}) == report['history']['fileChangingCommits'], f'Wrong commit count: {sid}')
            unique = {v['afterBlob']: v['afterRecords'] for v in versions}
            require(len(unique) == report['history']['uniqueFileVersions'], f'Wrong unique version count: {sid}')
            require(sum(v is None for v in unique.values()) == report['history']['unparsedFileVersions'], f'Wrong parse-gap count: {sid}')
            require(sum(1 for _ in read_jsonl(shard_path(sid + '.gaps.jsonl.gz'))) == report['history']['blockedComparisons'], f'Wrong blocked comparison count: {sid}')
            require(sum(n or 0 for n in unique.values()) == report['history']['recordVersionsProcessed'], f'Wrong record-version count: {sid}')
            entity_count = sum(1 for _ in read_jsonl(shard_path(sid + '.entities.jsonl.gz')))
            require(entity_count == report['history']['entitiesEverObserved'], f'Wrong inventory count: {sid}')
            grand_total += len(ids)
            require(not (all_ids & ids), 'Cross-source ID collision')
            all_ids.update(ids)
        require(review_ids == seen_reviews, 'Orphaned review override; never silently discard curation')
        require(summary['sourceRevisionCandidates'] == grand_total, 'Wrong global source total')
        link_count = 0
        for row in read_jsonl(shard_path('code-links.candidates.jsonl.gz')):
            require(set(row['relatedCandidateIds']) <= all_ids, 'Dangling code-link candidate reference')
            link_count += 1
        require(link_count == summary['codeAssociationCandidates'], 'Wrong relational candidate count')
        group_count, excess = 0, 0
        for row in read_jsonl(shard_path('duplicate-groups.jsonl.gz')):
            require({m['candidateId'] for m in row['members']} <= all_ids, 'Dangling duplicate-group member')
            group_count += 1
            excess += len(row['members']) - 1
        require(group_count == summary['exactCrossSourceDuplicateGroups']['groups'], 'Wrong duplicate-group total')
        require(grand_total - excess == summary['sourceTransitionLeadsAfterExactCrossSourceGrouping'], 'Wrong deduplicated total')
        known_ids = all_ids | {r['candidateId'] for r in legacy}
    else:
        retained = json.loads((OUT / 'reviewed-observations.json').read_text())
        require(retained['formatVersion'] == 1 and
                retained['manifestSha256'] == hashlib.sha256(manifest_raw).hexdigest(),
                'Stale or detached reviewed-observations.json')
        grand_total = 0
        for source in config['sources']:
            sid = source['id']
            report = json.loads((OUT / (sid + '.coverage.json')).read_text())
            require(report['sourceId'] == sid and report['revision'] == source['revision'] and report['path'] == source['path'],
                    f'Stale source coverage: {sid}; run research:scan')
            grand_total += report['discovery']['candidates']
        require(summary['sourceRevisionCandidates'] == grand_total, 'Wrong global source total')
        link_count = summary['codeAssociationCandidates']
        require(set(retained['matchedFormalIds']['airportIds']) <= airports, 'Missing airport match')
        require(set(retained['matchedFormalIds']['assignmentIds']) <= assignments, 'Missing assignment match')
        require(set(retained['matchedFormalIds']['nameIds']) <= names, 'Missing name match')
        reviewed_rows = retained['reviewedCandidates']
        require(set(reviewed_rows) == review_ids, 'Orphaned review override; never silently discard curation')
        for cid, row in reviewed_rows.items():
            extra = 'baseline_closed_record' if row['types'] == ['baseline_closed_record'] else None
            require(cid == stable_id('cand_', [row['sourceId'], row['sourceEntityId'], row['changes'], extra]), f'Unstable ID {cid}')
            reviewed = apply_review(row, reviews)['review']
            require(reviewed['status'] in STATUSES, 'Unknown live review status')
            require(reviewed.get('nextAction') and reviewed.get('evidenceGaps'), 'Incomplete live review')
            if reviewed['status'] == 'excluded':
                require(reviewed.get('exclusionReason'), 'Missing live exclusion reason')
        known_ids = set(retained['verifiedBatchCandidateIds']) | set(reviewed_rows) | {r['candidateId'] for r in legacy}

    for _, batch in batch_records:
        for event in batch['events']:
            ids = event['candidateIds'] + event['relatedCandidateIds']
            require(set(ids) <= known_ids, 'Dangling reviewed candidate')
            observation = event.get('sourceObservation')
            if observation:
                raw = reviewed_rows[observation['candidateId']]
                require(all(observation[k] == raw[k] for k in ('sourceId', 'sourceEntityId', 'changes', 'observations')), 'Review altered pinned source transition')
        for follow_up in batch.get('followUps', []):
            require(set(follow_up.get('admittedAirportIds', [])) <= airports, 'Follow-up admits a missing airport')
            require(set(follow_up.get('admittedAssignmentIds', [])) <= assignments, 'Follow-up admits a missing assignment')
            require(set(follow_up.get('admittedNameIds', [])) <= names, 'Follow-up admits a missing name')
        for lead in batch['nextBatch']:
            require(lead['candidateId'] in known_ids, 'Dangling next-batch lead')
    mode = 'full-shards' if not missing_shards else f'manifest-and-excerpts ({len(missing_shards)} shards omitted from Git)'
    print(f'Validated {grand_total:,} source candidates ({mode}), {link_count:,} code-association leads, {len(legacy)} legacy leads; curated data matches the reviewed baseline and preserved earlier records.')
    print(f'Validated {len(batches)} bounded review batch(es), {len(reviews)} live candidate review overrides.')


if __name__ == '__main__':
    main()
