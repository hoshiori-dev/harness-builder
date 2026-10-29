// Decides the OpenSpec state label of one pull request from its present state
// (.agents/knowledge/spec-workflow.md, gate 1). Pure logic over an `Api`
// interface; sync_pr_labels.ts supplies the `gh api` implementation and the
// tests a fake.
//
// Exactly one of these labels, or none, belongs on a pull request:
//   spec: skipped   no file under openspec/changes/ is touched
//   spec: pending   the head holds an unarchived change without a valid approval
//   spec: approved  a write-permission account added it while an unarchived
//                   change was at the head, and the approval package (every
//                   blob under the unarchived changes) still hashes the same
//   spec: archived  no unarchived change remains and this PR adds an archived one
//
// The approval is recorded in one comment (marker, status, commit, account,
// package hash). A later run keeps `spec: approved` only while the record is
// not withdrawn and the hash at the head equals the recorded one; otherwise the
// label falls back to `spec: pending` and the record is marked withdrawn. Every
// path the code cannot decide ends without `spec: approved`.

import { parse as parseYaml } from "@std/yaml";

export const SKIPPED = "spec: skipped";
export const PENDING = "spec: pending";
export const APPROVED = "spec: approved";
export const ARCHIVED = "spec: archived";
export const STATE_LABELS = [SKIPPED, PENDING, APPROVED, ARCHIVED] as const;
export type StateLabel = typeof STATE_LABELS[number];

export const CHANGES_DIR = "openspec/changes/";
export const RECORD_MARKER = "<!-- spec-approval-record -->";
/** The only account whose comments count as approval records: the workflow token's identity. */
export const RECORD_AUTHOR = "github-actions[bot]";

export interface Pull {
  state: "open" | "closed";
  head: string;
  labels: string[];
}
export interface TreeEntry {
  path: string;
  type: string;
  sha: string;
}
export interface ChangedFile {
  filename: string;
  status: string;
}
export interface LabelEvent {
  id: number;
  event: "labeled" | "unlabeled";
  label: string;
  actor: string;
}
export interface Comment {
  id: number;
  body: string;
  author: string;
}

export interface Api {
  pull(): Promise<Pull>;
  files(): Promise<ChangedFile[]>;
  tree(sha: string): Promise<{ entries: TreeEntry[]; truncated: boolean }>;
  labelEvents(): Promise<LabelEvent[]>;
  comments(): Promise<Comment[]>;
  permission(login: string): Promise<string>;
  /** Text of a blob by sha; used for each change's `.openspec.yaml`. */
  blob(sha: string): Promise<string>;
}

/** The event that started the run, when it was a label being added or removed. */
export interface Event {
  action: string;
  label: string;
  sender: string;
  head: string;
}

export interface Record {
  id: number;
  status: "approved" | "withdrawn";
  commit: string;
  by: string;
  hash: string;
}

export interface Decision {
  state: StateLabel | null;
  reason: string;
  /** True when the labels must not be touched at all (closed pull request). */
  leave?: boolean;
  /** Comment to create (no id) or update (with id); absent when nothing changes. */
  record?: { id?: number; body: string };
}

const COMMIT_RE = /^[0-9a-f]{40}$/;
const LOGIN_RE = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$/;
const HASH_RE = /^[0-9a-f]{64}$/;

export function isBot(login: string): boolean {
  return login.endsWith("[bot]");
}

/** Distinct unarchived change directories at a tree: `openspec/changes/<name>/…`, name != archive. */
export function unarchivedChanges(entries: TreeEntry[]): string[] {
  const names = new Set<string>();
  for (const e of entries) {
    if (!e.path.startsWith(CHANGES_DIR)) continue;
    const rest = e.path.slice(CHANGES_DIR.length);
    const slash = rest.indexOf("/");
    if (slash === -1) continue; // a plain file directly under changes/
    const name = rest.slice(0, slash);
    if (name !== "archive") names.add(name);
  }
  return [...names].sort();
}

/** sha256 over "path blob-sha" lines of every blob under the unarchived changes, sorted. */
export async function packageHash(entries: TreeEntry[], changes: string[]): Promise<string> {
  const lines = entries
    .filter((e) =>
      e.type === "blob" && changes.some((c) => e.path.startsWith(`${CHANGES_DIR}${c}/`))
    )
    .map((e) => `${e.path} ${e.sha}`)
    .sort();
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(lines.join("\n")));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function recordBody(
  status: Record["status"],
  commit: string,
  by: string,
  hash: string,
  note = "",
): string {
  const tail = status === "approved"
    ? `A maintainer approved the OpenSpec change(s) of this pull request at ${commit}. The pr-labels workflow keeps \`${APPROVED}\` while the files under \`${CHANGES_DIR}\` at the head hash to the same package; a change to them puts \`${PENDING}\` back and marks this record withdrawn.`
    : `This approval was withdrawn: ${note}. A maintainer re-adds \`${APPROVED}\` to approve the current package.`;
  return [
    RECORD_MARKER,
    `Status: ${status}`,
    `Approved commit: ${commit}`,
    `Approved by: ${by}`,
    `Package hash: ${hash}`,
    "",
    tail,
  ].join("\n");
}

export function parseRecord(comment: Comment): Record | null {
  if (comment.author !== RECORD_AUTHOR || !comment.body.startsWith(RECORD_MARKER)) return null;
  const get = (key: string) => comment.body.match(new RegExp(`^${key}: (\\S+)$`, "m"))?.[1];
  const status = get("Status"),
    commit = get("Approved commit"),
    by = get("Approved by"),
    hash = get("Package hash");
  if ((status !== "approved" && status !== "withdrawn") || !commit || !by || !hash) return null;
  if (!COMMIT_RE.test(commit) || !LOGIN_RE.test(by) || !HASH_RE.test(hash)) return null;
  return { id: comment.id, status, commit, by, hash };
}

/** The latest adding of `spec: approved` by a person, unless a person removed it later. */
export function standingApproval(events: LabelEvent[]): LabelEvent | undefined {
  const human = events.filter((e) => e.label === APPROVED && !isBot(e.actor));
  const latestAdd = human.filter((e) => e.event === "labeled").sort((a, b) => b.id - a.id)[0];
  if (!latestAdd) return undefined;
  const removedLater = human.some((e) => e.event === "unlabeled" && e.id > latestAdd.id);
  return removedLater ? undefined : latestAdd;
}

export async function decide(api: Api, event: Event | null): Promise<Decision> {
  const pull = await api.pull();
  if (pull.state !== "open") {
    return {
      state: null,
      leave: true,
      reason: "the pull request is closed; labels are left alone",
    };
  }

  const files = await api.files();
  const touches = files.some((f) => f.filename.startsWith(CHANGES_DIR));
  if (!touches) return { state: SKIPPED, reason: `no file under ${CHANGES_DIR} is touched` };

  const tree = await api.tree(pull.head);
  if (tree.truncated) {
    throw new Error("the head tree is truncated; the approval package cannot be read");
  }
  const changes = unarchivedChanges(tree.entries);
  if (changes.length === 0) {
    // Any status: the archive files are `added` against a base without the
    // change and `renamed` against a base that already holds it (a stack).
    const archived = files.some((f) => f.filename.startsWith(`${CHANGES_DIR}archive/`));
    return archived
      ? { state: ARCHIVED, reason: "no unarchived change; this pull request archives one" }
      : { state: null, reason: "no unarchived change and no archived one touched" };
  }

  // A change whose .openspec.yaml sets skip_specs: true has no specs to
  // approve (spec-workflow.md): when every unarchived change says so, the pull
  // request is spec-less and waits for the archive only.
  if (await allSkipSpecs(api, tree.entries, changes)) {
    return {
      state: SKIPPED,
      reason: `unarchived change(s) ${changes.join(", ")} all set skip_specs: true`,
    };
  }

  const hash = await packageHash(tree.entries, changes);
  const records = (await api.comments()).map(parseRecord).filter((r): r is Record => r !== null);
  const record = records.sort((a, b) => b.id - a.id)[0];
  const approval = standingApproval(await api.labelEvents());
  const list = changes.join(", ");

  // This run was started by a person adding spec: approved: record it, or say why not.
  if (event && event.action === "labeled" && event.label === APPROVED && !isBot(event.sender)) {
    const refusal = await refuse(api, event, pull, approval);
    if (refusal === null) {
      return {
        state: APPROVED,
        reason: `unarchived change(s) ${list}; approved at ${event.head} by ${event.sender}`,
        record: { id: record?.id, body: recordBody("approved", event.head, event.sender, hash) },
      };
    }
    return {
      state: PENDING,
      reason: `unarchived change(s) ${list}; the approval is not recorded: ${refusal}`,
      record: record?.status === "approved"
        ? {
          id: record.id,
          body: recordBody("withdrawn", record.commit, record.by, record.hash, refusal),
        }
        : undefined,
    };
  }

  // Every other run: keep spec: approved only while the record still holds.
  const problems: string[] = [];
  if (!approval) problems.push(`no standing adding of ${APPROVED} by a person`);
  if (!record) problems.push("no approval record comment");
  else if (record.status !== "approved") problems.push("the approval record is withdrawn");
  // The record belongs to the person whose adding of the label stands. A
  // different person's later adding (say a triage role re-adding after the
  // maintainer removed it) is a new approval attempt that only its own run,
  // with its permission check, may record.
  else if (approval && approval.actor !== record.by) {
    problems.push(
      `${APPROVED} now stands from ${approval.actor}, but the record was made for ${record.by}`,
    );
  } else if (record.hash !== hash) {
    problems.push(`the approval package changed since ${record.commit}`);
  }
  if (problems.length === 0) {
    return {
      state: APPROVED,
      reason: `unarchived change(s) ${list}; approval of ${record!.commit} by ${record!.by} stands`,
    };
  }
  const why = problems.join("; ");
  return {
    state: PENDING,
    reason: `unarchived change(s) ${list}; ${why}`,
    record: record?.status === "approved"
      ? { id: record.id, body: recordBody("withdrawn", record.commit, record.by, record.hash, why) }
      : undefined,
  };
}

/** True when every unarchived change carries `.openspec.yaml` with `skip_specs: true`. */
export async function allSkipSpecs(
  api: Api,
  entries: TreeEntry[],
  changes: string[],
): Promise<boolean> {
  for (const change of changes) {
    const marker = entries.find((e) =>
      e.type === "blob" && e.path === `${CHANGES_DIR}${change}/.openspec.yaml`
    );
    if (!marker) return false;
    if (!skipSpecs(await api.blob(marker.sha))) return false;
  }
  return true;
}

/** True only for a parseable YAML document whose top-level `skip_specs` is the boolean true. */
export function skipSpecs(yaml: string): boolean {
  let doc: unknown;
  try {
    doc = parseYaml(yaml);
  } catch {
    return false;
  }
  return typeof doc === "object" && doc !== null &&
    (doc as { skip_specs?: unknown }).skip_specs === true;
}

async function refuse(
  api: Api,
  event: Event,
  pull: Pull,
  approval: LabelEvent | undefined,
): Promise<string | null> {
  if (!LOGIN_RE.test(event.sender) || !COMMIT_RE.test(event.head)) {
    return "the event names an invalid account or commit";
  }
  if (pull.head !== event.head) return "the head is no longer the commit the event named";
  // The timeline may lag behind the event by a moment: an absent entry is
  // accepted (the event itself is the evidence), a different actor is not.
  if (approval && approval.actor !== event.sender) {
    return `the latest adding of ${APPROVED} by a person is not this event`;
  }
  const permission = await api.permission(event.sender);
  if (permission !== "admin" && permission !== "write") {
    return `${event.sender} has ${permission} permission, below write`;
  }
  return null;
}

/** The label writes that turn `current` into the decided state; none when the decision is to leave the labels. */
export function labelPlan(
  current: string[],
  decision: Decision,
): { add: string[]; remove: string[] } {
  if (decision.leave) return { add: [], remove: [] };
  const { state } = decision;
  const remove = STATE_LABELS.filter((l) => l !== state && current.includes(l));
  const add = state !== null && !current.includes(state) ? [state] : [];
  return { add, remove };
}
