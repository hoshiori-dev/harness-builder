#!/usr/bin/env -S deno run --allow-read --allow-run=gh
// Compares .github/labels.json with the labels of the GitHub repository
// `gh` is pointed at, prints the plan, and applies it only with --apply.
// Labels that exist remotely but not in the file are reported, never deleted.
import { fail, readJson } from "./lib/findings.ts";

interface Label {
  name: string;
  color: string;
  description: string;
}

const apply = Deno.args.includes("--apply");
for (const arg of Deno.args) {
  if (arg !== "--apply") fail(`unknown argument ${arg}; only --apply is accepted`);
}

const wanted = readJson(".github/labels.json") as Label[];
if (!Array.isArray(wanted)) fail(".github/labels.json: expected an array of labels");
for (const label of wanted) {
  for (const field of ["name", "color", "description"] as const) {
    if (typeof label?.[field] !== "string") {
      fail(
        `.github/labels.json: label ${
          JSON.stringify(label?.name ?? label)
        } needs a string "${field}"`,
      );
    }
  }
  if (!/^[0-9a-fA-F]{6}$/.test(label.color)) {
    fail(`.github/labels.json: label "${label.name}" color must be 6 hex digits without #`);
  }
  // GitHub rejects longer descriptions with HTTP 422 after the plan was printed.
  if (label.description.length > 100) {
    fail(
      `.github/labels.json: label "${label.name}" description is ${label.description.length} characters; GitHub allows 100`,
    );
  }
}

function gh(args: string[]): string {
  const result = new Deno.Command("gh", { args, stdout: "piped", stderr: "piped" }).outputSync();
  if (!result.success) {
    fail(
      `gh ${args.join(" ")} exited ${result.code}: ${
        new TextDecoder().decode(result.stderr).trim()
      }`,
    );
  }
  return new TextDecoder().decode(result.stdout);
}

const remote = JSON.parse(
  gh(["label", "list", "--limit", "200", "--json", "name,color,description"]),
) as Label[];
const byName = new Map(remote.map((l) => [l.name, l]));
const plan: { action: "create" | "edit"; label: Label }[] = [];
for (const label of wanted) {
  const current = byName.get(label.name);
  if (!current) plan.push({ action: "create", label });
  else if (
    current.color.toLowerCase() !== label.color.toLowerCase() ||
    current.description !== label.description
  ) {
    plan.push({ action: "edit", label });
  }
}
const extra = remote.filter((l) => !wanted.some((w) => w.name === l.name)).map((l) => l.name);

for (const step of plan) console.log(`${step.action}: ${step.label.name}`);
if (extra.length > 0) console.log(`remote-only (left untouched): ${extra.join(", ")}`);
if (plan.length === 0) console.log("labels: in sync");
if (!apply) {
  if (plan.length > 0) console.log("dry run; pass --apply to write");
  Deno.exit(0);
}
for (const { action, label } of plan) {
  gh([
    "label",
    action,
    label.name,
    "--color",
    label.color,
    "--description",
    label.description,
    ...(action === "create" ? ["--force"] : []),
  ]);
}
console.log(`applied ${plan.length} change(s)`);
