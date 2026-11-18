#!/usr/bin/env python3
"""Record the reviewed passenger-airport priorities and their remaining gates."""
import argparse
import csv
from datetime import date
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "research/evidence"
OUT = EVIDENCE / "formal-yield-queue"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def render():
    audit = load(EVIDENCE / "tao-boundary-audit/audit.json")
    horizon = audit["queryHorizon"]
    low, high = (date.fromisoformat(horizon[k]) for k in ("fromInclusive", "toExclusive"))

    def days(start, end):
        return max(0, (min(high, date.fromisoformat(end)) - max(low, date.fromisoformat(start))).days)

    faa = load(EVIDENCE / "global-public-data/coverage-report.json")
    faa_projection = faa["productionResolver"]["newResolvedCodeDateQueries"]
    with gzip.open(EVIDENCE / "global-public-data/faa-admission-candidates.jsonl.gz", "rt", encoding="utf-8") as stream:
        faa_site_ids = {json.loads(line)["ourAirportsId"] for line in stream}
    with gzip.open(ROOT / "reference/inputs/ourairports.csv.gz", "rt", encoding="utf-8", newline="") as stream:
        faa_scheduled_sites = sum(
            row["id"] in faa_site_ids and row["scheduled_service"] == "yes"
            for row in csv.DictReader(stream)
        )
    faa_window_days = days("2026-10-02", "2026-10-28")
    tao_projection = audit["tao"]["pendingProposalReplay"]["newlyResolved"]
    comparison = audit["productionComparison"]["byScheme"]
    cases = [
        {
            "case": "TAO — Liuting / Jiaodong",
            "codes": ["IATA:TAO"],
            "readiness": "Owner acceptance",
            "effort": "Low",
            "coverage": f"{tao_projection:,} additional dates in the pending proposal replay.",
            "nextGate": (
                "Review the 1991 China Eastern TAO observation, the Liuting site chronology and the 2021 transfer. "
                "The prepared interval retains an unknown original assignment date. Obtain case-specific acceptance."
            ),
            "references": ["../tao-boundary-audit/README.md"],
        },
        {
            "case": "BLR — HAL / Kempegowda",
            "codes": ["IATA:BLR"],
            "readiness": "Evidence and authorization",
            "effort": "Low to moderate",
            "coverage": (
                f"{days('2008-05-25', '2026-10-25'):,} successor dates if the later IATA bound and continuity are accepted. "
                f"Up to {days('2000-01-01', '2008-05-24'):,} predecessor dates with cutoff evidence."
            ),
            "nextGate": (
                "The MoCA Gazette records the switch at 00:01 on 2008-05-24. Keep that day uncertain. "
                "Review a dated successor IATA observation and acquire a HAL IATA observation supporting cutoff coverage. "
                "The exact boundary authorization packet is pending and excludes continuity."
            ),
            "references": ["../global-code-next/policy/README.md", "../global-iata-forensics/candidate-proposals.json"],
        },
        {
            "case": "IST — Atatürk / Istanbul Airport",
            "codes": ["IATA:IST"],
            "readiness": "Evidence and authorization",
            "effort": "Low to moderate",
            "coverage": f"Up to {days('2000-01-01', '2015-06-26'):,} predecessor dates with cutoff evidence.",
            "nextGate": (
                "The formal carrier evidence bounds Atatürk use from 2015 and the 2019 transfer day remains uncertain. "
                "Find a dated IATA IST observation bound to Atatürk at or before the cutoff and review continuity. "
                "The BTS master row supports physical attribution in the USDOT namespace."
            ),
            "references": ["../../../docs/evidence.md", "../source-lock.json"],
        },
        {
            "case": "PBI / DJT — Palm Beach",
            "codes": ["IATA:PBI", "IATA:DJT", "ICAO:KPBI", "ICAO:KDJT"],
            "readiness": "Authorization for bounded KDJT. Evidence and authorization for wider intervals",
            "effort": "Low for KDJT. Moderate for the predecessors",
            "coverage": (
                f"{days('2026-10-02', '2026-10-28'):,} dates in the bounded KDJT proposal. "
                f"{days('2026-08-19', '2026-11-18'):,} DJT dates if carrier and issuing-body continuity is accepted. "
                f"Up to {days('2000-01-01', '2026-08-18'):,} PBI dates with cutoff evidence."
            ),
            "nextGate": (
                "Use the reconciled Palm Beach UUID. Review the FAA pair for bounded KDJT separately from August IATA execution. "
                "Find a dated PBI IATA observation and establish KPBI continuity from a dated FAA identifier record independently. "
                "The current PBI directory row is metropolitan. The bounded KDJT window is included in the FAA scenario."
            ),
            "references": ["../global-iata-forensics/candidate-proposals.json", "../global-code-next/policy/README.md"],
        },
        {
            "case": "LYG / LZO / YBP — China relocations",
            "codes": ["IATA:LYG", "IATA:LZO", "IATA:YBP"],
            "readiness": "Evidence and authorization",
            "effort": "Moderate",
            "coverage": "Six formal site identities. Quantify assignment coverage after code-specific bounds are established.",
            "nextGate": (
                "Obtain a carrier cutover circular, IATA transfer notice or other primary code-specific record for each move "
                "and observations for the outer bounds. CAAC route pricing and operational notices help locate the cases. "
                "The existing China authorization covers the physical identities."
            ),
            "references": ["../../admissions/0.11.0/README.md", "../markets/assessments.json"],
        },
        {
            "case": "FRU / BSZ — Manas",
            "codes": ["IATA:FRU", "IATA:BSZ"],
            "readiness": "Evidence and authorization",
            "effort": "Moderate",
            "coverage": (
                f"{days('2025-08-12', '2026-11-18'):,} BSZ dates if the bounded continuity claim is accepted. "
                "FRU coverage depends on an earlier IATA observation."
            ),
            "nextGate": (
                "The carrier notice and current IATA rows support a conservative August 2025 switch window. "
                "Check UCFM NOTAM A0134/25 and A0140/25 for a tighter switch window and find a dated FRU IATA observation. "
                "Confirm the shared permanent Manas UUID and claim authority."
            ),
            "references": ["../global-iata-forensics/candidate-proposals.json"],
        },
        {
            "case": "Major passenger hub relocations",
            "codes": ["IATA:CAN", "IATA:KMG", "IATA:BKK", "IATA:ATH", "IATA:DOH", "IATA:KUL", "IATA:OSL", "IATA:MUC"],
            "readiness": "Evidence and authorization",
            "effort": "High",
            "coverage": "Five in-scope relocation histories and three successor-only histories. Quantify by hub after source review.",
            "nextGate": (
                "CAN, KMG, BKK, ATH and DOH need separately observed predecessor and successor codes with a verified cutover. "
                "For KUL, OSL and MUC, seek successor IATA use at the cutoff and a later continuity bound. "
                "Start with scheduled passenger hubs in the retained code-link and reuse indexes."
            ),
            "references": ["../global-code-expansion/"],
        },
        {
            "case": "FAA NASR bounded ICAO batch",
            "codes": ["ICAO:FAA NASR candidates"],
            "readiness": "Owner scope authorization and identity review",
            "effort": "Low for existing evidence. Moderate for passenger selection",
            "coverage": (
                f"{faa_projection:,} dates in the full 2,458-code hypothesis. "
                f"The {faa_scheduled_sites:,} sites flagged for scheduled service in the pinned directory "
                f"represent up to {faa_scheduled_sites * faa_window_days:,} of those dates."
            ),
            "nextGate": (
                "The matched FAA editions support [2026-10-02, 2026-10-28). "
                "Confirm passenger service for the screened sites, reconcile Palm Beach OurAirports 3766 to its canonical UUID and get FAA ICAO batch authorization. "
                "The scope covers the short ICAO window."
            ),
            "references": ["../global-public-data/faa-source-lock.json", "../global-public-data/coverage-report.json"],
        },
    ]
    payload = {
        "formatVersion": 2,
        "reviewedOn": "2026-11-18",
        "queryHorizon": horizon,
        "formalDataVersion": audit["current"]["dataVersion"],
        "actualNewlyResolved": sum(m["newlyResolved"] for m in comparison.values()),
        "rankingBasis": "Passenger relevance, evidence maturity, conditional in-scope yield, authorization and acquisition effort",
        "rankedCases": [{"rank": i, **case} for i, case in enumerate(cases, 1)],
    }
    lines = [
        "# Historical code research priorities",
        "",
        f"Local dates from {horizon['fromInclusive']} through the day before",
        f"{horizon['toExclusive']}. The order reflects passenger relevance, evidence maturity,",
        "potential in-scope coverage, claim authorization and acquisition effort.",
        "",
        f"**Actual improvement over the inherited formal data is {payload['actualNewlyResolved']} resolved code/date queries.**",
        "No case below has an immediate, unblocked gain. Conditional figures refer to",
        "individual code/date scenarios and can overlap. The TAO and FAA figures were",
        "replayed through the resolver on temporary proposals.",
        "",
        "| Rank | Case | Readiness | Acquisition effort | Conditional coverage | Next gate |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for case in payload["rankedCases"]:
        links = " ".join(f"[Evidence {i}]({path})" for i, path in enumerate(case["references"], 1))
        lines.append(
            f"| {case['rank']} | {case['case']} | {case['readiness']} | {case['effort']} | "
            f"{case['coverage']} | {case['nextGate']} {links} |"
        )
    lines.extend([
        "",
        "The earlier Uzbekistan ICAO prefix and Korean MOLIT cases remain in their",
        "existing review lanes. Uzbekistan still needs dated outer observations.",
        "Korean rule activation requires its own authorization.",
        "[Uzbekistan boundary proposal](../global-code-next/policy/README.md)",
        "[Korean readiness](../code-dates/korea-readiness/README.md)",
        "",
    ])
    return {
        "ranked-queue.json": json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        "README.md": "\n".join(lines),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for name, content in render().items():
        file = OUT / name
        if args.check:
            if file.read_text(encoding="utf-8") != content:
                raise ValueError(f"Stale research priority output: {file}")
        else:
            file.write_text(content, encoding="utf-8")
