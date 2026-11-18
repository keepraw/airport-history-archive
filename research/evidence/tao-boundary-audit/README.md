# TAO (Qingdao Liuting) Boundary Regression Audit

## Summary Verdict

`TAO -> Qingdao Liuting International Airport` (`apt_f470ecb5-c6dc-4516-a233-37302da2115b`) is **already formally admitted** in [airports.json](../../../data/airports.json) under `iata-tao-liuting`, resolving **1,821** local dates in `[2016-08-17, 2021-08-12)` (alongside `iata-tao-jiaodong`, which resolves **1,900** local dates in `[2021-08-12, 2026-10-25)`).

Extending `iata-tao-liuting` backward to `[1982-08-05, 2021-08-12)` was audited without rescanning any global database:

| Requirement | Audit Result | Formal Status |
| --- | --- | --- |
| Physical airport identity (`Qingdao Liuting International Airport`) | Proven (`apt_f470ecb5-c6dc-4516-a233-37302da2115b`, OurAirports `27224`, CAAC `cn-stat-2021`) | Already in `data/airports.json` |
| IATA code identity (`TAO`) | Proven (`tao-earlier`, `tao-code`, `tao-transfer`) | Already in `data/airports.json` |
| End boundary `2021-08-12` (`validTo`) | Proven (`2021-08-12` exact local midnight via `tao-code` + `tao-transfer`) | Already in `data/airports.json` |
| Start boundary `1982-08-05` (`validFrom`) | **Unproven as code boundary** (`1982-08-05` is CAAC civil flight reopening at Liuting; pre-1979 Postal *Tsingtao* `TAO` predates Liuting's 1982 civil reopening when Qingdao civil flights used Cangkou Airport in 1946–1949 and 1958–1961) | Held `pending` per admission policy |

## Production Resolver Measurements (`resolveAirport()`)

| Metric | Current `data/airports.json` (`0.12.0`) | Counterfactual `[1982-08-05, 2021-08-12)` | Delta |
| --- | ---: | ---: | ---: |
| Total days in `[1982-08-05, 2021-08-12)` | 14,252 | 14,252 | 0 |
| `resolved` -> Qingdao Liuting in `[1982-08-05, 2021-08-12)` | **1,821** | **14,252** | **+12,431** |
| `uncertain` in `[1982-08-05, 2021-08-12)` (`[1982-08-05, 2016-08-17)`) | 12,431 | 0 | -12,431 |
| `resolved` -> Qingdao Jiaodong in `[2021-08-12, 2026-10-25)` | 1,900 | 1,900 | 0 |
| Total formal `TAO` `resolved` `code/date` queries | **3,721** | **16,152** | **+12,431** |
| Net new formal `resolved` queries written today | **0** | — | — |

## Exact Missing Evidence to Unlock `+12,431` Formal `TAO` Queries

Per `AGENTS.md` Rules 7 & 9 and `research/admission/source-claims-v1/policy.json` (`opening_or_licence_as_code_effective` exclusion), `1982-08-05` cannot be written into `data/airports.json` from airport-reopening chronicles alone. To formally admit the pre-2016 interval, retrieve **one dated primary code-bearing record** (such as a late-1982 CAAC timetable, IATA Coding Administration bulletin, or historical CAAC AIP/AIC binding `TAO` to Qingdao Liuting) and submit for Owner per-record acceptance.
