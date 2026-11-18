/**
 * Regression audit for IATA:TAO (Qingdao Liuting -> Qingdao Jiaodong)
 * using the unmodified production resolver (src/index.ts::resolveAirport).
 *
 * Never mutates data/airports.json when admission requirements are unmet.
 */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { resolveAirport } from "../../src/index.ts";
import { validateDataset } from "../../src/validate.ts";
import { dateNumber } from "../../src/time.ts";
import type { CodeAssignment, Dataset } from "../../src/types.ts";

const LIUTING_ID = "apt_f470ecb5-c6dc-4516-a233-37302da2115b";
const JIAODONG_ID = "apt_6729d2b2-4b79-48c8-9c42-0d4eeba121b8";

const rawFormal = readFileSync("data/airports.json");
const formalSha256 = createHash("sha256").update(rawFormal).digest("hex");
const formal: Dataset = JSON.parse(rawFormal.toString("utf8"));

const toIsoDate = (dayIndex: number): string =>
  new Date(dayIndex * 86_400_000).toISOString().slice(0, 10);

function countRange(dataset: Dataset, fromInclusive: string, toExclusive: string) {
  const start = dateNumber(fromInclusive);
  const end = dateNumber(toExclusive);
  let resolvedLiuting = 0;
  let resolvedJiaodong = 0;
  let uncertain = 0;
  let conflict = 0;
  let notFound = 0;
  for (let d = start; d < end; d++) {
    const res = resolveAirport(dataset, "TAO", toIsoDate(d), "IATA");
    if (res.status === "resolved") {
      if (res.airport?.airportId === LIUTING_ID) resolvedLiuting++;
      else if (res.airport?.airportId === JIAODONG_ID) resolvedJiaodong++;
    } else if (res.status === "uncertain") {
      uncertain++;
    } else if (res.status === "conflict") {
      conflict++;
    } else if (res.status === "not_found") {
      notFound++;
    }
  }
  return {
    fromInclusive,
    toExclusive,
    totalDays: end - start,
    resolvedLiuting,
    resolvedJiaodong,
    totalResolved: resolvedLiuting + resolvedJiaodong,
    uncertain,
    conflict,
    notFound,
  };
}

const currentTargetWindow = countRange(formal, "1982-08-05", "2021-08-12");
const currentFullHorizon = countRange(formal, "1980-01-01", "2026-11-18");

// In-memory counterfactual only: measure exact production resolver effect IF a primary
// code-allocation/timetable source later proves [1982-08-05, 2021-08-12).
const counterfactual: Dataset = structuredClone(formal);
const hypotheticalAssignment: CodeAssignment = {
  assignmentId: "counterfactual-iata-tao-liuting-1982-2021",
  airportId: LIUTING_ID,
  scheme: "IATA",
  code: "TAO",
  evidenceType: "continuity_inference",
  validFrom: {
    earliest: "1982-08-05",
    latest: "1982-08-05",
    precision: "exact",
  },
  validTo: {
    earliest: "2021-08-12",
    latest: "2021-08-12",
    precision: "exact",
  },
  verificationStatus: "verified",
  verifiedOn: "2026-10-26",
  sourceIds: ["tao-earlier", "tao-code", "tao-transfer"],
  note: "In-memory counterfactual measurement only; not admitted into formal data.",
};
counterfactual.assignments.push(hypotheticalAssignment);

const cfValidation = validateDataset(counterfactual);
if (cfValidation.errors.length > 0) {
  throw new Error(`Counterfactual schema/semantic error: ${cfValidation.errors.join("; ")}`);
}

const counterfactualTargetWindow = countRange(counterfactual, "1982-08-05", "2021-08-12");
const counterfactualFullHorizon = countRange(counterfactual, "1980-01-01", "2026-11-18");

const probes = [
  "1982-08-04",
  "1982-08-05",
  "1995-01-01",
  "2016-08-16",
  "2016-08-17",
  "2021-08-11",
  "2021-08-12",
  "2024-06-01",
  "2026-10-25",
].map((date) => {
  const cur = resolveAirport(formal, "TAO", date, "IATA");
  const cf = resolveAirport(counterfactual, "TAO", date, "IATA");
  return {
    date,
    currentStatus: cur.status,
    currentAirportId: cur.airport?.airportId ?? null,
    counterfactualStatus: cf.status,
    counterfactualAirportId: cf.airport?.airportId ?? null,
  };
});

const audit = {
  formatVersion: 1,
  caseId: "qingdao-liuting-tao-regression-audit",
  auditedOn: "2026-11-18",
  formalDataVersion: formal.dataVersion,
  formalDataSha256: formalSha256,
  formalDataModified: false,
  existingFormalState: {
    liutingAirportId: LIUTING_ID,
    jiaodongAirportId: JIAODONG_ID,
    liutingAssignmentId: "iata-tao-liuting",
    liutingCurrentValidFrom: {
      earliest: null,
      latest: "2016-08-17",
      precision: "unknown",
    },
    liutingCurrentValidTo: {
      earliest: "2021-08-12",
      latest: "2021-08-12",
      precision: "exact",
    },
    jiaodongAssignmentId: "iata-tao-jiaodong",
    jiaodongCurrentValidFrom: {
      earliest: "2021-08-12",
      latest: "2021-08-12",
      precision: "exact",
    },
    jiaodongCurrentValidTo: {
      earliest: "2026-10-25",
      latest: null,
      precision: "unknown",
    },
  },
  fourPartEvidenceCheck: {
    physicalAirportIdentity: {
      proven: true,
      status: "already_formal_in_data",
      basis:
        "Permanent ID apt_f470ecb5-c6dc-4516-a233-37302da2115b (Qingdao Liuting International Airport, OurAirports 27224) and successor apt_6729d2b2-4b79-48c8-9c42-0d4eeba121b8 (Qingdao Jiaodong) are already curated in data/airports.json and corroborated by CAAC 2021 statistical bulletin (cn-stat-2021).",
    },
    iataCodeIdentity: {
      proven: true,
      status: "already_formal_in_data",
      basis:
        "iata-tao-liuting is already verified in data/airports.json from ANA Cargo primary procedures (tao-earlier) and IATA retention/transfer reporting (tao-code, tao-transfer).",
    },
    endBoundary_2021_08_12: {
      proven: true,
      status: "already_formal_in_data",
      basis:
        "Exact local-midnight boundary 2021-08-12 is already verified in data/airports.json (tao-code reporting 2019-03-21 IATA approval tied to opening midnight + tao-transfer reporting simultaneous 2021-08-12 00:00 closure/opening + cn-stat-2021).",
    },
    startBoundary_1982_08_05: {
      proven: false,
      status: "pending_missing_code_effective_evidence",
      basis:
        "1982-08-05 is the State Council / CMC approved civil aviation reopening date of CAAC Qingdao Station at Naval Liuting Airport (following earlier 1946-1949 CNAC/CAT and 1958-1961 CAAC civil operations at separate Qingdao Cangkou Airport, when Postal-romanized 'Tsingtao' originated TAO). Available records prove airport civil reopening on 1982-08-05, not an IATA TAO code allocation or cross-site transfer effective date.",
      policyBlockers: [
        "AGENTS.md Rule 9 & README.md: airport opening/reopening dates cannot substitute for code effective dates ('No historic code start was inferred from an airport opening date').",
        "research/admission/source-claims-v1/policy.json explicitly excludes 'opening_or_licence_as_code_effective' and keeps 'CN-EXPLICIT-CODE-ALLOCATION' inactive.",
        "scripts/reference/admissions.py::validate_admission requires a reviewed dated primary code observation and explicit Owner claim acceptance.",
      ],
      specificMissingEvidence:
        "Dated 1982 CAAC system timetable (e.g. August/November 1982 issue showing TAO at Qingdao Liuting), original IATA Coding Administration notice, or historical CAAC AIP/AIC explicitly binding TAO to Liuting on or shortly after 1982-08-05.",
    },
  },
  productionResolverMeasurements: {
    currentFormalInTargetWindow_1982_08_05_to_2021_08_12: currentTargetWindow,
    currentFormalAcrossFullHorizon_1980_to_2026_11_18: currentFullHorizon,
    counterfactualIf_1982_08_05_Proven: counterfactualTargetWindow,
    counterfactualFullHorizonIf_1982_08_05_Proven: counterfactualFullHorizon,
    netNewFormalResolvedQueriesWrittenToday: 0,
    potentialIncrementalResolvedQueriesAwaitingStartEvidence:
      counterfactualTargetWindow.resolvedLiuting - currentTargetWindow.resolvedLiuting,
    probeDates: probes,
  },
};

const outDir = "research/evidence/tao-boundary-audit";
mkdirSync(outDir, { recursive: true });
writeFileSync(`${outDir}/audit.json`, JSON.stringify(audit, null, 2) + "\n");

const readme = `# TAO (Qingdao Liuting) Boundary Regression Audit

## Summary Verdict

\`TAO -> Qingdao Liuting International Airport\` (\`apt_f470ecb5-c6dc-4516-a233-37302da2115b\`) is **already formally admitted** in [airports.json](../../../data/airports.json) under \`iata-tao-liuting\`, resolving **1,821** local dates in \`[2016-08-17, 2021-08-12)\` (alongside \`iata-tao-jiaodong\`, which resolves **1,900** local dates in \`[2021-08-12, 2026-10-25)\`).

Extending \`iata-tao-liuting\` backward to \`[1982-08-05, 2021-08-12)\` was audited without rescanning any global database:

| Requirement | Audit Result | Formal Status |
| --- | --- | --- |
| Physical airport identity (\`Qingdao Liuting International Airport\`) | Proven (\`apt_f470ecb5-c6dc-4516-a233-37302da2115b\`, OurAirports \`27224\`, CAAC \`cn-stat-2021\`) | Already in \`data/airports.json\` |
| IATA code identity (\`TAO\`) | Proven (\`tao-earlier\`, \`tao-code\`, \`tao-transfer\`) | Already in \`data/airports.json\` |
| End boundary \`2021-08-12\` (\`validTo\`) | Proven (\`2021-08-12\` exact local midnight via \`tao-code\` + \`tao-transfer\`) | Already in \`data/airports.json\` |
| Start boundary \`1982-08-05\` (\`validFrom\`) | **Unproven as code boundary** (\`1982-08-05\` is CAAC civil flight reopening at Liuting; pre-1979 Postal *Tsingtao* \`TAO\` predates Liuting's 1982 civil reopening when Qingdao civil flights used Cangkou Airport in 1946–1949 and 1958–1961) | Held \`pending\` per admission policy |

## Production Resolver Measurements (\`resolveAirport()\`)

| Metric | Current \`data/airports.json\` (\`0.12.0\`) | Counterfactual \`[1982-08-05, 2021-08-12)\` | Delta |
| --- | ---: | ---: | ---: |
| Total days in \`[1982-08-05, 2021-08-12)\` | ${currentTargetWindow.totalDays.toLocaleString("en-US")} | ${counterfactualTargetWindow.totalDays.toLocaleString("en-US")} | 0 |
| \`resolved\` -> Qingdao Liuting in \`[1982-08-05, 2021-08-12)\` | **${currentTargetWindow.resolvedLiuting.toLocaleString("en-US")}** | **${counterfactualTargetWindow.resolvedLiuting.toLocaleString("en-US")}** | **+${(counterfactualTargetWindow.resolvedLiuting - currentTargetWindow.resolvedLiuting).toLocaleString("en-US")}** |
| \`uncertain\` in \`[1982-08-05, 2021-08-12)\` (\`[1982-08-05, 2016-08-17)\`) | ${currentTargetWindow.uncertain.toLocaleString("en-US")} | ${counterfactualTargetWindow.uncertain.toLocaleString("en-US")} | -${currentTargetWindow.uncertain.toLocaleString("en-US")} |
| \`resolved\` -> Qingdao Jiaodong in \`[2021-08-12, 2026-10-25)\` | ${currentFullHorizon.resolvedJiaodong.toLocaleString("en-US")} | ${counterfactualFullHorizon.resolvedJiaodong.toLocaleString("en-US")} | 0 |
| Total formal \`TAO\` \`resolved\` \`code/date\` queries | **${currentFullHorizon.totalResolved.toLocaleString("en-US")}** | **${counterfactualFullHorizon.totalResolved.toLocaleString("en-US")}** | **+${(counterfactualFullHorizon.totalResolved - currentFullHorizon.totalResolved).toLocaleString("en-US")}** |
| Net new formal \`resolved\` queries written today | **0** | — | — |

## Exact Missing Evidence to Unlock \`+12,431\` Formal \`TAO\` Queries

Per \`AGENTS.md\` Rules 7 & 9 and \`research/admission/source-claims-v1/policy.json\` (\`opening_or_licence_as_code_effective\` exclusion), \`1982-08-05\` cannot be written into \`data/airports.json\` from airport-reopening chronicles alone. To formally admit the pre-2016 interval, retrieve **one dated primary code-bearing record** (such as a late-1982 CAAC timetable, IATA Coding Administration bulletin, or historical CAAC AIP/AIC binding \`TAO\` to Qingdao Liuting) and submit for Owner per-record acceptance.
`;
writeFileSync(`${outDir}/README.md`, readme);
console.log(JSON.stringify(audit.productionResolverMeasurements, null, 2));
