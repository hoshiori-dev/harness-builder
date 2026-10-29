import { assertEquals, assertStringIncludes } from "@std/assert";
import { makeTree, runScript } from "./lib/testing.ts";

Deno.test("sync_labels rejects a description over GitHub's 100-character limit before any gh call", () => {
  const root = makeTree({
    ".github/labels.json": JSON.stringify([
      { name: "ok", color: "0e8a16", description: "x".repeat(100) },
      { name: "long", color: "0e8a16", description: "y".repeat(101) },
    ]),
  });
  const result = runScript("sync_labels.ts", [], root);
  assertEquals(result.code, 2);
  assertStringIncludes(result.output, 'label "long" description is 101 characters');
});
