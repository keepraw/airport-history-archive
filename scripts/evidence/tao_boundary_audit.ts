// Compare the inherited formal dataset and current checkout through the public resolver.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { queryHorizon, resolveAirport } from "../../src/index.ts";
import { dateNumber } from "../../src/time.ts";
import type { CodeAssignment, Source } from "../../src/types.ts";
import { assertDataset } from "../../src/validate.ts";

function readDataset(path: string) {
  const contents = readFileSync(new URL(path, import.meta.url));
  const dataset: unknown = JSON.parse(contents.toString("utf8"));
  assertDataset(dataset);
  return { dataset, sha256: createHash("sha256").update(contents).digest("hex") };
}

const baseline = readDataset("../../test/curated-0.12.0.json");
const current = readDataset("../../data/airports.json");
const proposalBytes = readFileSync(new URL(
  "../../research/evidence/tao-boundary-audit/admission-proposal.json",
  import.meta.url,
));
const proposal = JSON.parse(proposalBytes.toString("utf8")) as {
  baselineSha256: string;
  preparedOn: string;
  assignment: CodeAssignment;
  sources: Source[];
};
if (proposal.baselineSha256 !== baseline.sha256)
  throw new Error("TAO proposal does not match the frozen formal baseline");

// Exercise the pending record in memory with the status it would need after
// owner acceptance. The reviewed dataset and authorization receipts are untouched.
const proposed = {
  ...baseline.dataset,
  assignments: [...baseline.dataset.assignments, {
    ...proposal.assignment, verificationStatus: "verified", verifiedOn: proposal.preparedOn,
  }],
  sources: [...baseline.dataset.sources, ...proposal.sources.map((source) => ({
    ...source, verificationStatus: "verified",
  }))],
};
assertDataset(proposed);

const { fromInclusive, toExclusive } = queryHorizon;
const dateIndexes = { start: dateNumber(fromInclusive), end: dateNumber(toExclusive) };
const dates = Array.from({ length: dateIndexes.end - dateIndexes.start }, (_, i) =>
  new Date((dateIndexes.start + i) * 86_400_000).toISOString().slice(0, 10),
);

const codes = new Map(
  [...baseline.dataset.assignments, ...current.dataset.assignments].map(
    ({ code, scheme }) => [scheme + ":" + code, { code, scheme }],
  ),
);
const comparisonByScheme = {
  IATA: { baselineResolved: 0, currentResolved: 0, newlyResolved: 0, lost: 0, changedAirport: 0 },
  ICAO: { baselineResolved: 0, currentResolved: 0, newlyResolved: 0, lost: 0, changedAirport: 0 },
};
const taoStatusCounts = { resolved: 0, uncertain: 0, conflict: 0, not_found: 0, invalid_input: 0 };
const taoResolvedByAirportId: Record<string, number> = {};
const proposalReplay = { resolved: 0, newlyResolved: 0, lost: 0, changedAirport: 0, conflicts: 0 };

for (const { code, scheme } of codes.values()) {
  const comparison = comparisonByScheme[scheme];
  for (const date of dates) {
    const before = resolveAirport(baseline.dataset, code, date, scheme);
    const after = resolveAirport(current.dataset, code, date, scheme);
    if (before.airport) comparison.baselineResolved++;
    if (after.airport) comparison.currentResolved++;
    if (!before.airport && after.airport) comparison.newlyResolved++;
    if (before.airport && !after.airport) comparison.lost++;
    if (before.airport && after.airport && before.airport.airportId !== after.airport.airportId)
      comparison.changedAirport++;

    if (scheme === "IATA" && code === "TAO") {
      taoStatusCounts[after.status]++;
      if (after.airport) {
        const id = after.airport.airportId;
        taoResolvedByAirportId[id] = (taoResolvedByAirportId[id] ?? 0) + 1;
      }
      const simulated = resolveAirport(proposed, code, date, scheme);
      if (simulated.status === "conflict") proposalReplay.conflicts++;
      if (simulated.airport) proposalReplay.resolved++;
      if (!before.airport && simulated.airport) proposalReplay.newlyResolved++;
      if (before.airport && !simulated.airport) proposalReplay.lost++;
      if (before.airport && simulated.airport && before.airport.airportId !== simulated.airport.airportId)
        proposalReplay.changedAirport++;
    }
  }
}

const oldIds = new Set(baseline.dataset.assignments.map((assignment) => assignment.assignmentId));
const oldAirportIds = new Set(baseline.dataset.airports.map((airport) => airport.airportId));
const newAssignments = current.dataset.assignments.filter((assignment) => !oldIds.has(assignment.assignmentId));
const audit = {
  formatVersion: 2,
  caseId: "qingdao-liuting-tao-cutoff",
  auditedOn: "2026-11-18",
  queryHorizon,
  baseline: { dataVersion: baseline.dataset.dataVersion, sha256: baseline.sha256 },
  current: { dataVersion: current.dataset.dataVersion, sha256: current.sha256 },
  formalAdditions: {
    airports: current.dataset.airports.filter(({ airportId }) => !oldAirportIds.has(airportId)).map(({ airportId }) => airportId),
    iataAssignments: newAssignments.filter(({ scheme }) => scheme === "IATA").map(({ assignmentId }) => assignmentId),
    icaoAssignments: newAssignments.filter(({ scheme }) => scheme === "ICAO").map(({ assignmentId }) => assignmentId),
  },
  productionComparison: {
    localDates: dates.length,
    distinctCodesByScheme: codes.size,
    queriesPerDataset: dates.length * codes.size,
    byScheme: comparisonByScheme,
  },
  tao: {
    assignments: current.dataset.assignments.filter(({ scheme, code }) => scheme === "IATA" && code === "TAO"),
    statusCounts: taoStatusCounts,
    resolvedByAirportId: taoResolvedByAirportId,
    pendingProposalReplay: {
      proposalSha256: createHash("sha256").update(proposalBytes).digest("hex"),
      formalAdmission: false,
      ...proposalReplay,
    },
    probes: [
      "1999-12-31", fromInclusive, "2016-08-16", "2016-08-17",
      "2021-08-11", "2021-08-12", "2026-10-24", "2026-10-25",
      "2026-11-18", toExclusive,
    ].map((date) => {
      const { status, airport } = resolveAirport(current.dataset, "TAO", date);
      return { date, status, airportId: airport?.airportId ?? null };
    }),
  },
};

const output = new URL("../../research/evidence/tao-boundary-audit/audit.json", import.meta.url);
const serialized = JSON.stringify(audit, null, 2) + "\n";
if (process.argv.includes("--check")) {
  if (readFileSync(output, "utf8") !== serialized) throw new Error("Stale resolver audit");
} else {
  writeFileSync(output, serialized);
}
console.log(JSON.stringify({ production: audit.productionComparison, tao: taoStatusCounts }));
