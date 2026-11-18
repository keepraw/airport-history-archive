# Repository Slimming Audit and Git History Cleanup Plan

## Executive Summary

| Metric | Before Cleanup (`f59459a`) | After Phase 4 Working-Tree Cleanup | After Optional Phase 5 History Rewrite |
| --- | ---: | ---: | ---: |
| Tracked working-tree files | 1,293 | 1,066 | 1,066 |
| Tracked working-tree size | **357.01 MiB** | **~58.8 MiB** (**-298.85 MiB / -83.5%**) | **~58.8 MiB** |
| `.git` object database size (packed) | **322.24 MiB** | **~322.3 MiB** (historical blobs retained) | **~24–26 MiB** (**~-297 MiB / -92%**) |
| Formal `data/airports.json` (`0.12.0`) | 46 airports / 55 assignments | Byte-for-byte unchanged | Byte-for-byte unchanged |

This audit executes Phases 1–4 in full on the current branch and provides an explicit, safe execution plan for Phase 5 (`git filter-repo`) without rewriting `main` history behind the scenes.

---

## Phase 1: Working-Tree Inventory and Script Dependency Audit

All 1,293 tracked files (374,346,609 bytes / 357.01 MiB) at `origin/main` (`f59459a`) were inventoried by role and script dependency:

| Path Group | Size | Tracked Role | Dependent Scripts / Workflows | Disposition |
| --- | ---: | --- | --- | --- |
| `data/airports.json`, `schema/`, `src/` | 0.18 MiB | **Formal production dataset & resolver** | `src/resolve.ts`, `src/validate.ts`, all admission gates | **Retain in Git** |
| `reference/generated/*` (`records.0..f.jsonl.gz`, `manifest.json`, `sources.json`) | 20.57 MiB | **Executor-bound baseline reference index** | `scripts/reference/query.py` (SHA-256 pinned in `policy_executor.py`), `pipeline.py`, `public_data.py`, `bulk/worldwide.py` | **Retain in Git** (required by cryptographic executor fingerprint) |
| `reference/inputs/ourairports.csv.gz`, `reference/source-lock.json` | 3.62 MiB | **Admission-policy locked snapshot** | `research/admission/source-claims-v1/policy.json` (`0.11.0`), `scripts/reference/validate.py` | **Retain in Git** |
| `research/evidence/inputs/*` + `source-lock.json` | 1.05 MiB | **Locked primary US BTS/FAA originals** | `scripts/evidence/pipeline.py::load_locked`, `validate-schema.ts` | **Retain in Git** |
| `research/admission/**`, `research/evidence/{first-admission,global-batch,major-markets,market-transfers,priority-markets,policy-pilot,global-iata-forensics,global-code-next,code-dates}/**` | ~31.8 MiB | **Source locks, bounded excerpts, admission grants, and reviewed research conclusions** | `policy_gate.py`, `first_admission.ts`, `global_batch.py`, `major_markets.py`, `market_transfers.py`, `priority_markets.py`, `legacy_replay.py` | **Retain in Git** |
| `research/discovery/generated/*.jsonl.gz` (142 files at the PR base) | **193.72 MiB** | Regenerable global directory scan shards (`*.candidates.*`, `*.entities.*`, `*.versions.*`, `*.gaps.*`, `code-links`, `duplicate-groups`) | `scripts/discovery/validate.py`, `scripts/discovery/query.py`, `scripts/reference/validate.py`, `bulk/worldwide.py` | **Remove from Git** (`work/discovery/generated/` on demand; retain `manifest.json`, `*.coverage.json`, `summary.json`, `reviewed-observations.json`) |
| `research/evidence/direct/{inputs,texts}/*` (32 files) | **52.03 MiB** | Large raw PDFs/CSVs/HTMLs and full `pdftotext` dumps already hash-locked in `source-lock.json` | `scripts/evidence/direct.py`, `scripts/evidence/admitted.py` | **Remove from Git** (`work/evidence/direct/` on demand; retain `source-lock.json`, `excerpt-lock.json`, `excerpts/*.json`, `assessments.json`) |
| `research/evidence/global-code-expansion/*.jsonl.gz` (51 files at the PR base) | **21.78 MiB** | 47 ranked-event shards and four compact indexes | `scripts/evidence/global_code_screen.py`, `scripts/evidence/global_code_audit.py` | Keep the four [compact indexes](#compact-index-retention) and existing manifests in Git. Stage large ranking shards under `work/global-code-expansion/` on demand. |
| `research/evidence/global-public-data/*.jsonl.gz` (excl. `faa-admission-candidates.jsonl.gz`) + `proposed-data.json` + `resolver-query-codes.json` (21 files) | **20.07 MiB** | Global Wikidata/OSM entity, revision, crosswalk, and candidate shards + deterministically reconstructible `proposed-data.json` | `scripts/evidence/public_data.py` | **Remove from Git** (retain `source-lock.json`, `faa-source-lock.json`, `faa-admission-candidates.jsonl.gz`, `artifact-manifest.json`, `coverage-report.json`) |
| `reference/triage/groups.jsonl.gz` (1 file) | **7.66 MiB** | Regenerable 88,330-group mechanical triage index | `scripts/reference/validate.py`, `scripts/evidence/pipeline.py`, `bulk/worldwide.py` | **Remove from Git** (retain `manifest.json`, `metrics.json`, `code-reuse-leads.jsonl.gz`) |
| `research/evidence/generated/*.jsonl.gz` (5 files) | **6.59 MiB** | Mechanical observation/match/review-packet streams | `scripts/evidence/pipeline.py`, `scripts/evidence/validate-schema.ts` | **Remove from Git** (`observations.jsonl.gz` materializes into `work/evidence/generated/` in ~1s from retained `research/evidence/inputs/*`) |

---

## Phase 2: Minimal Retention Set & Provenance Preservation

To guarantee zero loss of historical evidence provenance while removing 298.85 MiB of intermediate/raw data:

1. **Cryptographic locks preserved:** Every `source-lock.json`, `faa-source-lock.json`, `manifest.json`, `artifact-manifest.json`, `jsonl-shards.json`, `shard-reconstruction.json`, and `test/curated-*.json` baseline remains tracked in Git with original SHA-256 digests intact.
2. **Bounded provenance excerpts added (~0.60 MiB total):**
   - `research/discovery/generated/reviewed-observations.json` (`103,826` bytes): pins all 55 `reviews.json` candidate records, batch candidate IDs, and formal ID matches against `manifest.json`.
   - `research/evidence/direct/excerpt-lock.json` + 16 `research/evidence/direct/excerpts/<sourceId>.json` files (`66,631` bytes): pins minimal attributed quotes and exact page/line/row locators reproducing all 35 `assessments.json` facts and all `0.8.0` formal admission citations with zero locator drift.
   - `research/evidence/global-code-expansion/studied-ranking-index.json` (`453,205` bytes): pins the 335 canonical and related ranked-event entries audited by regional transfer assessments.

---

## Phase 3 & Phase 4: Script Updates and Current-Tree Cleanup

- **252 tracked files (313,364,751 bytes / 298.85 MiB)** were removed from the Git index and working tree via `git rm`.
- Validators and build scripts (`scripts/discovery/validate.py`, `scripts/discovery/query.py`, `scripts/reference/validate.py`, `bulk/worldwide.py`, `scripts/evidence/direct.py`, `scripts/evidence/admitted.py`, `scripts/evidence/pipeline.py`, `scripts/evidence/validate-schema.ts`, `scripts/evidence/global_code_screen.py`, `scripts/evidence/global_code_audit.py`, `scripts/evidence/public_data.py`, and `scripts/evidence/legacy_replay.py`) now resolve large streams from ignored `work/` when staged locally and verify cryptographic manifests, retained bounded excerpts, and reconstructed datasets on clean CI checkouts.
- None of the 20 files fingerprinted by `scripts/evidence/policy_executor.py` were modified.

### Compact index retention

The exact PR base is `f59459ac3e11d7e19b26db9612acf6a10b556309`.
The four indexes below were restored from that commit. Their combined size is
932,744 bytes (0.89 MiB). The SHA-256 values cover the compressed bytes in
`research/evidence/global-code-expansion/`.

| Index | SHA-256 |
| --- | --- |
| `high-value-queue.jsonl.gz` | `2ca7cbba3afda33b234244d9416c2a1af36a7a91c36c1126b831de6eb2666c8d` |
| `remaining-high-value-queue.jsonl.gz` | `4052dde0591e04039cbb14332b81778087ff43c68b1f88079d2b9ed8611fe97c` |
| `ranked-code-links.jsonl.gz` | `fb8b9b1c4b313f4d801e9e529cfa4707f8bab48a363aae211f1baafe141f9fda` |
| `ranked-reuse-leads.jsonl.gz` | `ab96efc36a94b44db5058abfb696ee70cb4ef79f25fd38a962a7309038563c73` |

### Assets absent from the follow-up checkout

The ignored repository `work/` directory was absent at handoff. Validation
created temporary build outputs there. The inherited cache and original
archives were unavailable. The retained source locks identify each original
by URL and hash.

- The PR still omits ranked-event shards `ranked-events.000.jsonl.gz`
  through `ranked-events.046.jsonl.gz` and all 142 discovery JSONL shards
  present at the base.
- Direct evidence omits the 16 originals in `research/evidence/direct/inputs/`
  and the matching 16 extractions in `research/evidence/direct/texts/`.
  The existing lock records the exact originals and extract paths.
  [Direct evidence lock](../research/evidence/direct/source-lock.json)
- The public-data cache lacks both FAA NASR airport ZIPs, dated 2026-10-01
  and 2026-10-29, including their `APT_BASE.csv` members. The source lock
  records the archive and member hashes for each edition.
  [FAA archive lock](../research/evidence/global-public-data/faa-source-lock.json)
- The remaining base-only files also include the 21 public-data projections
  and generated outputs, five evidence streams and
  `reference/triage/groups.jsonl.gz`. The exact list of every base path
  absent from the branch can be reproduced from Git.

```sh
git diff --name-only --diff-filter=D f59459ac3e11d7e19b26db9612acf6a10b556309 HEAD
```

At handoff there were also 604 unavailable private original, extracted-text and
normalized-text paths explicitly named in the tracked research records.
The exact paths in those fields can be listed without acquiring any originals.

```sh
git grep -h -E '"private(Original|ExtractedText|NormalizedText)Path": "work/' -- research |
  sed -E 's/.*": "(work\/[^"]+)".*/\1/' |
  sort -u
```

---

## Phase 5: Git History Bloat Evaluation and Explicit Rewrite Plan

### 1. Current `.git` Object Measurements

Even after deleting 298.85 MiB from the current tree, Git retains every historical blob reachable from prior commits on `main`:

- **Current `.git` directory size:** **322.24 MiB**
- **Reachable packed Git objects (`git rev-list --objects --all`):** **321.97 MiB** compressed (**368.60 MiB** uncompressed)
  - Blobs removed from `HEAD` in Phase 4 but still referenced by historical commits (`PR #5` through `PR #37`): **298.85 MiB**
  - Earlier superseded non-`HEAD` historical blobs (484 objects): **1.06 MiB**
  - Retained `HEAD` blobs + commit/tree metadata: **~22.1 MiB** compressed
- **Savings from Phase 4 (`git rm`) alone:**
  - Working-tree / shallow checkout (`--depth 1`) / archive tarball: **-298.85 MiB** (**357.01 MiB -> ~58.8 MiB**)
  - Full `git clone` history transfer: **0 MiB** (remains **~322 MiB** until history rewrite)
- **Projected `.git` size after `git filter-repo` + `git gc --prune=now --aggressive`:** **~24–26 MiB** (**~297 MiB** saved).

### 2. Why History Rewrite Was NOT Executed Automatically

Per user instructions and `AGENTS.md` (*"does not authorize automatic merges or rewriting earlier merge commits"*), rewriting `main` requires explicit Owner sign-off and a coordinated maintenance window because:

1. **Force-push impact:** Rewriting history alters every commit SHA from the first discovery commit (`PR #5`) through `HEAD`, requiring `git push --force-with-lease origin main` (temporarily unlocking branch protection on `main` and invalidating open forks/worktrees).
2. **Pinned `BASE_COMMIT` SHA constants in repository scripts:** Six verification/replay scripts and several research manifests pin exact historical commit SHAs that must be remapped using `.git/filter-repo/commit-map` immediately after filtering:
   - `scripts/evidence/legacy_replay.py` (`BASE = '1e35d424a42377ea80c5c4ab53e1ee3d492b5acf'`)
   - `scripts/evidence/public_data.py` (`bb1046455e949c6c0bf3a18769464cb232bec19e`)
   - `scripts/evidence/global_code_admission.py` (`BASE_COMMIT`)
   - `scripts/evidence/history_audit.py` (`PR17_HEAD`, `PR24_MERGE`)
   - `scripts/evidence/priority_market_archive.py` & `scripts/evidence/admitted_090.py`
   - `baseCommit` / `baselineCommit` fields in `research/**/manifest.json` and `source-lock.json`

### 3. Safe Execution Plan (Run Only After Owner Approval)

1. **Archive pre-rewrite backup bundle (outside Git):**
   ```sh
   git bundle create ../airport-history-pre-filter-backup.bundle --all
   ```
2. **Strip only the 6 verified regenerable/raw path globs via `git filter-repo`:**
   ```sh
   git filter-repo \
     --invert-paths \
     --path-glob 'research/discovery/generated/*.jsonl.gz' \
     --path-glob 'research/evidence/direct/inputs/*' \
     --path-glob 'research/evidence/direct/texts/*' \
     --path-glob 'research/evidence/global-code-expansion/ranked-events.*.jsonl.gz' \
     --path 'research/evidence/global-code-expansion/ranked-events.jsonl.gz' \
     --path-glob 'research/evidence/global-public-data/wikidata-*.jsonl.gz' \
     --path-glob 'research/evidence/global-public-data/osm-*.jsonl.gz' \
     --path-glob 'research/evidence/global-public-data/bts-*.jsonl.gz' \
     --path-glob 'research/evidence/global-public-data/faa-nasr-*.jsonl.gz' \
     --path-glob 'research/evidence/global-public-data/global-crosswalk*.jsonl.gz' \
     --path-glob 'research/evidence/global-public-data/historical-code-candidates*.jsonl.gz' \
     --path-glob 'research/evidence/global-public-data/physical-reuse-candidates.jsonl.gz' \
     --path-glob 'research/evidence/global-public-data/unmatched-wikidata-entities.jsonl.gz' \
     --path 'research/evidence/global-public-data/proposed-data.json' \
     --path 'research/evidence/global-public-data/resolver-query-codes.json' \
     --path 'reference/triage/groups.jsonl.gz' \
     --path-glob 'research/evidence/generated/*.jsonl.gz'
   ```
3. **Remap pinned `BASE_COMMIT` constants** in the 6 scripts above using `.git/filter-repo/commit-map` in a single `keepraw`-authored follow-up commit; verify `data/airports.json` and all retained `source-lock.json` / `excerpts/` files are byte-identical to pre-filter `HEAD`.
4. **Re-run full CI suite locally**, then coordinate a scheduled `git push --force-with-lease origin main`.
