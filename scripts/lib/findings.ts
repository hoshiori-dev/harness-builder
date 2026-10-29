// Shared reporting for the project's management scripts.
//
// A finding is a problem in a committed file that the person or agent fixing
// it must act on: it names the file, the rule, the problem, and the fix. The
// scripts collect findings and exit 1 once, at the end. An unexpected failure
// of a script itself (unreadable file, missing tool) is not a finding: it
// exits 2 immediately through `fail`, with a message naming what was wrong.

export interface Finding {
  file: string;
  line?: number;
  rule: string;
  problem: string;
  fix: string;
}

export class Findings {
  readonly items: Finding[] = [];

  add(finding: Finding): void {
    this.items.push(finding);
  }

  /** Prints every finding and a summary line; returns the process exit code. */
  report(label: string): number {
    for (const f of this.items) {
      const where = f.line === undefined ? f.file : `${f.file}:${f.line}`;
      console.log(`${where}: ${f.rule}: ${f.problem} Fix: ${f.fix}`);
    }
    if (this.items.length === 0) {
      console.log(`${label}: ok`);
      return 0;
    }
    console.log(`${label}: ${this.items.length} finding(s)`);
    return 1;
  }
}

/** Unexpected failure of the script itself: print and exit 2. */
export function fail(message: string): never {
  console.error(`error: ${message}`);
  Deno.exit(2);
}

export function exists(path: string): boolean {
  try {
    Deno.lstatSync(path);
    return true;
  } catch (error) {
    if (error instanceof Deno.errors.NotFound) return false;
    throw error;
  }
}

export function isDirectory(path: string): boolean {
  try {
    return Deno.statSync(path).isDirectory;
  } catch (error) {
    if (error instanceof Deno.errors.NotFound) return false;
    throw error;
  }
}

export function readText(path: string): string {
  try {
    return Deno.readTextFileSync(path);
  } catch (error) {
    return fail(`cannot read ${path}: ${(error as Error).message}`);
  }
}

/** Reads and parses a JSON file; a parse error is an unexpected failure. */
export function readJson(path: string): unknown {
  const text = readText(path);
  try {
    return JSON.parse(text);
  } catch (error) {
    return fail(`${path} is not valid JSON: ${(error as Error).message}`);
  }
}

/** Sorted directory entries, so every listing is deterministic. */
export function listDir(path: string): Deno.DirEntry[] {
  const entries = [...Deno.readDirSync(path)];
  entries.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));
  return entries;
}

/** Files git tracks or would track: committed files plus untracked, not-ignored ones. */
export function gitFiles(root: string): string[] {
  const result = new Deno.Command("git", {
    args: ["ls-files", "--cached", "--others", "--exclude-standard", "-z"],
    cwd: root,
    stdout: "piped",
    stderr: "piped",
  }).outputSync();
  if (!result.success) {
    fail(`git ls-files exited ${result.code}: ${new TextDecoder().decode(result.stderr).trim()}`);
  }
  return new TextDecoder().decode(result.stdout).split("\0").filter((p) => p.length > 0).sort();
}

/** The symlink's target, or null when the path is missing or not a symlink. */
export function readLinkOrNull(path: string): string | null {
  try {
    if (!Deno.lstatSync(path).isSymlink) return null;
  } catch (error) {
    if (error instanceof Deno.errors.NotFound) return null;
    throw error;
  }
  return Deno.readLinkSync(path);
}
