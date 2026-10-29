#!/usr/bin/env -S deno run --allow-read
// Lists the unarchived OpenSpec changes of the working tree: every directory
// directly under openspec/changes/ except archive/. Exit 0 when there is none
// (the tree may be merged), 1 while one exists (names on stdout), 2 on an
// unexpected error. The pr workflow's archive-verdict job turns status 1 into
// the absence of the `checks / spec-archived` required check.
import { join } from "@std/path";
import { fail, isDirectory, listDir } from "./lib/findings.ts";

if (Deno.args.length > 0) fail(`unknown arguments ${Deno.args.join(" ")}; this script takes none`);

const dir = join(Deno.cwd(), "openspec/changes");
const unarchived = isDirectory(dir)
  ? listDir(dir).filter((e) => e.isDirectory && e.name !== "archive").map((e) => e.name)
  : [];

if (unarchived.length === 0) {
  console.log("check_spec_archived: no unarchived change");
  Deno.exit(0);
}
for (const name of unarchived) {
  console.log(
    `openspec/changes/${name}: unarchived change. Fix: archive it on the branch before merging (openspec-archive-change).`,
  );
}
Deno.exit(1);
