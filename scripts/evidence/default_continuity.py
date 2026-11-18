"""Build and validate the owner-authorized passenger-airport continuity admission."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'reference'))
from common import ROOT, checked, digest, distance, position, read_jsonl

DIRECTORY = ROOT / 'research/admission/default-continuity-v1'
RELEASE = ROOT / 'research/admissions/0.13.0'
POLICY = DIRECTORY / 'policy.json'
EXCEPTIONS = DIRECTORY / 'exceptions.json'
BASE = ROOT / 'test/curated-0.12.0.json'
FORMAL = ROOT / 'data/airports.json'
SOURCE = 'continuity-current-ourairports'
AUTHORITY = 'owner-default-continuity-v1'
TIMEZONES = 'continuity-reference-timezones'
FIELDS = {'IATA': 'iata_code', 'ICAO': 'icao_code'}
PATTERNS = {'IATA': re.compile('[A-Z]{3}'), 'ICAO': re.compile('[A-Z]{4}')}
LAND = {'large_airport', 'medium_airport', 'small_airport'}
LARGE_REGIONAL = {'large_airport', 'medium_airport'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def code_at(row, scheme):
    value = row[FIELDS[scheme]]
    return value if PATTERNS[scheme].fullmatch(value) else None


def coordinates(row):
    return position(row['latitude_deg'], row['longitude_deg'])


def bts_sites():
    sites = defaultdict(list)
    path = ROOT / 'research/evidence/inputs/bts-master.csv.gz'
    with gzip.open(path, 'rt', encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            coord = position(row['LATITUDE'], row['LONGITUDE'])
            if coord is not None:
                sites[row['AIRPORT'], row['AIRPORT_COUNTRY_CODE_ISO']].append(coord)
    return sites


def passenger_tier(row, bts):
    kind, scheduled = row['type'], row['scheduled_service'] == 'yes'
    if scheduled and kind in LAND | {'seaplane_base'}:
        return 'scheduled'
    iata = code_at(row, 'IATA')
    if kind in LARGE_REGIONAL and iata:
        return 'regional'
    if kind == 'small_airport' and iata and code_at(row, 'ICAO'):
        coord = coordinates(row)
        if coord is not None and any(distance(coord, other) <= 1 for other in bts[iata, row['iso_country']]):
            return 'regional'
    return None


def inventory(aliases, exclusions):
    lock = load(ROOT / 'reference/source-lock.json')
    raw = gzip.decompress((ROOT / 'reference/inputs/ourairports.csv.gz').read_bytes())
    require(sha256(raw).hexdigest() == lock['sha256'], 'Pinned OurAirports CSV changed')
    with io.StringIO(raw.decode('utf-8'), newline='') as stream:
        rows = list(csv.DictReader(stream))
    by_id = {row['id']: row for row in rows}
    require(len(rows) == len(by_id) == lock['records'], 'Invalid reference population')
    bts = bts_sites()
    eligible = {key: tier for key, row in by_id.items() if (tier := passenger_tier(row, bts))}
    for alias, spec in aliases.items():
        canonical = spec['canonicalReferenceId']
        require(alias in eligible and canonical in eligible and canonical not in aliases,
                f'Invalid duplicate-site binding: {alias} / {canonical}')
        a, b = by_id[alias], by_id[canonical]
        separation = distance(coordinates(a), coordinates(b))
        require(a['iso_country'] == b['iso_country'] and separation is not None and separation <= 1
                and all(code_at(a, scheme) in (None, code_at(b, scheme)) for scheme in FIELDS),
                f'Duplicate-site binding failed the pinned identity check: {alias}')
        del eligible[alias]
    excluded = {key: {**exclusions[key], 'name': by_id[key]['name'], 'screenedTier': eligible.pop(key, None)}
                for key in exclusions}
    current_codes = defaultdict(set)
    for key, row in by_id.items():
        if key not in aliases and key not in exclusions and row['type'] in LAND | {'seaplane_base', 'heliport'}:
            for scheme in FIELDS:
                code = code_at(row, scheme)
                if code:
                    current_codes[scheme, code].add(key)
    return by_id, eligible, excluded, current_codes


def retained_screen(references, eligible, reviewed):
    codes = {(scheme, code_at(references[key], scheme)) for key in eligible for scheme in FIELDS}
    directory = ROOT / 'research/evidence/global-code-expansion'
    indexes = {
        'ranked-reuse-leads': ('historicallyVerified',),
        'ranked-code-links': ('historicallyVerified',),
        'high-value-queue': ('relocationProven', 'formalAdmission'),
        'remaining-high-value-queue': ('formalCoverageClaimed',),
    }
    report = {}
    for name, flags in indexes.items():
        counts = dict(rows=0, matchingCodes=0, matchingReviewedCases=0, affirmativeRows=0)
        for row in read_jsonl(directory / (name + '.jsonl.gz')):
            keys = {(row['scheme'], row['code'])} if 'scheme' in row else {
                (scheme, code) for scheme in FIELDS for code in row[scheme]
            }
            counts['rows'] += 1
            counts['matchingCodes'] += bool(keys & codes)
            counts['matchingReviewedCases'] += bool(keys & reviewed)
            if any(row[flag] is True for flag in flags):
                counts['affirmativeRows'] += 1
                require(not (keys & codes) or keys & reviewed,
                        f'Unreviewed current code in affirmative evidence: {name}: {keys}')
        report[name] = counts
    return report


def timezones(sites):
    root = ROOT / 'reference/generated'
    manifest = load(root / 'manifest.json')
    result = {}
    for suffix in '0123456789abcdef':
        name = f'records.{suffix}.jsonl.gz'
        checked(root / name, manifest['files'][name]['sha256'])
        for row in read_jsonl(root / name):
            if row['presentAtSnapshot'] and row['sourceEntityId'] in sites and row['timezone']:
                result[row['sourceEntityId']] = row['timezone']
    return result


def fact(value, source, note):
    return {'value': value, 'status': 'reference' if value is not None else 'unknown',
            'sourceIds': [source] if value is not None else [], 'note': note}


def permanent_id(reference_id):
    # Derive a stable v4 ID for genuinely new sites from the pinned identity
    # anchor. Future admissions reuse the formal mapping before minting any IDs.
    anchor = f'keepraw/airport-history/ourairports/d97df1673cc5ba61a/{reference_id}'
    return 'apt_' + str(uuid.UUID(bytes=sha256(anchor.encode()).digest()[:16], version=4))


def airport(row, zone, airport_id):
    return {
        'airportId': airport_id,
        'externalIds': {'ourAirports': row['id']},
        'name': fact(row['name'], SOURCE, 'Reference display name.'),
        'coordinates': fact(coordinates(row), SOURCE, 'Pinned WGS84 physical-site reference.'),
        'timezone': fact(zone, TIMEZONES, 'Pinned reference IANA timezone.' if zone else 'No uniquely matched pinned timezone.'),
    }


def lower(cutoff):
    return {'earliest': None, 'latest': cutoff, 'precision': 'unknown'}


def upper(exclusive):
    return {'earliest': exclusive, 'latest': None, 'precision': 'unknown'}


def formal_source(source_id, title, url, checked_on, source_type, note, license_id, license_url=None):
    return {'sourceId': source_id, 'title': title, 'url': url, 'accessedOn': checked_on,
            'sourceType': source_type, 'verificationStatus': 'verified', 'note': note,
            'license': {'id': license_id, 'url': license_url, 'note': 'Scoped factual attribution. See the evidence register.'}}


def policy_sources(policy):
    lock = load(ROOT / 'reference/source-lock.json')
    tz = load(ROOT / 'reference/generated/sources.json')['airportsdata']
    return [
        formal_source(SOURCE, 'Pinned OurAirports physical airport and typed code snapshot', lock['downloadUrl'],
                      lock['observedAt'][:10], 'secondary',
                      'Current association from the row identified by externalIds.ourAirports. IATA and ICAO use their own columns.',
                      'LicenseRef-Public-Domain', lock['licenseUrl']),
        formal_source(TIMEZONES, 'Pinned airportsdata timezone references',
                      f"{tz['url']}/blob/{tz['revision']}/{tz['path']}", tz['observedAt'][:10], 'secondary',
                      'Timezone only. The reference index matched identifier, country and coordinates.',
                      'MIT', f"{tz['url']}/blob/{tz['revision']}/LICENSE"),
        formal_source(AUTHORITY, 'Keepraw owner default historical continuity policy v1',
                      'https://github.com/keepraw/airport-history/pull/39', policy['authorization']['recordedOn'], 'primary',
                      'Policy and exact owner authority recorded in research/admission/default-continuity-v1/policy.json.',
                      'MIT'),
    ]


def assignment(existing, site, scheme, code, start, end, sources, note, date_reviewed):
    if existing is None:
        anchor = site['externalIds'].get('ourAirports', site['airportId'])
        existing = {'assignmentId': f'continuity-{scheme.lower()}-{code.lower()}-{anchor}'}
    return {**existing, 'airportId': site['airportId'], 'scheme': scheme, 'code': code,
            'validFrom': start, 'validTo': end, 'evidenceType': 'continuity_inference',
            'verificationStatus': 'verified', 'verifiedOn': date_reviewed, 'note': note,
            'sourceIds': list(dict.fromkeys([*existing.get('sourceIds', []), AUTHORITY, *sources]))}


def identities(base, references, eligible, exceptions, issues):
    by_reference = {airport['airportId']: airport for airport in base['airports']}
    for existing in base['airports']:
        key = existing['externalIds'].get('ourAirports')
        if key:
            require(key not in by_reference, f'Duplicate formal physical binding: {key}')
            by_reference[key] = existing
    planned = {site for site, spec in exceptions['currentPopulationExclusions'].items()
               if spec['reason'] == 'under_construction'}
    extra = {str(site) for case in exceptions['cases'] for site in case['sites']} - planned
    require(all(site.isdecimal() or site in by_reference for site in extra), 'Unknown inherited physical site')
    extra = {site for site in extra if site.isdecimal()}
    zones = timezones(set(eligible) | extra)
    reserved = exceptions['priorIdentityBindings']
    occupied = set(a['airportId'] for a in base['airports'])
    added = []
    for key in sorted(set(eligible) | extra, key=int):
        if key not in references:
            require(key not in extra, f'Unknown reviewed physical site {key}')
            issues[key].append('missing_reference')
            continue
        row = references[key]
        coord = coordinates(row)
        if not coord or not row['name'].strip() or not re.fullmatch('[A-Z]{2}', row['iso_country']):
            require(key not in extra, f'Invalid reviewed identity {key}')
            issues[key].append('invalid_physical_identity')
            continue
        prior = by_reference.get(key)
        if prior:
            separation = distance(prior['coordinates']['value'], coord)
            reconciliation = exceptions.get('locationReconciliations', {}).get(key)
            confirmed = reconciliation is not None and reconciliation['airportId'] == prior['airportId'] and (
                reconciliation['icao'] == code_at(row, 'ICAO')
            ) and any(a['airportId'] == prior['airportId'] and a['scheme'] == 'ICAO' and
                      a['code'] == reconciliation['icao'] for a in base['assignments'])
            if (separation is None or separation > 1) and not confirmed:
                require(key not in extra, f'Reviewed site disagrees with permanent identity {key}')
                issues[key].append('permanent_identity_location_mismatch')
            continue
        airport_id = reserved.get(key, permanent_id(key))
        require(airport_id not in occupied, f'Duplicate permanent ID: {airport_id}')
        occupied.add(airport_id)
        record = airport(row, zones.get(key), airport_id)
        by_reference[key] = record
        added.append(record)
    return by_reference, added


def bounds_pair(spec, start, end):
    return spec.get('validFrom', start), spec.get('validTo', end)


def build(policy, exceptions):
    aliases = exceptions['siteAliases']
    exclusions = exceptions['currentPopulationExclusions']
    cases = {case['case']: set(case['sites']) for case in exceptions['cases']}
    require(all(key in cases[spec['case']] for key, spec in exclusions.items()),
            'Current population exclusion needs a reviewed physical site')
    references, eligible, excluded, current_codes = inventory(aliases, exclusions)
    from_date, end_date = policy['queryHorizon']['fromInclusive'], policy['queryHorizon']['toExclusive']
    start, end = lower(from_date), upper(end_date)
    review_date = policy['authorization']['recordedOn']
    frozen = load(BASE)
    issues = defaultdict(list)
    sites, added = identities(frozen, references, eligible, exceptions, issues)
    assignments = {a['assignmentId']: a for a in frozen['assignments']}
    relationships = {(a['airportId'], a['scheme'], a['code']): a for a in assignments.values()}
    require(len(relationships) == len(assignments), 'Unexpected repeated baseline relation')
    old_codes = defaultdict(list)
    for row in assignments.values():
        old_codes[row['scheme'], row['code']].append(row)
    handled = set()
    default_ids = []
    exception_ids = {}
    for case in exceptions['cases']:
        selected = []
        for spec in case.get('assignments', []):
            key, scheme, code = str(spec['site']), spec['scheme'], spec['code']
            require(key in {str(s) for s in case['sites']}, f'Unreviewed site in {case["case"]}')
            require(PATTERNS[scheme].fullmatch(code), f'Invalid reviewed code: {scheme}:{code}')
            relation = key, scheme, code
            require(relation not in handled, f'Repeated review: {relation}')
            handled.add(relation)
            site = sites[key]
            old = relationships.get((site['airportId'], scheme, code))
            if spec.get('usePriorBounds'):
                require(old is not None, f'Missing inherited bounds: {relation}')
                before, after = bounds_pair(spec, old['validFrom'], old['validTo'])
            else:
                before, after = bounds_pair(spec, start, end)
            row = assignment(old, site, scheme, code, before, after, spec['sources'],
                             f"Owner continuity policy v1. {case['case']}. {spec['note']}", review_date)
            require(row['assignmentId'] not in assignments or old is not None, 'Repeated assignment ID')
            assignments[row['assignmentId']] = row
            selected.append(row['assignmentId'])
        for item in case.get('holds', []):
            key, scheme, code = str(item['site']), item['scheme'], item['code']
            require(key in sites or key in excluded, f'Unknown held site: {key}')
            relation = key, scheme, code
            require(relation not in handled, f'Both held and admitted: {relation}')
            handled.add(relation)
            issues[key].append(f'{scheme}:{code} {item["reason"]}')
        exception_ids[case['case']] = selected

    for key in sorted(eligible, key=int):
        if key not in sites or 'permanent_identity_location_mismatch' in issues[key]:
            continue
        row, site = references[key], sites[key]
        for scheme in FIELDS:
            code = code_at(row, scheme)
            if code is None:
                issues[key].append(f'{scheme} missing_typed_current_code')
                continue
            if (key, scheme, code) in handled:
                continue
            if len(current_codes[scheme, code]) != 1:
                issues[key].append(f'{scheme}:{code} competing_current_physical_rows')
                continue
            old = relationships.get((site['airportId'], scheme, code))
            competitors = [a for a in old_codes[scheme, code] if a['airportId'] != site['airportId']]
            if any(a['validTo']['latest'] is None or a['validTo']['latest'] > from_date for a in competitors):
                issues[key].append(f'{scheme}:{code} competing_reviewed_historical_site')
                continue
            if old and old['validTo']['latest'] is not None:
                issues[key].append(f'{scheme}:{code} reviewed_withdrawal_requires_new_evidence')
                continue
            record = assignment(old, site, scheme, code, start, end, [SOURCE],
                                f'Owner continuity policy v1. Current {scheme} from typed OurAirports row {key}.',
                                review_date)
            assignments[record['assignmentId']] = record
            default_ids.append(record['assignmentId'])

    new_sources = [*policy_sources(policy), *exceptions['sources']]
    require(not set(s['sourceId'] for s in new_sources) & {s['sourceId'] for s in frozen['sources']},
            'An inherited source record would be replaced')
    dataset = {**frozen, 'dataVersion': policy['dataVersion'], 'airports': [*frozen['airports'], *added],
               'assignments': list(assignments.values()), 'sources': [*frozen['sources'], *new_sources]}
    historical = {sites[str(key)]['airportId']: sites[str(key)]['name']['value']
                  for case in exceptions['cases'] for key in case.get('historicalSites', [])}
    summary = {
        'eligible': {key: {'tier': tier, 'name': references[key]['name'],
                           'airportId': sites[key]['airportId'] if key in sites else None,
                           'codes': {scheme: code_at(references[key], scheme) for scheme in FIELDS},
                           'issues': issues[key]} for key, tier in eligible.items()},
        'baselineAssignmentIds': default_ids,
        'exceptionAssignmentIds': exception_ids,
        'duplicateReferenceRows': aliases,
        'excludedCurrentReferenceRows': excluded,
        'retainedEvidenceScreen': retained_screen(references, eligible, {(scheme, code) for _, scheme, code in handled}),
        'historicalSites': [{'airportId': key, 'name': name} for key, name in sorted(historical.items())],
    }
    return dataset, summary


def encode_dataset(dataset):
    # One interval or physical record per line keeps the formal dataset reviewable.
    fields = []
    for key, value in dataset.items():
        label = '  ' + json.dumps(key) + ': '
        if isinstance(value, list):
            lines = [json.dumps(row, ensure_ascii=False, separators=(',', ':'), sort_keys=True) for row in value]
            label += '[\n    ' + ',\n    '.join(lines) + '\n  ]'
        else:
            label += json.dumps(value)
        fields.append(label)
    return '{\n' + ',\n'.join(fields) + '\n}\n'


def inherited_assignment_view(current):
    """Compare historical receipts against the frozen release that they admitted."""
    if current['dataVersion'] != '0.13.0':
        return current
    receipt = load(RELEASE / 'coverage.json')['fingerprint']
    checked(FORMAL, receipt['formalSha256'])
    checked(BASE, receipt['baselineSha256'])
    old = load(BASE)['assignments']
    identity = lambda row: (row['airportId'], row['scheme'], row['code'])
    actual = {row['assignmentId']: identity(row) for row in current['assignments']}
    require(all(actual.get(row['assignmentId']) == identity(row) for row in old),
            'A frozen assignment identity was changed or removed')
    return {**current, 'assignments': old}


def run(command):
    policy, exceptions = load(POLICY), load(EXCEPTIONS)
    require(policy['policyId'] == AUTHORITY and policy['dataVersion'] == '0.13.0' and
            policy['authorization']['kind'] == 'explicit-owner-task' and
            policy['authorization']['owner'] == 'keepraw', 'Continuity authority is missing')
    require(policy['queryHorizon'] == load(ROOT / 'src/query-horizon.json'), 'Policy and product date bounds differ')
    for path, expected in policy['inputSha256'].items():
        checked(ROOT / path, expected)
    require(str(BASE.relative_to(ROOT)) in policy['inputSha256'], 'Baseline is not pinned')
    dataset, summary = build(policy, exceptions)
    encoded = encode_dataset(dataset).encode()
    work = ROOT / 'work/default-continuity'
    work.mkdir(parents=True, exist_ok=True)
    published_report = RELEASE / 'coverage.json'
    with tempfile.TemporaryDirectory(dir=work) as tmp:
        scratch = Path(tmp)
        inventory_path = scratch / 'inventory.json'
        inventory_path.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True), encoding='utf-8')
        candidate, report = FORMAL, published_report
        if command == 'build':
            candidate, report = scratch / 'airports.json', scratch / 'coverage.json'
            candidate.write_bytes(encoded)
        else:
            require(FORMAL.read_bytes() == encoded, 'Formal dataset differs from the authorized deterministic admission')
        subprocess.run(['node', 'scripts/evidence/default_continuity_coverage.ts', command,
                        str(candidate), str(inventory_path), str(report)], cwd=ROOT, check=True)
        if command == 'build':
            candidate.replace(FORMAL)
            report.replace(published_report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build', 'validate'))
    run(parser.parse_args().command)
