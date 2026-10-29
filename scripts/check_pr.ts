#!/usr/bin/env -S deno run --allow-read --allow-env
// Checks a pull request's title and body against this repository's rules:
// the title is a Conventional Commits subject, and the body keeps every
// heading of .github/pull_request_template.md and ticks the secrets item.
//
//   check_pr.ts --title "<title>" --body-file <path>
//   PR_TITLE=... PR_BODY=... check_pr.ts
import { fail, Findings, readText } from "./lib/findings.ts";

const TITLE_RE =
  /^(feat|fix|docs|refactor|test|chore|ci|build|perf|style|revert)(\([a-z0-9][a-z0-9-]*\))?!?: [a-z0-9].*$/;
const TITLE_MAX = 72;
const SECURITY_KEYWORD = "No secrets";

const args = Deno.args;
let title = Deno.env.get("PR_TITLE");
let body = Deno.env.get("PR_BODY");
for (let i = 0; i < args.length; i += 2) {
  if (args[i] === "--title") title = args[i + 1];
  else if (args[i] === "--body-file") body = readText(args[i + 1]);
  else fail(`unknown argument ${args[i]}; use --title <text> and --body-file <path>`);
}
if (title === undefined) fail("no title: pass --title or set PR_TITLE");
if (body === undefined) fail("no body: pass --body-file or set PR_BODY");

const findings = new Findings();
if (!TITLE_RE.test(title)) {
  findings.add({
    file: "pull request title",
    rule: "pr-title",
    problem: `"${title}" is not a Conventional Commits subject.`,
    fix:
      "use `<type>(<scope>)?: <lowercase subject>` with a type from feat, fix, docs, refactor, test, chore, ci, build, perf, style, revert.",
  });
} else if (title.length > TITLE_MAX) {
  findings.add({
    file: "pull request title",
    rule: "pr-title",
    problem: `is ${title.length} characters (limit ${TITLE_MAX}).`,
    fix: "shorten the subject; details belong in the body.",
  });
}

const template = readText(".github/pull_request_template.md");
const headings = [...template.matchAll(/^## (.+)$/gm)].map((m) => m[1]);
for (const heading of headings) {
  const literal = heading.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); // headings are text, not patterns
  if (!new RegExp(`^## ${literal}\\s*$`, "m").test(body)) {
    findings.add({
      file: "pull request body",
      rule: "pr-template",
      problem: `section "## ${heading}" is missing.`,
      fix: "keep every heading of .github/pull_request_template.md.",
    });
  }
}
const securityLine = body.split("\n").find((l) => l.includes(SECURITY_KEYWORD));
if (securityLine === undefined || !/^\s*- \[x\]/i.test(securityLine)) {
  findings.add({
    file: "pull request body",
    rule: "pr-security-item",
    problem: `the checklist item containing "${SECURITY_KEYWORD}" is missing or not ticked.`,
    fix: "confirm the change holds no secrets or private data and tick the item.",
  });
}
Deno.exit(findings.report("check_pr"));
