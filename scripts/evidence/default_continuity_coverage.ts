/** Exact counts of distinct namespace/code/local-date queries in the formal release. */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { queryHorizon, resolveAirport } from "../../src/index.ts";
import { dateNumber } from "../../src/time.ts";
import type { CodeAssignment, Dataset } from "../../src/types.ts";
import { assertDataset } from "../../src/validate.ts";

type Scheme = CodeAssignment["scheme"];
type Inventory = {
  eligible: Record<string, {
    tier: "scheduled" | "regional";
    name: string;
    airportId: string | null;
    codes: Record<Scheme, string | null>;
    issues: string[];
  }>;
  baselineAssignmentIds: string[];
  exceptionAssignmentIds: Record<string, string[]>;
  duplicateReferenceRows: Record<string, { canonicalReferenceId: string; basis: string }>;
  excludedCurrentReferenceRows: Record<string, { name: string; reason: string; case: string; screenedTier: string | null }>;
  retainedEvidenceScreen: Record<string, Record<string, number>>;
  historicalSites: { airportId: string; name: string }[];
};

const load = (path: string) => JSON.parse(readFileSync(path, "utf8"));
const hash = (path: string) => createHash("sha256").update(readFileSync(path)).digest("hex");
const iso = (day: number) => new Date(day * 86_400_000).toISOString().slice(0, 10);
const schemes = ["IATA", "ICAO"] as const;
const baselinePath = "test/curated-0.12.0.json";
const policyPath = "research/admission/default-continuity-v1/policy.json";
const exceptionsPath = "research/admission/default-continuity-v1/exceptions.json";

function dataset(path: string): Dataset {
  const input: unknown = load(path);
  assertDataset(input);
  return input;
}

function measure(before: Dataset, after: Dataset, defaultIds: Set<string>, exceptionCases: Map<string, string>) {
  const start = dateNumber(queryHorizon.fromInclusive);
  const end = dateNumber(queryHorizon.toExclusive);
  const groups = new Map<string, CodeAssignment[]>();
  for (const a of [...before.assignments, ...after.assignments]) {
    const key = a.scheme + ":" + a.code;
    const group = groups.get(key);
    if (group) group.push(a);
    else groups.set(key, [a]);
  }

  const metrics = () => ({ before: 0, after: 0, new: 0, lost: 0, changedSite: 0, conflicts: 0 });
  const byScheme = { IATA: metrics(), ICAO: metrics() };
  const newByBasis = {
    IATA: { defaultContinuity: 0, historicalExceptions: 0 },
    ICAO: { defaultContinuity: 0, historicalExceptions: 0 },
  };
  const lastDay = new Map<string, string>();
  const byCode = new Map<string, ReturnType<typeof metrics>>();
  const newByException = new Map<string, number>();
  let resolverCalls = 0;
  for (const [key, group] of groups) {
    const { scheme, code } = group[0]!;
    const cuts = new Set([start, end]);
    for (const a of group) {
      for (const boundary of [a.validFrom, a.validTo]) {
        for (const date of [boundary.earliest, boundary.latest]) {
          if (date) {
            const day = dateNumber(date);
            if (start < day && day < end) cuts.add(day);
          }
        }
      }
    }
    const ordered = [...cuts].sort((a, b) => a - b);
    const totals = metrics();
    for (let i = 0; i < ordered.length - 1; i++) {
      const date = iso(ordered[i]!);
      const span = ordered[i + 1]! - ordered[i]!;
      // Assignment overlap with a whole day only changes at an integral boundary.
      const old = resolveAirport(before, code, date, scheme);
      const current = resolveAirport(after, code, date, scheme);
      resolverCalls += 2;
      if (old.status === "resolved") totals.before += span;
      if (current.status === "resolved") totals.after += span;
      if (current.status === "resolved" && old.status !== "resolved") {
        totals.new += span;
        const assignmentId = current.candidates.find(c => c.temporalMatch === "certain")!.assignment.assignmentId;
        const reviewedCase = exceptionCases.get(assignmentId);
        if (reviewedCase) {
          newByBasis[scheme].historicalExceptions += span;
          newByException.set(reviewedCase, (newByException.get(reviewedCase) ?? 0) + span);
        } else if (defaultIds.has(assignmentId)) newByBasis[scheme].defaultContinuity += span;
        else throw new Error(`New coverage has no authorized basis: ${assignmentId}`);
      }
      if (old.status === "resolved" && current.status !== "resolved") totals.lost += span;
      if (old.airport && current.airport && old.airport.airportId !== current.airport.airportId)
        totals.changedSite += span;
      if (current.status === "conflict") totals.conflicts += span;
      if (i === ordered.length - 2 && current.airport)
        lastDay.set(key, current.airport.airportId);
    }
    byCode.set(key, totals);
    for (const metric of Object.keys(totals) as (keyof typeof totals)[]) {
      byScheme[scheme][metric] += totals[metric];
    }
  }
  return { byScheme, byCode, lastDay, newByBasis, newByException, resolverCalls };
}

const [command, currentPath, inventoryPath, reportPath] = process.argv.slice(2);
if (!currentPath || !inventoryPath || !reportPath || (command !== "build" && command !== "validate"))
  throw new Error("Expected build or validate followed by dataset, inventory, and report paths");
const current = dataset(currentPath);
const previous = dataset(baselinePath);
const inventory = load(inventoryPath) as Inventory;
const defaultIds = new Set(inventory.baselineAssignmentIds);
const exceptionCases = new Map(Object.entries(inventory.exceptionAssignmentIds)
  .flatMap(([name, ids]) => ids.map(id => [id, name] as const)));
const { byScheme, byCode, lastDay, newByBasis, newByException, resolverCalls } =
  measure(previous, current, defaultIds, exceptionCases);
const previousIds = new Set(previous.assignments.map(a => a.assignmentId));
const stats = (scheme: Scheme) => {
  const rows = current.assignments.filter(a => a.scheme === scheme);
  return {
    assignments: rows.length,
    newAssignments: rows.filter(a => !previousIds.has(a.assignmentId)).length,
    uniqueCodes: new Set(rows.map(a => a.code)).size,
    defaultContinuityAssignments: rows.filter(a => defaultIds.has(a.assignmentId)).length,
    historicalExceptionAssignments: rows.filter(a => exceptionCases.has(a.assignmentId)).length,
    resolvedQueries: byScheme[scheme],
    newlyResolvedByBasis: newByBasis[scheme],
  };
};
const population = { scheduled: { processed: 0, covered: 0 }, regional: { processed: 0, covered: 0 } };
const coveredByScheme = { IATA: 0, ICAO: 0 };
const uncovered = [];
const issuesByReason: Record<string, number> = {};
const uncoveredByReason: Record<string, number> = {};
for (const [referenceId, row] of Object.entries(inventory.eligible)) {
  population[row.tier].processed++;
  const matched = schemes.filter(s => row.airportId !== null &&
    row.codes[s] !== null && lastDay.get(s + ":" + row.codes[s]) === row.airportId);
  for (const scheme of matched) coveredByScheme[scheme]++;
  if (matched.length) population[row.tier].covered++;
  const issues = matched.length || row.issues.length ? row.issues : ["outside_reviewed_assignment_interval"];
  if (!matched.length) uncovered.push({ referenceId, ...row, issues });
  const reasons = issues.map(issue => issue.replace(/^(IATA|ICAO)(:[A-Z]+)? /, ""));
  for (const reason of reasons) {
    issuesByReason[reason] = (issuesByReason[reason] ?? 0) + 1;
  }
  if (!matched.length)
    for (const reason of new Set(reasons))
      uncoveredByReason[reason] = (uncoveredByReason[reason] ?? 0) + 1;
}
const counts = Object.values(population);
const processed = counts.reduce((sum, row) => sum + row.processed, 0);
const covered = counts.reduce((sum, row) => sum + row.covered, 0);
const taoDates = ["1999-12-31", "2000-01-01", "2021-08-11", "2021-08-12", "2026-11-18", "2026-11-19"];
const tao = taoDates.map(date => {
  const result = resolveAirport(current, "TAO", date);
  return { date, status: result.status, airportId: result.airport?.airportId ?? null };
});
const liuting = "apt_f470ecb5-c6dc-4516-a233-37302da2115b";
const jiaodong = "apt_6729d2b2-4b79-48c8-9c42-0d4eeba121b8";
if (tao.some((result, i) => result.airportId !== [null, liuting, liuting, jiaodong, jiaodong, null][i]))
  throw new Error("The formal TAO intervals fail the owner's boundary probes");
if (tao[0]?.status !== "not_found" || tao[5]?.status !== "not_found")
  throw new Error("The resolver returned coverage outside the supported dates");
if (schemes.some(s => byScheme[s].conflicts || byScheme[s].lost || byScheme[s].changedSite))
  throw new Error("Continuity admission introduced a conflict or changed a previously resolved answer");

const exceptions = load(exceptionsPath) as { cases: { case: string; status: string }[] };
const report = {
  formatVersion: 1,
  dataVersion: current.dataVersion,
  fingerprint: { baselineSha256: hash(baselinePath), formalSha256: hash(currentPath),
    policySha256: hash(policyPath), exceptionRegisterSha256: hash(exceptionsPath) },
  queryHorizon,
  localDates: dateNumber(queryHorizon.toExclusive) - dateNumber(queryHorizon.fromInclusive),
  retainedEvidenceScreen: inventory.retainedEvidenceScreen,
  formalPhysicalAirports: current.airports.length,
  newFormalPhysicalAirports: current.airports.length - previous.airports.length,
  historicalPredecessorsProcessed: inventory.historicalSites,
  formal: { IATA: stats("IATA"), ICAO: stats("ICAO") },
  distinctSchemeCodeKeys: byCode.size,
  weightedResolverCalls: resolverCalls,
  newlyResolvedQueries: byScheme.IATA.new + byScheme.ICAO.new,
  currentPassengerCoverage: {
    measuredOn: iso(dateNumber(queryHorizon.toExclusive) - 1),
    referenceRowsScreened: processed + Object.keys(inventory.duplicateReferenceRows).length +
      Object.values(inventory.excludedCurrentReferenceRows).filter(row => row.screenedTier !== null).length,
    duplicateReferenceRows: inventory.duplicateReferenceRows,
    excludedCurrentReferenceRows: inventory.excludedCurrentReferenceRows,
    processed, covered, percent: Number((100 * covered / processed).toFixed(2)),
    byTier: population, coveredByScheme, missingBothSchemes: uncovered.length,
    issuesByReason, uncoveredByReason, uncovered,
  },
  reviewedExceptions: exceptions.cases.map(c => ({
    case: c.case, status: c.status, assignmentIds: inventory.exceptionAssignmentIds[c.case],
    newlyResolvedQueries: newByException.get(c.case) ?? 0,
  })),
  tao: { probes: tao, measuredQueries: byCode.get("IATA:TAO") },
};
const output = JSON.stringify(report, null, 2) + "\n";
if (command === "build")
  writeFileSync(reportPath, output);
else if (readFileSync(reportPath, "utf8") !== output)
  throw new Error("Continuity admission coverage receipt differs from actual resolver results");

console.log(JSON.stringify({
  airports: report.formalPhysicalAirports, newAirports: report.newFormalPhysicalAirports,
  iata: report.formal.IATA, icao: report.formal.ICAO, resolverCalls, newResolved: report.newlyResolvedQueries,
  current: { processed, covered, percent: report.currentPassengerCoverage.percent },
  historicalPredecessors: inventory.historicalSites.length, tao: report.tao.measuredQueries,
}));
