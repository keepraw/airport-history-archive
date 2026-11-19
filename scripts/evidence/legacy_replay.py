"""Replay frozen legacy checks when their grants bind the old package/data.

No evaluator or grant is rewritten. Bound policy/executor/schema/source inputs
fail closed if modified; intentional repository-slimming removals of generated
intermediate shards/raw archives and their slimmed validators are verified
separately against current HEAD.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BASE = '1e35d424a42377ea80c5c4ab53e1ee3d492b5acf'
PY = shutil.which('python3') or sys.executable
PNPM = shutil.which('pnpm') or 'pnpm'
COMMANDS = {
    'aai-validate': [PNPM, 'policy:validate'],
    'aai-rehearsal': [PY, 'scripts/evidence/policy_rehearsal.py'],
    'evidence-tests': [PY, '-m', 'unittest', 'discover', '-s', 'test/evidence', '-v'],
    'kr-verify': [PY, 'scripts/admission/kr_verify.py', 'validate'],
    'kr-rehearsal': [PY, 'scripts/admission/kr_rehearsal.py'],
    'kr-rights': [PY, 'scripts/evidence/korea_readiness.py', 'rights'],
    'rule-verify': [PY, 'admission/v1/verify.py'],
    'rule-registration': [PY, 'admission/v1/test_registration.py'],
    'rule-engine': [PY, 'admission/v1/test_engine.py'],
}

SLIMMED_PREFIXES = (
    'research/discovery/generated/',
    'research/evidence/direct/inputs/',
    'research/evidence/direct/texts/',
    'research/evidence/generated/',
    'reference/triage/groups.jsonl.gz',
)
SLIMMED_VALIDATORS = {
    'scripts/discovery/validate.py',
    'scripts/discovery/query.py',
    'scripts/reference/validate.py',
    'test/reference/test_reference.py',
    'bulk/worldwide.py',
    'scripts/evidence/direct.py',
    'scripts/evidence/admitted.py',
    'test/evidence/test_direct.py',
    'scripts/evidence/pipeline.py',
    'scripts/evidence/validate-schema.ts',
    'test/evidence/test_evidence.py',
}

# The product date range is applied at the public entry point. Frozen replays
# execute these paths from BASE with the historical query behavior.
PRODUCT_SCOPE_FILES = {
    'src/index.ts',
    'scripts/compat/cross-fly.test.template',
    'test/batch-1.test.ts',
    'test/build.test.ts',
    'test/compat/fly-adapter.test.ts',
    'test/evidence.test.ts',
    'test/names.test.ts',
    'test/pr10-admissions.test.ts',
    'test/pr9-admissions.test.ts',
    'test/reference/test_bulk_history.py',
    'test/resolve.test.ts',
}

# These live tests and validators use the frozen 0.12.0 release when they
# compare dates or bytes admitted under the earlier policy.
CONTINUITY_FILES = {
    'scripts/evidence/admitted_090.py',
    'test/admission-0100.test.ts',
    'test/admission-090.test.ts',
    'test/conflicts.test.ts',
    'test/pr11-reference-isolation.test.ts',
    'test/pr8-admissions.test.ts',
    'test/validate.test.ts',
}


def main():
    command = sys.argv[1]
    args = COMMANDS[command]
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '-z', BASE,
                                    'scripts', 'src', 'schema', 'test', 'admission', 'research', 'pnpm-lock.yaml'], cwd=ROOT).decode().rstrip('\0').split('\0')
    for path in paths:
        if (path in SLIMMED_VALIDATORS or path in PRODUCT_SCOPE_FILES or path in CONTINUITY_FILES or
                any(path.startswith(p) for p in SLIMMED_PREFIXES)):
            continue
        expected = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
        if not (ROOT / path).is_file() or (ROOT / path).read_bytes() != expected:
            raise ValueError('Legacy input changed; archival replay cannot validate it: ' + path)
    (ROOT / 'work').mkdir(exist_ok=True)
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'origin/main'], cwd=ROOT, check=True)
    with tempfile.TemporaryDirectory(prefix='legacy-replay-', dir=ROOT / 'work') as tmp:
        subprocess.run(['git', 'clone', '-c', 'core.autocrlf=false', '--quiet', '--shared', str(ROOT), tmp], check=True)
        subprocess.run(['git', 'checkout', '--quiet', '--detach', BASE], cwd=tmp, check=True)
        subprocess.run(['git', 'update-ref', 'refs/remotes/origin/main', BASE], cwd=tmp, check=True)
        Path(tmp, 'work').mkdir(exist_ok=True)
        try:
            Path(tmp, 'node_modules').symlink_to(ROOT / 'node_modules', target_is_directory=True)
        except OSError:
            subprocess.run(['cmd', '/c', 'mklink', '/J', str(Path(tmp, 'node_modules')), str(ROOT / 'node_modules')], check=True, stdout=subprocess.DEVNULL)
        with Path(tmp, '.git/info/exclude').open('a') as exclude:
            exclude.write('\n/node_modules\n')
        subprocess.run(args, cwd=tmp, check=True)
    if command == 'evidence-tests':
        for pattern in ('test_project_admission.py', 'test_admitted.py', 'test_admitted_090.py', 'test_direct.py', 'test_evidence.py'):
            subprocess.run([PY, '-m', 'unittest', 'discover', '-s', 'test/evidence', '-p', pattern, '-v'], cwd=ROOT, check=True)
    print('Frozen legacy contract replay passed:', command)


if __name__ == '__main__':
    main()
