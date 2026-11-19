import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, createReadStream } from "node:fs";
import { fileURLToPath } from "node:url";
import { createGunzip } from "node:zlib";
import { createInterface } from "node:readline";
import { Ajv } from "ajv";

const root = new URL("../../", import.meta.url);
const rootDir = fileURLToPath(root);
const schema = JSON.parse(readFileSync(new URL("schema/evidence-observation.schema.json", root), "utf8")) as object;
const validate = new Ajv({ allErrors: true, strict: true }).compile(schema);

const workTarget = new URL("work/evidence/generated/observations.jsonl.gz", root);
const shippedTarget = new URL("research/evidence/generated/observations.jsonl.gz", root);
if (!existsSync(workTarget) && !existsSync(shippedTarget)) {
  let generated = false;
  for (const bin of ["python3", "python"]) {
    try {
      execFileSync(bin, ["scripts/evidence/pipeline.py", "observations"], { cwd: rootDir, stdio: "ignore" });
      generated = true;
      break;
    } catch {
      // Try fallback interpreter if python3 is unavailable on Windows.
    }
  }
  if (!generated) throw new Error("Unable to materialize evidence observations from locked primary inputs.");
}
const target = existsSync(shippedTarget) ? shippedTarget : workTarget;

const lines = createInterface({ input: createReadStream(target).pipe(createGunzip()), crlfDelay: Infinity });
let count = 0;
for await (const line of lines) {
  if (!validate(JSON.parse(line))) throw new Error(JSON.stringify(validate.errors));
  count++;
}
console.log(`Validated strict evidence schema for ${count} observations (${target.pathname.split("/").slice(-3).join("/")}).`);
