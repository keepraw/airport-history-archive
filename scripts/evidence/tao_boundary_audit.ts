// Exhaustively replay IATA TAO for every supported local date.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { queryHorizon, resolveAirport } from "../../src/index.ts";
import { dateNumber } from "../../src/time.ts";
import { assertDataset } from "../../src/validate.ts";

function readDataset(path: string) {
  const bytes = readFileSync(new URL(path, import.meta.url));
  const data: unknown = JSON.parse(bytes.toString("utf8"));
  assertDataset(data);
  return { data, sha256: createHash("sha256").update(bytes).digest("hex") };
}

const baseline = readDataset("../../test/curated-0.12.0.json");
const formal = readDataset("../../data/airports.json");
const start = dateNumber(queryHorizon.fromInclusive);
const end = dateNumber(queryHorizon.toExclusive);
const iso = (day: number) => new Date(day * 86_400_000).toISOString().slice(0, 10);
const totals = () => ({ resolved: 0, uncertain: 0, conflict: 0, not_found: 0, invalid_input: 0 });
const before = totals();
const after = totals();
const resolvedByAirportId: Record<string, number> = {};
const difference = { newlyResolved: 0, lost: 0, changedAirport: 0 };
for (let day = start; day < end; day++) {
  const date = iso(day);
  const old = resolveAirport(baseline.data, "TAO", date);
  const current = resolveAirport(formal.data, "TAO", date);
  before[old.status]++;
  after[current.status]++;
  if (current.airport) {
    const id = current.airport.airportId;
    resolvedByAirportId[id] = (resolvedByAirportId[id] ?? 0) + 1;
    if (!old.airport) difference.newlyResolved++;
    else if (old.airport.airportId !== id) difference.changedAirport++;
  } else if (old.airport) difference.lost++;
}

const probes = ["2000-01-01", "2021-08-11", "2021-08-12", "2026-11-18", "2026-11-19"]
  .map(date => {
    const result = resolveAirport(formal.data, "TAO", date);
    return { date, status: result.status, airportId: result.airport?.airportId ?? null };
  });
const report = {
  formatVersion: 2,
  queryHorizon,
  baselineDataVersion: baseline.data.dataVersion,
  baselineSha256: baseline.sha256,
  formalDataVersion: formal.data.dataVersion,
  formalSha256: formal.sha256,
  scheme: "IATA",
  code: "TAO",
  datesCompared: end - start,
  before,
  after,
  resolvedByAirportId,
  difference,
  probes,
};
if (after.resolved !== end - start || difference.lost || difference.changedAirport ||
    probes[4]?.status !== "not_found")
  throw new Error("Formal TAO coverage does not match the owner's decision");
const output = new URL("../../research/evidence/tao-boundary-audit/audit.json", import.meta.url);
const rendered = JSON.stringify(report, null, 2) + "\n";
if (process.argv.includes("--check")) {
  if (readFileSync(output, "utf8") !== rendered)
    throw new Error("Published TAO audit differs from the production resolver");
} else writeFileSync(output, rendered);
console.log(`TAO resolved on ${after.resolved} dates, including ${difference.newlyResolved} newly resolved dates.`);
