import { assertEquals, assertStringIncludes } from "@std/assert";
import { fromFileUrl } from "@std/path";
import { runScript } from "./lib/testing.ts";

const repo = fromFileUrl(new URL("../", import.meta.url));
const goodBody =
  `## Summary\n\nx\n\n## Related work\n\nCloses #1\n\n## Verification\n\njust check\n\n## Checklist\n\n- [x] just check passes locally.\n- [x] No secrets, tokens, or private data are in this change.\n`;

Deno.test("check_pr accepts a conventional title and a complete body", () => {
  const body = Deno.makeTempFileSync();
  Deno.writeTextFileSync(body, goodBody);
  const result = runScript("check_pr.ts", [
    "--title",
    "feat(skills): add example skill",
    "--body-file",
    body,
  ], repo);
  assertEquals(result.code, 0, result.output);
});

Deno.test("check_pr rejects a bad title, a missing section, and an unticked security item", () => {
  const body = Deno.makeTempFileSync();
  Deno.writeTextFileSync(
    body,
    goodBody.replace("## Verification\n\njust check\n\n", "").replace(
      "- [x] No secrets",
      "- [ ] No secrets",
    ),
  );
  const result = runScript(
    "check_pr.ts",
    ["--title", "Add Example Skill", "--body-file", body],
    repo,
  );
  assertEquals(result.code, 1);
  assertStringIncludes(result.output, "pr-title");
  assertStringIncludes(result.output, 'section "## Verification" is missing');
  assertStringIncludes(result.output, "pr-security-item");
});
