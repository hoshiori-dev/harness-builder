#!/usr/bin/env -S deno run --allow-read --allow-env --allow-run=gh
// Keeps the OpenSpec state label of a pull request current (lib/pr_labels.ts
// holds the rules; .agents/knowledge/spec-workflow.md explains them).
//
//   sync_pr_labels.ts <number>          print the decision; write nothing
//   sync_pr_labels.ts <number> --apply  write the label difference and the record comment
//   sync_pr_labels.ts --apply           the pr-labels workflow: PR_NUMBER (or
//                                       DISPATCH_NUMBER) and EVENT_ACTION,
//                                       EVENT_LABEL, EVENT_SENDER, EVENT_HEAD
//                                       come from the environment
//
// Everything is read and written through `gh api`; nothing of the pull request
// is checked out or run. Values the pull request controls reach `gh api` only as
// request bodies or percent-encoded path segments. On an error after the labels
// were read, `spec:approved` is replaced by `spec:pending`: an undecidable
// state never keeps an approval.
import {
  Api,
  APPROVED,
  ChangedFile,
  Comment,
  decide,
  Event,
  LabelEvent,
  labelPlan,
  PENDING,
  Pull,
  TreeEntry,
} from "./lib/pr_labels.ts";
import { fail } from "./lib/findings.ts";

const apply = Deno.args.includes("--apply");
const positional = Deno.args.filter((a) => a !== "--apply");
if (positional.length > 1) fail("usage: sync_pr_labels.ts [<number>] [--apply]");
// `||`, not `??`: the workflow sets PR_NUMBER to the empty string on a dispatch.
const numberArg = positional[0] || Deno.env.get("PR_NUMBER") || Deno.env.get("DISPATCH_NUMBER") ||
  "";
if (!/^[0-9]+$/.test(numberArg)) {
  fail("no pull request number: pass it or set PR_NUMBER / DISPATCH_NUMBER");
}
const number = Number(numberArg);
const repo = Deno.env.get("GITHUB_REPOSITORY") ??
  gh(["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]).trim();
if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repo)) fail(`unusable repository name "${repo}"`);

const event: Event | null = positional.length === 0 && Deno.env.get("EVENT_ACTION")
  ? {
    action: Deno.env.get("EVENT_ACTION") ?? "",
    label: Deno.env.get("EVENT_LABEL") ?? "",
    sender: Deno.env.get("EVENT_SENDER") ?? "",
    head: Deno.env.get("EVENT_HEAD") ?? "",
  }
  : null;

function gh(args: string[]): string {
  const result = new Deno.Command("gh", { args, stdout: "piped", stderr: "piped" }).outputSync();
  if (!result.success) {
    throw new Error(
      `gh ${args.join(" ")} exited ${result.code}: ${
        new TextDecoder().decode(result.stderr).trim()
      }`,
    );
  }
  return new TextDecoder().decode(result.stdout);
}
function api<T>(path: string, extra: string[] = []): T {
  return JSON.parse(gh(["api", ...extra, `repos/${repo}/${path}`])) as T;
}
function paged<T>(path: string): T[] {
  return JSON.parse(gh(["api", "--paginate", "--slurp", `repos/${repo}/${path}`])).flat() as T[];
}
const issue = `issues/${number}`;

const github: Api = {
  pull: () => {
    const p = api<{ state: string; head: { sha: string }; labels: { name: string }[] }>(
      `pulls/${number}`,
    );
    return Promise.resolve(
      {
        state: p.state === "open" ? "open" : "closed",
        head: p.head.sha,
        labels: p.labels.map((l) => l.name),
      } as Pull,
    );
  },
  files: () => Promise.resolve(paged<ChangedFile>(`pulls/${number}/files?per_page=100`)),
  tree: (sha) => {
    const t = api<{ tree: TreeEntry[]; truncated: boolean }>(`git/trees/${sha}?recursive=1`);
    return Promise.resolve({ entries: t.tree, truncated: t.truncated });
  },
  labelEvents: () =>
    Promise.resolve(
      paged<{ id: number; event: string; label?: { name: string }; actor?: { login: string } }>(
        `${issue}/timeline?per_page=100`,
      )
        .filter((e) => (e.event === "labeled" || e.event === "unlabeled") && e.label && e.actor)
        .map((e) => ({
          id: e.id,
          event: e.event as LabelEvent["event"],
          label: e.label!.name,
          actor: e.actor!.login,
        })),
    ),
  comments: () =>
    Promise.resolve(
      paged<{ id: number; body: string; user?: { login: string } }>(
        `${issue}/comments?per_page=100`,
      ).map((c): Comment => ({
        id: c.id,
        author: c.user?.login ?? "",
        body: c.body ?? "",
      })),
    ),
  blob: (sha) =>
    Promise.resolve(
      api<{ content: string }>(`git/blobs/${encodeURIComponent(sha)}`).content.replaceAll("\n", ""),
    ).then((b64) => new TextDecoder().decode(Uint8Array.from(atob(b64), (c) => c.charCodeAt(0)))),
  permission: (login) =>
    Promise.resolve(
      api<{ permission: string }>(`collaborators/${encodeURIComponent(login)}/permission`)
        .permission,
    ),
};

// One read of the pull request per run: decide() and the plan see the same labels and head.
let pullOnce: Promise<Pull> | null = null;
const readPull = github.pull;
github.pull = () => (pullOnce ??= readPull());

let current: Pull | null = null;
try {
  const pull = await github.pull();
  current = pull;
  const decision = await decide(github, event);
  const plan = labelPlan(pull.labels, decision);
  const shown = decision.leave ? "untouched" : decision.state ?? "no state label";
  console.log(`#${number}: ${shown} (${decision.reason})`);
  for (const l of plan.add) console.log(`  add    ${l}`);
  for (const l of plan.remove) console.log(`  remove ${l}`);
  if (decision.record) {
    console.log(`  ${decision.record.id ? "update" : "create"} the approval record comment`);
  }
  if (!apply) {
    console.log("dry run; pass --apply to write");
    Deno.exit(0);
  }
  // The record first: a label without a record is repaired by the next run, a
  // record without a label is restored by it, but a label written before a failed
  // record would stand as an approval nothing vouches for.
  if (decision.record) {
    if (decision.record.id === undefined) {
      gh([
        "api",
        "-X",
        "POST",
        `repos/${repo}/${issue}/comments`,
        "-f",
        `body=${decision.record.body}`,
      ]);
    } else {
      gh([
        "api",
        "-X",
        "PATCH",
        `repos/${repo}/issues/comments/${decision.record.id}`,
        "-f",
        `body=${decision.record.body}`,
      ]);
    }
  }
  for (const l of plan.remove) {
    gh(["api", "-X", "DELETE", `repos/${repo}/${issue}/labels/${encodeURIComponent(l)}`]);
  }
  for (const l of plan.add) {
    gh(["api", "-X", "POST", `repos/${repo}/${issue}/labels`, "-f", `labels[]=${l}`]);
  }
  console.log(`applied ${plan.add.length + plan.remove.length} label change(s)`);
} catch (error) {
  console.error(`sync_pr_labels: ${(error as Error).message}`);
  // Fail safe on an open pull request only; a 404 on the delete means the label is already gone.
  if (apply && current?.state === "open" && current.labels.includes(APPROVED)) {
    try {
      try {
        gh([
          "api",
          "-X",
          "DELETE",
          `repos/${repo}/${issue}/labels/${encodeURIComponent(APPROVED)}`,
        ]);
      } catch (e) {
        if (!String((e as Error).message).includes("HTTP 404")) throw e;
      }
      gh(["api", "-X", "POST", `repos/${repo}/${issue}/labels`, "-f", `labels[]=${PENDING}`]);
      console.error(`replaced ${APPROVED} by ${PENDING} because the state could not be decided`);
    } catch (inner) {
      console.error(`could not replace ${APPROVED}: ${(inner as Error).message}`);
    }
  }
  Deno.exit(2);
}
