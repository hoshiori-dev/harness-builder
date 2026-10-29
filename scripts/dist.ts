#!/usr/bin/env -S deno run --allow-read --allow-write --allow-run=git
// Builds the release archive: the plugin payload (portable files, bundled
// server code, client namespaces, and every registered client's generated
// files, without which the archive loads in no client that needs a pointer
// manifest or a converted MCP file) as dist/<name>-<version>.zip from the
// committed tree, so untracked files never ship.
//
//   dist.ts [--tag vX.Y.Z]   with --tag, fail unless X.Y.Z equals plugin.json#version
import { join } from "@std/path";
import { CLIENTS } from "./lib/clients.ts";
import { fail } from "./lib/findings.ts";
import { loadManifest } from "./lib/plugin.ts";

const root = Deno.cwd();
const { manifest, errors } = loadManifest(root);
if (errors.length > 0) {
  fail(`plugin.json violates the Agent Plugins schema:\n  ${errors.join("\n  ")}`);
}
if (manifest.version === undefined) fail("plugin.json has no version; a release needs one.");

const tagIndex = Deno.args.indexOf("--tag");
if (tagIndex !== -1) {
  const tag = Deno.args[tagIndex + 1];
  if (!tag || !/^v\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$/.test(tag)) {
    fail(`tag "${tag ?? ""}" is not vX.Y.Z. Fix: tag releases as v<plugin.json version>.`);
  }
  if (tag.slice(1) !== manifest.version) {
    fail(
      `tag ${tag} does not match plugin.json version ${manifest.version}. Fix: bump the version or retag.`,
    );
  }
}

const payload = [
  "plugin.json",
  "mcp.json",
  "LICENSE",
  "README.md",
  "skills",
  "mcp",
  ...[...Deno.readDirSync(root)].filter((e) => e.isDirectory && e.name.startsWith("com.")).map((
    e,
  ) => e.name),
  // The generated client files: without them the archive loads in no client
  // that needs a pointer manifest or a converted MCP file (client-matrix.md).
  ...CLIENTS.flatMap((c) => c.generatedFiles),
].filter((p) => {
  try {
    Deno.lstatSync(join(root, p));
    return true;
  } catch {
    return false;
  }
}).sort();

Deno.mkdirSync(join(root, "dist"), { recursive: true });
const archive = `dist/${manifest.name}-${manifest.version}.zip`;
const result = new Deno.Command("git", {
  args: [
    "archive",
    "--format=zip",
    `--prefix=${manifest.name}/`,
    "-o",
    archive,
    "HEAD",
    "--",
    ...payload,
  ],
  cwd: root,
  stderr: "piped",
}).outputSync();
if (!result.success) {
  fail(
    `git archive exited ${result.code}: ${
      new TextDecoder().decode(result.stderr).trim()
    } (every payload path must be committed)`,
  );
}
console.log(`wrote ${archive} (${payload.join(", ")})`);
