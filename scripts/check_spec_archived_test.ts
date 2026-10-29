import { assertEquals, assertStringIncludes } from "@std/assert";
import { makeTree, runScript } from "./lib/testing.ts";

Deno.test("check_spec_archived passes without openspec/changes and with archived changes only", () => {
  const bare = makeTree({ "plugin.json": "{}\n" });
  assertEquals(runScript("check_spec_archived.ts", [], bare).code, 0);

  const archived = makeTree({
    "openspec/changes/archive/2026-10-27-add-thing/proposal.md": "# done\n",
    "openspec/changes/README.md": "plain files are not changes\n",
  });
  const result = runScript("check_spec_archived.ts", [], archived);
  assertEquals(result.code, 0, result.output);
  assertStringIncludes(result.output, "no unarchived change");
});

Deno.test("check_spec_archived exits 1 naming every unarchived change", () => {
  const root = makeTree({
    "openspec/changes/archive/old/proposal.md": "# done\n",
    "openspec/changes/add-thing/proposal.md": "# wip\n",
    "openspec/changes/fix-other/proposal.md": "# wip\n",
  });
  const result = runScript("check_spec_archived.ts", [], root);
  assertEquals(result.code, 1);
  assertStringIncludes(result.output, "openspec/changes/add-thing: unarchived change");
  assertStringIncludes(result.output, "openspec/changes/fix-other: unarchived change");
});
