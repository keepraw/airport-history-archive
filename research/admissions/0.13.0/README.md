# Owner-authorized airport continuity since 2000

The owner authorized a rebuttable presumption of continuity for current
airport-specific codes from 2000-01-01. The public resolver accepts local dates
in `[2000-01-01, 2026-11-19)`. Each verified default assignment uses
`continuity_inference` and cites the owner policy and its pinned current code
field. An airport's IATA and ICAO fields are sourced independently.
[Owner decision](../../admission/default-continuity-v1/policy.json) ·
[Formal dataset](../../../data/airports.json)

## Formal results

| Metric | IATA | ICAO |
| --- | ---: | ---: |
| Formal assignments | 6,370 | 6,214 |
| New assignments over 0.12.0 | 6,342 | 6,187 |
| Unique codes | 6,352 | 6,211 |
| Default continuity assignments | 6,275 | 6,149 |
| Exception assignments | 91 | 60 |
| Newly resolved code/date queries | 61,909,944 | 60,473,220 |

The release contains **6,510 physical airport identities, including 6,464 new
identities**, and records **29 distinct historical predecessors**. The resolver
covers **122,497,566** distinct code/date queries across both namespaces,
including **122,383,164** new results. Default continuity contributes
121,973,223 new results. Evidence-reviewed exceptions contribute 409,941.
Every previously resolved query retains the same physical airport.
[Production coverage receipt](coverage.json)

## Passenger population

The pinned screen starts with 6,488 directory rows. It includes fixed-wing
airports and seaplane bases marked for scheduled service, other medium and
large airports with a typed IATA code, and small airports with both typed
codes and a same-country BTS statistical site within 1 km. The BTS input
corroborates regional relevance and location. The separately typed OurAirports
fields supply the code associations. One duplicate and four screened rows
with documented former service or construction status leave 6,483 eligible
current physical sites.

| Current population | Processed | Resolved on 2026-11-18 |
| --- | ---: | ---: |
| Scheduled | 4,222 | 4,145 |
| Other passenger and regional | 2,261 | 2,261 |
| Total | 6,483 | 6,406 (98.81%) |

The remaining 77 sites lack both typed current codes in the pinned directory.
The receipt lists their names, reference IDs and outstanding claims.
Sites with one admitted scheme count once. Historical predecessor coverage is
measured separately.
[Population detail and unresolved sites](coverage.json)

## Rebuttals and TAO

The register contains 62 case groups. Sixty changed formal intervals, including
nine split groups, 41 bounded groups and ten groups retaining earlier evidence
limits where appropriate. The pre-cutoff review and construction holds have
their own decisions. Boundary notes distinguish operation, observed code use,
and an administrative code-effective date. The compact research indexes were
screened and remain reproducible inputs.
[Exception register](../../admission/default-continuity-v1/exceptions.json) ·
[Measured case results](../../evidence/formal-yield-queue/README.md)

Both IATA TAO assignments use their existing permanent identities. Liuting
resolves on `[2000-01-01, 2021-08-12)`, and Jiaodong on
`[2021-08-12, 2026-11-19)`. The exhaustive TAO replay measures 9,819 resolved
dates, including 6,098 newly resolved dates.
[TAO evidence and boundary probes](../../evidence/tao-boundary-audit/README.md)

## Reproduction

```sh
python3 scripts/evidence/default_continuity.py build
python3 scripts/evidence/default_continuity.py validate
node scripts/evidence/tao_boundary_audit.ts --check
python3 scripts/evidence/rank_by_formal_yield.py --check
pnpm validate:admission
pnpm check
```

The deterministic builder pins the source versions and reviewed exceptions and
validates the result with schema 3.0.0. The coverage check invokes the production
resolver over every span between changes in possible or certain coverage and
counts the span's whole local dates once per scheme and code. Earlier admission
gates replay their frozen releases and the 0.13.0 gate verifies the live output.
The builder uses the pinned local inputs.
