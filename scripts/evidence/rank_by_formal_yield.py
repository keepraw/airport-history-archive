#!/usr/bin/env python3
"""Rank reviewed exceptions by newly resolved queries in the formal dataset."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/evidence/formal-yield-queue"
COVERAGE = ROOT / "research/admissions/0.13.0/coverage.json"
EXCEPTIONS = ROOT / "research/admission/default-continuity-v1/exceptions.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def render():
    report, register = load(COVERAGE), load(EXCEPTIONS)
    details = {row["case"]: row for row in register["cases"]}
    sorted_cases = sorted(report["reviewedExceptions"], key=lambda row: (-row["newlyResolvedQueries"], row["case"]))
    cases = [
        {
            "rank": rank,
            **row,
            "outstandingClaims": details[row["case"]].get("holds", []),
        }
        for rank, row in enumerate(sorted_cases, 1)
    ]
    exception_gain = sum(row["newlyResolvedQueries"] for row in cases)
    if exception_gain != sum(row["newlyResolvedByBasis"]["historicalExceptions"] for row in report["formal"].values()):
        raise ValueError("Reviewed exception gains do not add up to the production measurement")
    payload = {
        "formatVersion": 3,
        "reviewedOn": register["reviewedOn"],
        "queryHorizon": report["queryHorizon"],
        "formalDataVersion": report["dataVersion"],
        "formalDatasetSha256": report["fingerprint"]["formalSha256"],
        "actualNewlyResolved": report["newlyResolvedQueries"],
        "actualNewlyResolvedFromExceptions": exception_gain,
        "rankedCases": cases,
    }
    lines = [
        "# Historical code exception results",
        "",
        f"The {report['dataVersion']} production resolver added {report['newlyResolvedQueries']:,} distinct",
        f"code/date results over the frozen 0.12.0 release. Reviewed exceptions contributed {exception_gain:,}.",
        "[Coverage receipt](../../admissions/0.13.0/coverage.json)",
        "",
        "The order reflects actual gains for reviewed cases. Evidence, interval bounds and reasons",
        "for open code associations are recorded by case.",
        "[Exception register](../../admission/default-continuity-v1/exceptions.json)",
        "",
        "| Rank | Case | Disposition | New resolved days | Open associations |",
        "| ---: | --- | --- | ---: | ---: |",
    ]
    labels = {"split": "Split", "bounded": "Bounded", "retained_boundary": "Prior boundary retained",
              "pre_cutoff": "Transfer before 2000", "held": "Held"}
    for case in cases:
        lines.append(f"| {case['rank']} | {case['case']} | {labels[case['status']]} | "
                     f"{case['newlyResolvedQueries']:,} | {len(case['outstandingClaims'])} |")
    lines.append("")
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
                raise ValueError(f"Stale formal yield: {file}")
        else:
            file.write_text(content, encoding="utf-8")
