# High-Value Research Queue Ranked by Expected Formal Data Yield

This queue replaces candidate-count / revision-count heuristics with **expected formal `resolved` `code + date -> physical airport` yield** measured against `src/resolve.ts`.

> **Key structural finding:** In `src/resolve.ts`, any assignment with an unbounded side (`validFrom.latest = null` or `validTo.earliest = null`) has an empty `certain` interval and yields **0 `resolved` queries**. Every high-priority task must establish **both** a start bound (`validFrom.latest`) and an end/horizon bound (`validTo.earliest`).

## Ranked Queue

| Rank | Case | Codes | Category | Expected New `resolved` Queries | Missing Docs | Exact Blocker to Formal `data/` |
| ---: | --- | --- | --- | ---: | ---: | --- |
| 1 | `in-blr-hal-kempegowda-transfer` | `IATA:BLR` | `cross_physical_airport_iata_transfer` | **+11,619** | 1 | 1 dated pre-2008 primary BLR code observation at HAL (e.g. DGCA/AAI accident or operational record) to bound HAL's validFrom.latest; Owner per-record claim approval to bind [2008-05-25, 2026-10-25) on Kempegowda (+6,727 immediate days) and pre-2008 window on HAL |
| 2 | `cn-tao-liuting-pre2016-extension` | `IATA:TAO` | `cross_physical_airport_iata_predecessor_extension` | **+12,431** | 1 | 1 dated primary TAO code-use/allocation record at Qingdao Liuting from 1982 (e.g. CAAC late-1982 timetable or CAAC AIP/AIC) + Owner claim acceptance |
| 3 | `tr-ist-ataturk-pre2015-extension` | `IATA:IST` | `cross_physical_airport_iata_predecessor_extension` | **+11,132** | 1 | 1 dated 1980s/1990s primary aviation accident report or official state/airline schedule explicitly binding IST to Ataturk/Yesilkoy + Owner claim acceptance |
| 4 | `us-pbi-djt-kpbi-kdjt-recode` | `IATA:PBI`, `IATA:DJT`, `ICAO:KPBI`, `ICAO:KDJT` | `same_site_iata_and_icao_recode` | **+18,024** | 1 | 1 dated historical primary PBI IATA observation (e.g. NTSB/DOT docket) for pre-2026 PBI start bound; Owner approval of unified UUID apt_eb176a20-e0e3-438d-a330-a7b81185232d and bounded intervals |
| 5 | `cn-relocations-formal-identities-lyg-lzo-ybp` | `IATA:LYG`, `IATA:LZO`, `IATA:YBP` | `cross_physical_airport_iata_transfer_with_formal_ids` | **+10,950** | 3 | Explicit IATA code-transfer notice, airline GDS cutover circular citing LYG/LZO/YBP effective dates, or CAAC AIP/SUP per airport + Owner claim review |
| 6 | `major-global-hub-iata-transfers-can-kmg-bkk-kul-ath-osl-muc-doh` | `IATA:CAN`, `IATA:KMG`, `IATA:BKK`, `IATA:KUL`, `IATA:ATH`, `IATA:OSL`, `IATA:MUC`, `IATA:DOH` | `cross_physical_airport_major_hub_iata_transfer` | **+80,000** | 16 | Per hub: 1 dated pre-move primary code observation (e.g. accident report or official schedule), 1 primary code-switch implementation notice/AIP SUP, and Owner review |
| 7 | `kg-fru-bsz-manas-recode` | `IATA:FRU`, `IATA:BSZ` | `same_site_iata_recode` | **+7,988** | 1 | 1 dated pre-2025 primary FRU observation (e.g. MAK/interstate accident report at Manas) + Owner approval of [2025-08-09, 2025-08-12) conservative switch bound |
| 8 | `us-faa-nasr-bounded-icao-batch` | `2,458 US ICAO codes (e.g. KATL, KORD, KLAX, KJFK, ...)` | `bulk_bounded_icao_continuity_proposal` | **+63,908** | 0 | Owner policy/batch scope authorization + UUID deduplication for ourAirports=3766 (note: ICAO-only and 26-day window; zero IATA coverage unless paired with US DOT/IATA primary sources) |
| 9 | `uz-icao-prefix-ut-to-uz-and-kr-molit-icao` | `26 UZ ICAO codes (UT* -> UZ*)`, `KR MOLIT ICAO batch (54 days)` | `state_icao_prefix_transition_and_authorized_aip_window` | **+54** | 2 | Outer dated ICAO observations for Uzbekistan UT*/UZ* to make intervals two-sided; Owner authorization comment for KR rule-v1 |
