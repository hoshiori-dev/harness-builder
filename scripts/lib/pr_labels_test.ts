import { assertEquals, assertRejects, assertStringIncludes } from "@std/assert";
import {
  Api,
  APPROVED,
  ARCHIVED,
  ChangedFile,
  Comment,
  decide,
  Event,
  LabelEvent,
  labelPlan,
  packageHash,
  parseRecord,
  PENDING,
  Pull,
  RECORD_AUTHOR,
  recordBody,
  SKIPPED,
  TreeEntry,
} from "./pr_labels.ts";

const HEAD = "a".repeat(40);
const blob = (path: string, sha = "1".repeat(40)): TreeEntry => ({ path, type: "blob", sha });
const CHANGE = [
  blob("openspec/changes/add-thing/proposal.md"),
  blob("openspec/changes/add-thing/specs/skill/spec.md", "2".repeat(40)),
];
const ARCHIVE = [blob("openspec/changes/archive/2026-10-01-old/proposal.md", "3".repeat(40))];

interface Fixture {
  pull?: Partial<Pull>;
  files?: ChangedFile[];
  entries?: TreeEntry[];
  truncated?: boolean;
  events?: LabelEvent[];
  comments?: Comment[];
  permission?: string;
  blobs?: Record<string, string>;
}
function fake(f: Fixture): Api {
  return {
    pull: () => Promise.resolve({ state: "open", head: HEAD, labels: [], ...f.pull }),
    files: () =>
      Promise.resolve(
        f.files ?? [{ filename: "openspec/changes/add-thing/proposal.md", status: "added" }],
      ),
    tree: () =>
      Promise.resolve({
        entries: f.entries ?? [...ARCHIVE, ...CHANGE],
        truncated: f.truncated ?? false,
      }),
    labelEvents: () => Promise.resolve(f.events ?? []),
    comments: () => Promise.resolve(f.comments ?? []),
    permission: () => Promise.resolve(f.permission ?? "write"),
    blob: (sha) => Promise.resolve(f.blobs?.[sha] ?? ""),
  };
}
const approveEvent: Event = {
  action: "labeled",
  label: APPROVED,
  sender: "maintainer",
  head: HEAD,
};
const approvedBy = (actor: string, id = 10): LabelEvent => ({
  id,
  event: "labeled",
  label: APPROVED,
  actor,
});

Deno.test("skipped when no file under openspec/changes/ is touched", async () => {
  const d = await decide(fake({ files: [{ filename: "README.md", status: "modified" }] }), null);
  assertEquals(d.state, SKIPPED);
});

Deno.test("pending while an unarchived change has no approval", async () => {
  const d = await decide(fake({}), null);
  assertEquals(d.state, PENDING);
  assertStringIncludes(d.reason, "add-thing");
  assertEquals(d.record, undefined);
});

Deno.test("archived when no unarchived change remains and an archive is added", async () => {
  const api = fake({
    entries: ARCHIVE,
    files: [{ filename: "openspec/changes/archive/2026-10-01-old/proposal.md", status: "added" }],
  });
  assertEquals((await decide(api, null)).state, ARCHIVED);
  const removedOnly = fake({
    entries: ARCHIVE,
    files: [{ filename: "openspec/changes/add-thing/proposal.md", status: "removed" }],
  });
  assertEquals((await decide(removedOnly, null)).state, null);
});

Deno.test("a write-permission account adding spec:approved is recorded", async () => {
  const api = fake({ events: [approvedBy("maintainer")] });
  const d = await decide(api, approveEvent);
  assertEquals(d.state, APPROVED);
  assertEquals(d.record?.id, undefined);
  const record = parseRecord({ id: 1, body: d.record!.body, author: RECORD_AUTHOR })!;
  assertEquals(record.status, "approved");
  assertEquals(record.commit, HEAD);
  assertEquals(record.by, "maintainer");
  assertEquals(record.hash, await packageHash([...ARCHIVE, ...CHANGE], ["add-thing"]));
});

Deno.test("the approval is refused below write permission, on a moved head, or for a bot", async () => {
  const read = await decide(
    fake({ events: [approvedBy("maintainer")], permission: "read" }),
    approveEvent,
  );
  assertEquals(read.state, PENDING);
  assertStringIncludes(read.reason, "below write");
  const moved = await decide(fake({ events: [approvedBy("maintainer")] }), {
    ...approveEvent,
    head: "b".repeat(40),
  });
  assertEquals(moved.state, PENDING);
  assertStringIncludes(moved.reason, "no longer the commit");
  const bot = await decide(fake({ events: [approvedBy("github-actions[bot]")] }), {
    ...approveEvent,
    sender: "github-actions[bot]",
  });
  assertEquals(bot.state, PENDING);
});

Deno.test("a standing approval survives unrelated pushes and dies when the package changes", async () => {
  const hash = await packageHash([...ARCHIVE, ...CHANGE], ["add-thing"]);
  const record: Comment = {
    id: 7,
    body: recordBody("approved", HEAD, "maintainer", hash),
    author: RECORD_AUTHOR,
  };
  const same = await decide(
    fake({
      events: [approvedBy("maintainer")],
      comments: [record],
      pull: { head: "c".repeat(40) },
    }),
    null,
  );
  assertEquals(same.state, APPROVED);
  assertEquals(same.record, undefined);

  const edited = fake({
    events: [approvedBy("maintainer")],
    comments: [record],
    entries: [
      ...ARCHIVE,
      blob("openspec/changes/add-thing/proposal.md", "9".repeat(40)),
      CHANGE[1],
    ],
  });
  const d = await decide(edited, null);
  assertEquals(d.state, PENDING);
  assertStringIncludes(d.reason, "package changed");
  assertEquals(d.record?.id, 7);
  assertEquals(
    parseRecord({ id: 7, body: d.record!.body, author: RECORD_AUTHOR })?.status,
    "withdrawn",
  );
});

Deno.test("a record approves only the person whose adding of the label stands", async () => {
  const hash = await packageHash([...ARCHIVE, ...CHANGE], ["add-thing"]);
  const record: Comment = {
    id: 7,
    body: recordBody("approved", HEAD, "maintainer", hash),
    author: RECORD_AUTHOR,
  };
  const events: LabelEvent[] = [
    approvedBy("maintainer", 10),
    { id: 11, event: "unlabeled", label: APPROVED, actor: "maintainer" },
    approvedBy("triager", 12),
  ];
  const d = await decide(fake({ events, comments: [record], pull: { labels: [APPROVED] } }), null);
  assertEquals(d.state, PENDING);
  assertStringIncludes(d.reason, "record was made for maintainer");
  assertEquals(
    parseRecord({ id: 7, body: d.record!.body, author: RECORD_AUTHOR })?.status,
    "withdrawn",
  );
  // The same person removing and re-adding keeps their own record.
  const own = [approvedBy("maintainer", 10), {
    id: 11,
    event: "unlabeled" as const,
    label: APPROVED,
    actor: "maintainer",
  }, approvedBy("maintainer", 12)];
  assertEquals((await decide(fake({ events: own, comments: [record] }), null)).state, APPROVED);
});

Deno.test("a person removing spec:approved, or a label without a record, means pending", async () => {
  const hash = await packageHash([...ARCHIVE, ...CHANGE], ["add-thing"]);
  const record: Comment = {
    id: 7,
    body: recordBody("approved", HEAD, "maintainer", hash),
    author: RECORD_AUTHOR,
  };
  const removed = await decide(
    fake({
      events: [approvedBy("maintainer"), {
        id: 11,
        event: "unlabeled",
        label: APPROVED,
        actor: "maintainer",
      }],
      comments: [record],
    }),
    null,
  );
  assertEquals(removed.state, PENDING);
  const noRecord = await decide(
    fake({ events: [approvedBy("maintainer")], pull: { labels: [APPROVED] } }),
    null,
  );
  assertEquals(noRecord.state, PENDING);
  assertEquals(labelPlan([APPROVED, "type:task"], noRecord), {
    add: [PENDING],
    remove: [APPROVED],
  });
});

Deno.test("a record comment from anyone but the workflow identity is ignored", async () => {
  const hash = await packageHash([...ARCHIVE, ...CHANGE], ["add-thing"]);
  const body = recordBody("approved", HEAD, "maintainer", hash);
  const forged: Comment = { id: 9, body, author: "contributor" };
  const otherBot: Comment = { id: 10, body, author: "dependabot[bot]" };
  for (const comments of [[forged], [otherBot], [forged, otherBot]]) {
    const api = fake({
      events: [approvedBy("maintainer")],
      comments,
      pull: { labels: [APPROVED] },
    });
    const d = await decide(api, null);
    assertEquals(d.state, PENDING);
    assertStringIncludes(d.reason, "no approval record");
    assertEquals(d.record, undefined, "a forged record is never edited");
  }
});

Deno.test("a change whose .openspec.yaml sets skip_specs: true is spec-less", async () => {
  const marker = blob("openspec/changes/add-thing/.openspec.yaml", "5".repeat(40));
  const skipped = fake({
    entries: [...ARCHIVE, ...CHANGE, marker],
    blobs: { ["5".repeat(40)]: "schema: spec-driven\nskip_specs: true\n" },
  });
  assertEquals((await decide(skipped, null)).state, SKIPPED);
  const notSkipped = fake({
    entries: [...ARCHIVE, ...CHANGE, marker],
    blobs: { ["5".repeat(40)]: "skip_specs: false\n" },
  });
  assertEquals((await decide(notSkipped, null)).state, PENDING);
  const second = blob("openspec/changes/other/proposal.md", "6".repeat(40));
  const mixed = fake({
    entries: [...ARCHIVE, ...CHANGE, marker, second],
    blobs: { ["5".repeat(40)]: "skip_specs: true\n" },
  });
  assertEquals(
    (await decide(mixed, null)).state,
    PENDING,
    "one change without the marker keeps the gate",
  );
});

Deno.test("skip_specs is read as a YAML document, not as text", async () => {
  const { skipSpecs } = await import("./pr_labels.ts");
  assertEquals(skipSpecs("schema: spec-driven\nskip_specs: true\n"), true);
  assertEquals(
    skipSpecs("notes: |\n  skip_specs: true\nskip_specs: false\n"),
    false,
    "block scalar",
  );
  assertEquals(skipSpecs("nested:\n  skip_specs: true\n"), false, "nested");
  assertEquals(skipSpecs('skip_specs: "true"\n'), false, "string");
  assertEquals(skipSpecs("skip_specs: [unclosed\n"), false, "invalid yaml");
  const marker = blob("openspec/changes/add-thing/.openspec.yaml", "5".repeat(40));
  const tricked = fake({
    entries: [...ARCHIVE, ...CHANGE, marker],
    blobs: { ["5".repeat(40)]: "notes: |\n  skip_specs: true\nskip_specs: false\n" },
  });
  assertEquals((await decide(tricked, null)).state, PENDING);
});

Deno.test("an approval whose timeline entry has not appeared yet is still recorded", async () => {
  const d = await decide(fake({ events: [] }), approveEvent);
  assertEquals(d.state, APPROVED);
  const other = await decide(fake({ events: [approvedBy("someone-else")] }), approveEvent);
  assertEquals(other.state, PENDING);
});

Deno.test("archiving is recognised whatever status the archive files carry", async () => {
  for (const status of ["added", "renamed", "modified"]) {
    const files = [{ filename: "openspec/changes/archive/2026-10-01-old/proposal.md", status }];
    assertEquals((await decide(fake({ entries: ARCHIVE, files }), null)).state, ARCHIVED, status);
  }
});

Deno.test("closed pull requests keep their labels; truncated trees are not decided", async () => {
  const closed = await decide(
    fake({ pull: { state: "closed", labels: [ARCHIVED, "type:task"] } }),
    null,
  );
  assertEquals(closed.state, null);
  assertEquals(closed.leave, true);
  assertEquals(labelPlan([ARCHIVED, "type:task"], closed), { add: [], remove: [] });
  await assertRejects(() => decide(fake({ truncated: true }), null), Error, "truncated");
});
