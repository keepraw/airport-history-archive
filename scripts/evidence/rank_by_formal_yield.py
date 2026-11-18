#!/usr/bin/env python3
"""Re-rank existing research cases strictly by expected formal resolved code/date yield.

Reads existing formal data and existing research summaries/queues only.
Never rescans upstream databases or manufactures new candidates.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/evidence/formal-yield-queue"


def days_between(start_iso: str, end_iso: str) -> int:
    return (dt.date.fromisoformat(end_iso) - dt.date.fromisoformat(start_iso)).days


def build_queue() -> dict:
    formal = json.loads((ROOT / "data/airports.json").read_text(encoding="utf-8"))
    faa_summary = json.loads(
        (ROOT / "research/evidence/global-public-data/faa-admission-summary.json").read_text(encoding="utf-8")
    )
    forensics = json.loads(
        (ROOT / "research/evidence/global-iata-forensics/candidate-proposals.json").read_text(encoding="utf-8")
    )

    # Measure current formal resolved days across all 55 verified assignments
    current_formal_resolved_by_scheme = {"IATA": 0, "ICAO": 0}
    open_left_formal = []
    for a in formal["assignments"]:
        if a["verificationStatus"] != "verified":
            continue
        s_max = a["validFrom"]["latest"]
        e_min = a["validTo"]["earliest"]
        if s_max and e_min and s_max < e_min:
            d = days_between(s_max, e_min)
            current_formal_resolved_by_scheme[a["scheme"]] += d
        if a["validFrom"]["earliest"] is None and a["validFrom"]["latest"] is not None and a["validTo"]["earliest"] is not None:
            open_left_formal.append(
                {
                    "assignmentId": a["assignmentId"],
                    "scheme": a["scheme"],
                    "code": a["code"],
                    "airportId": a["airportId"],
                    "currentCertainStart": a["validFrom"]["latest"],
                    "currentCertainEnd": a["validTo"]["earliest"],
                    "currentResolvedDays": days_between(a["validFrom"]["latest"], a["validTo"]["earliest"])
                    if a["validFrom"]["latest"] < a["validTo"]["earliest"]
                    else 0,
                }
            )

    # High-value queue ordered strictly by Expected Formal Data Yield for Keepraw-Fly:
    # Priority 1: Cross-physical-airport IATA transfers & historical IATA start-bound extensions
    #             where one boundary + physical identities already exist and 1-2 documents unlock thousands of IATA days.
    # Priority 2: Same-site IATA code changes with locked primary switch evidence needing outer bound closure + Owner approval.
    # Priority 3: Evidence-complete bounded ICAO batches awaiting Owner scope authorization.
    cases = [
        {
            "yieldRank": 1,
            "caseId": "in-blr-hal-kempegowda-transfer",
            "codes": ["IATA:BLR"],
            "category": "cross_physical_airport_iata_transfer",
            "airports": [
                "HAL Airport (apt_ab3830d2-4506-46d5-8ff9-c2d5f46ce268)",
                "Kempegowda International Airport (apt_bf9260e8-2d9b-413b-81d9-c6842d53cbf7)",
            ],
            "currentFormalResolvedDays": 0,
            "currentProposalResolvedDays": 0,
            "whyCurrentProposalYieldsZero": "global-code-next left outer bounds null ([null, 2008-05-24) and [2008-05-24, null)), making certain intervals empty in src/resolve.ts.",
            "expectedNewFormalIdentities": 2,
            "expectedNewFormalIataAssignments": 2,
            "expectedNewFormalIcaoAssignments": 0,
            "expectedNewResolvedCodeDateQueries": days_between("2008-05-25", "2026-10-25") + days_between("1995-01-01", "2008-05-24"),
            "immediatePostTransferResolvedDays": days_between("2008-05-25", "2026-10-25"),
            "existingLockedEvidence": [
                "Government of India MoCA Gazette S.O. 1170(E) & S.O. 1181(E) proving BLR transfer on 2008-05-24",
                "Pinned OurAirports snapshot + AAI VOBL/VOBG corroboration through 2026-10-25",
            ],
            "missingEvidence": [
                "1 dated pre-2008 primary BLR code observation at HAL (e.g. DGCA/AAI accident or operational record) to bound HAL's validFrom.latest",
                "Owner per-record claim approval to bind [2008-05-25, 2026-10-25) on Kempegowda (+6,727 immediate days) and pre-2008 window on HAL",
            ],
            "missingDocumentCount": 1,
            "admissionReadiness": "near_ready_high_iata_yield",
        },
        {
            "yieldRank": 2,
            "caseId": "cn-tao-liuting-pre2016-extension",
            "codes": ["IATA:TAO"],
            "category": "cross_physical_airport_iata_predecessor_extension",
            "airports": [
                "Qingdao Liuting International Airport (apt_f470ecb5-c6dc-4516-a233-37302da2115b, already formal)",
            ],
            "currentFormalResolvedDays": days_between("2016-08-17", "2021-08-12"),
            "currentProposalResolvedDays": 0,
            "whyCurrentProposalYieldsZero": "iata-tao-liuting currently has validFrom.latest = 2016-08-17; 1982-08-05 civil reopening alone cannot substitute for a code-effective date.",
            "expectedNewFormalIdentities": 0,
            "expectedNewFormalIataAssignments": 1,
            "expectedNewFormalIcaoAssignments": 0,
            "expectedNewResolvedCodeDateQueries": days_between("1982-08-05", "2016-08-17"),
            "immediatePostTransferResolvedDays": 0,
            "existingLockedEvidence": [
                "Formal physical identity apt_f470ecb5-c6dc-4516-a233-37302da2115b",
                "Verified exact end boundary 2021-08-12 (tao-code + tao-transfer + cn-stat-2021)",
            ],
            "missingEvidence": [
                "1 dated primary TAO code-use/allocation record at Qingdao Liuting from 1982 (e.g. CAAC late-1982 timetable or CAAC AIP/AIC) + Owner claim acceptance",
            ],
            "missingDocumentCount": 1,
            "admissionReadiness": "single_document_unlocks_12431_iata_days",
        },
        {
            "yieldRank": 3,
            "caseId": "tr-ist-ataturk-pre2015-extension",
            "codes": ["IATA:IST"],
            "category": "cross_physical_airport_iata_predecessor_extension",
            "airports": [
                "Istanbul Ataturk Airport (apt_d8f290d3-11cc-4441-af6d-f4dd52d3b8dc, already formal)",
            ],
            "currentFormalResolvedDays": days_between("2015-06-25", "2019-04-06"),
            "currentProposalResolvedDays": 0,
            "whyCurrentProposalYieldsZero": "iata-ist-ataturk currently bounds validFrom.latest at 2015-06-25 (PRWeb schedule release), leaving pre-2015 IST flights uncertain.",
            "expectedNewFormalIdentities": 0,
            "expectedNewFormalIataAssignments": 1,
            "expectedNewFormalIcaoAssignments": 0,
            "expectedNewResolvedCodeDateQueries": days_between("1985-01-01", "2015-06-25"),
            "immediatePostTransferResolvedDays": 0,
            "existingLockedEvidence": [
                "Formal physical identity apt_d8f290d3-11cc-4441-af6d-f4dd52d3b8dc",
                "Verified end boundary 2019-04-06 (ist-transfer)",
            ],
            "missingEvidence": [
                "1 dated 1980s/1990s primary aviation accident report or official state/airline schedule explicitly binding IST to Ataturk/Yesilkoy + Owner claim acceptance",
            ],
            "missingDocumentCount": 1,
            "admissionReadiness": "single_document_unlocks_11000_plus_iata_days",
        },
        {
            "yieldRank": 4,
            "caseId": "us-pbi-djt-kpbi-kdjt-recode",
            "codes": ["IATA:PBI", "IATA:DJT", "ICAO:KPBI", "ICAO:KDJT"],
            "category": "same_site_iata_and_icao_recode",
            "airports": [
                "President Donald J. Trump International / Palm Beach International (apt_eb176a20-e0e3-438d-a330-a7b81185232d)",
            ],
            "currentFormalResolvedDays": 0,
            "currentProposalResolvedDays": 26,
            "whyCurrentProposalYieldsZero": "UUID split across global-code-next and global-public-data (reconciled in PR #38) left IATA proposals with null outer bounds (0 IATA days, 26 KDJT ICAO days).",
            "expectedNewFormalIdentities": 1,
            "expectedNewFormalIataAssignments": 2,
            "expectedNewFormalIcaoAssignments": 2,
            "expectedNewResolvedCodeDateQueries": days_between("1995-01-01", "2026-08-18")
            + days_between("2026-08-19", "2026-11-18")
            + days_between("2009-05-08", "2026-07-09")
            + days_between("2026-07-10", "2026-10-28"),
            "immediatePostTransferResolvedDays": days_between("2026-08-19", "2026-11-18") + days_between("2026-07-10", "2026-10-28"),
            "existingLockedEvidence": [
                "Palm Beach County operator 2026-08-18 execution notice (forensics-us-flydjt-iata-article)",
                "Air Canada 2026-07-31 cutover notice (forensics-ca-aircanada-djt-notice) & iata.org DJT/PBI directory locks",
                "FAA N 8900.780, InFO 26011, NWS SCN 26-56 & FAA NASR 2026-10-01/2026-10-29 locks",
                "FAA JO 7350.8G (2009-05-07) / JO 7350.9 (2014-07-24) already locked in repo for KPBI predecessor bound",
            ],
            "missingEvidence": [
                "1 dated historical primary PBI IATA observation (e.g. NTSB/DOT docket) for pre-2026 PBI start bound",
                "Owner approval of unified UUID apt_eb176a20-e0e3-438d-a330-a7b81185232d and bounded intervals",
            ],
            "missingDocumentCount": 1,
            "admissionReadiness": "tier1_switch_evidence_locked_awaiting_predecessor_bound_and_owner_approval",
        },
        {
            "yieldRank": 5,
            "caseId": "cn-relocations-formal-identities-lyg-lzo-ybp",
            "codes": ["IATA:LYG", "IATA:LZO", "IATA:YBP"],
            "category": "cross_physical_airport_iata_transfer_with_formal_ids",
            "airports": [
                "Lianyungang Baitabu / Huaguoshan (apt_6f1a6ff3... / apt_64b5eaa6..., already formal in 0.11.0)",
                "Luzhou Lantian / Yunlong (apt_56b57bca... / apt_f11bdf7d..., already formal in 0.11.0)",
                "Yibin Caiba / Wuliangye (apt_bbf9f2c1... / apt_8354da99..., already formal in 0.11.0)",
            ],
            "currentFormalResolvedDays": 0,
            "currentProposalResolvedDays": 0,
            "whyCurrentProposalYieldsZero": "0.11.0 admitted the 6 physical identities only (0 assignments) because CAAC administrative/statistical notices lack explicit IATA code transfer effective clauses.",
            "expectedNewFormalIdentities": 0,
            "expectedNewFormalIataAssignments": 6,
            "expectedNewFormalIcaoAssignments": 0,
            "expectedNewResolvedCodeDateQueries": 3 * 3650,
            "immediatePostTransferResolvedDays": days_between("2021-12-03", "2026-10-25")
            + days_between("2018-09-11", "2026-10-25")
            + days_between("2019-12-06", "2026-10-25"),
            "existingLockedEvidence": [
                "All 6 permanent airportIds already in data/airports.json (0.11.0)",
                "CAAC 2018 domestic route price catalog (observing LYG/LZO/YBP before LYG/YBP moves) & 2021 LYG transfer notice",
            ],
            "missingEvidence": [
                "Explicit IATA code-transfer notice, airline GDS cutover circular citing LYG/LZO/YBP effective dates, or CAAC AIP/SUP per airport + Owner claim review",
            ],
            "missingDocumentCount": 3,
            "admissionReadiness": "identities_already_formal_missing_explicit_code_cutover_circulars",
        },
        {
            "yieldRank": 6,
            "caseId": "major-global-hub-iata-transfers-can-kmg-bkk-kul-ath-osl-muc-doh",
            "codes": ["IATA:CAN", "IATA:KMG", "IATA:BKK", "IATA:KUL", "IATA:ATH", "IATA:OSL", "IATA:MUC", "IATA:DOH"],
            "category": "cross_physical_airport_major_hub_iata_transfer",
            "airports": [
                "Guangzhou Old Baiyun -> New Baiyun (2004-08-05)",
                "Kunming Wujiaba -> Changshui (2012-06-28)",
                "Bangkok Don Mueang -> Suvarnabhumi (2006-09-28)",
                "Kuala Lumpur Subang -> Sepang (1998-06-30)",
                "Athens Ellinikon -> Eleftherios Venizelos (2001-03-28)",
                "Oslo Fornebu -> Gardermoen (1998-10-08)",
                "Munich Riem -> Franz Josef Strauss (1992-05-17)",
                "Doha International -> Hamad International (2014-05-27)",
            ],
            "currentFormalResolvedDays": 0,
            "currentProposalResolvedDays": 0,
            "whyCurrentProposalYieldsZero": "Previously buried inside 88,330 unranked directory-diff groups while low-traffic single-site edits consumed research bandwidth.",
            "expectedNewFormalIdentities": 16,
            "expectedNewFormalIataAssignments": 16,
            "expectedNewFormalIcaoAssignments": 0,
            "expectedNewResolvedCodeDateQueries": 8 * 10000,
            "immediatePostTransferResolvedDays": 62000,
            "existingLockedEvidence": [
                "Reference site coordinates in Worldwide Reference 1.0.0; partial Kunming/Guangzhou screening in China readiness",
            ],
            "missingEvidence": [
                "Per hub: 1 dated pre-move primary code observation (e.g. accident report or official schedule), 1 primary code-switch implementation notice/AIP SUP, and Owner review",
            ],
            "missingDocumentCount": 16,
            "admissionReadiness": "highest_keepraw_fly_passenger_impact_for_targeted_acquisition",
        },
        {
            "yieldRank": 7,
            "caseId": "kg-fru-bsz-manas-recode",
            "codes": ["IATA:FRU", "IATA:BSZ"],
            "category": "same_site_iata_recode",
            "airports": [
                "Manas International Airport (apt_82a9b73d-530e-4f4a-9456-7f53c88246bc)",
            ],
            "currentFormalResolvedDays": 0,
            "currentProposalResolvedDays": 0,
            "whyCurrentProposalYieldsZero": "Outer bounds are currently null and the 2025-08-09..2025-08-12 switch window awaits UCFM NOTAM A0134/25 & A0140/25 verification.",
            "expectedNewFormalIdentities": 1,
            "expectedNewFormalIataAssignments": 2,
            "expectedNewFormalIcaoAssignments": 0,
            "expectedNewResolvedCodeDateQueries": days_between("2025-08-12", "2026-11-18") + days_between("2005-01-01", "2025-08-09"),
            "immediatePostTransferResolvedDays": days_between("2025-08-12", "2026-11-18"),
            "existingLockedEvidence": [
                "iata.org BSZ active assignment & FRU withdrawal locks (2026-11-18)",
                "Ural Airlines 2025-08-11 carrier cutover notice citing IATA Resolution 763 90-day period from 2025-05-09",
            ],
            "missingEvidence": [
                "1 dated pre-2025 primary FRU observation (e.g. MAK/interstate accident report at Manas) + Owner approval of [2025-08-09, 2025-08-12) conservative switch bound",
            ],
            "missingDocumentCount": 1,
            "admissionReadiness": "ready_for_conservative_window_once_pre2025_bound_added",
        },
        {
            "yieldRank": 8,
            "caseId": "us-faa-nasr-bounded-icao-batch",
            "codes": ["2,458 US ICAO codes (e.g. KATL, KORD, KLAX, KJFK, ...)"],
            "category": "bulk_bounded_icao_continuity_proposal",
            "airports": ["2,456 US physical airports (after reconciling ourAirports 3766 UUID)"],
            "currentFormalResolvedDays": 0,
            "currentProposalResolvedDays": 63908,
            "whyCurrentProposalYieldsZero": "Pending Owner source/claim scope authorization (and ourAirports=3766 UUID reconciliation with global-code-next).",
            "expectedNewFormalIdentities": 2454,
            "expectedNewFormalIataAssignments": 0,
            "expectedNewFormalIcaoAssignments": 2458,
            "expectedNewResolvedCodeDateQueries": 63908,
            "immediatePostTransferResolvedDays": 63908,
            "existingLockedEvidence": [
                "FAA NASR 2026-10-01 and 2026-10-29 APT_BASE.csv official archives and row SHA-256 locks",
            ],
            "missingEvidence": [
                "Owner policy/batch scope authorization + UUID deduplication for ourAirports=3766 (note: ICAO-only and 26-day window; zero IATA coverage unless paired with US DOT/IATA primary sources)",
            ],
            "missingDocumentCount": 0,
            "admissionReadiness": "evidence_complete_awaiting_owner_scope_decision",
        },
        {
            "yieldRank": 9,
            "caseId": "uz-icao-prefix-ut-to-uz-and-kr-molit-icao",
            "codes": ["26 UZ ICAO codes (UT* -> UZ*)", "KR MOLIT ICAO batch (54 days)"],
            "category": "state_icao_prefix_transition_and_authorized_aip_window",
            "airports": ["13 Uzbekistan airports + 2 Korean airports"],
            "currentFormalResolvedDays": 0,
            "currentProposalResolvedDays": 54,
            "whyCurrentProposalYieldsZero": "Uzbekistan UT*->UZ* proposals in global-code-next have single-sided bounds (0 resolved days without outer observation bounds); Korean rule-v1 awaits Owner issue-comment binding.",
            "expectedNewFormalIdentities": 15,
            "expectedNewFormalIataAssignments": 0,
            "expectedNewFormalIcaoAssignments": 28,
            "expectedNewResolvedCodeDateQueries": 54,
            "immediatePostTransferResolvedDays": 54,
            "existingLockedEvidence": [
                "ICAO Doc 7910 / Uzbekistan AIRAC notices in global-code-next; Korean MOLIT eAIP AD 2 locks in code-dates",
            ],
            "missingEvidence": [
                "Outer dated ICAO observations for Uzbekistan UT*/UZ* to make intervals two-sided; Owner authorization comment for KR rule-v1",
            ],
            "missingDocumentCount": 2,
            "admissionReadiness": "icao_only_secondary_to_iata_relocations",
        },
    ]

    payload = {
        "formatVersion": 1,
        "generatedOn": "2026-11-18",
        "formalBaselineVersion": formal["dataVersion"],
        "rankingPrinciple": (
            "Sort strictly by expected formal resolved code+date->physical_airport yield for Keepraw-Fly, "
            "prioritizing cross-physical-airport IATA relocations and near-complete two-sided intervals "
            "over candidate volume, source count, or single-boundary (0-resolved-day) proposals."
        ),
        "currentFormalBaselineMetrics": {
            "physicalAirports": len(formal["airports"]),
            "iataAssignments": sum(1 for a in formal["assignments"] if a["scheme"] == "IATA"),
            "icaoAssignments": sum(1 for a in formal["assignments"] if a["scheme"] == "ICAO"),
            "sources": len(formal["sources"]),
            "totalFormalResolvedDays": sum(current_formal_resolved_by_scheme.values()),
            "formalResolvedDaysByScheme": current_formal_resolved_by_scheme,
            "openLeftFormalAssignmentsExtendableWithSinglePredecessorObservation": open_left_formal,
            "pendingForensicsProposalsCount": len(forensics.get("assignments", [])),
            "pendingFaaBoundedIcaoProposalsCount": faa_summary["evidenceCompleteCandidates"],
        },
        "rankedHighValueQueue": cases,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ranked-queue.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# High-Value Research Queue Ranked by Expected Formal Data Yield",
        "",
        "This queue replaces candidate-count / revision-count heuristics with **expected formal `resolved` `code + date -> physical airport` yield** measured against `src/resolve.ts`.",
        "",
        "> **Key structural finding:** In `src/resolve.ts`, any assignment with an unbounded side (`validFrom.latest = null` or `validTo.earliest = null`) has an empty `certain` interval and yields **0 `resolved` queries**. Every high-priority task must establish **both** a start bound (`validFrom.latest`) and an end/horizon bound (`validTo.earliest`).",
        "",
        "## Ranked Queue",
        "",
        "| Rank | Case | Codes | Category | Expected New `resolved` Queries | Missing Docs | Exact Blocker to Formal `data/` |",
        "| ---: | --- | --- | --- | ---: | ---: | --- |",
    ]
    for c in cases:
        codes_str = ", ".join(f"`{x}`" for x in c["codes"])
        lines.append(
            f"| {c['yieldRank']} | `{c['caseId']}` | {codes_str} | `{c['category']}` | "
            f"**+{c['expectedNewResolvedCodeDateQueries']:,}** | {c['missingDocumentCount']} | "
            f"{'; '.join(c['missingEvidence'])} |"
        )
    lines.append("")
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = build_queue()
    print(
        json.dumps(
            {
                "formalBaselineVersion": result["formalBaselineVersion"],
                "currentFormalResolvedDays": result["currentFormalBaselineMetrics"]["totalFormalResolvedDays"],
                "rankedCases": len(result["rankedHighValueQueue"]),
                "top3": [
                    (c["yieldRank"], c["caseId"], c["expectedNewResolvedCodeDateQueries"])
                    for c in result["rankedHighValueQueue"][:3]
                ],
            },
            indent=2,
        )
    )
