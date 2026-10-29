# Tools and Their Quiet Flags

Read when listing candidate tools for a check or writing any check command
into a hook, recipe, or CI job. Each row lists the recommended tool first,
then the alternatives; present them that way and configure only the tool
the user names. The quiet column is what the recipe runs. [§3.1]

Before writing a flag, confirm it in `<tool> --help` of the version the
project pins: flags change between major versions. A flag that does not
exist fails the check on its first run.

## Python

| Role | Candidates (recommended first) | Quiet command |
|---|---|---|
| Format | **ruff format**; black | `ruff format --check --quiet` (hook: `ruff format --quiet`) |
| Lint | **ruff check**; flake8, pylint | `ruff check --output-format concise --quiet` |
| Typecheck | **pyright**; mypy | `pyright` (one line per diagnostic already); `mypy --no-error-summary` |
| Test | **pytest**; unittest | `pytest -q --tb=short --no-header` |

## TypeScript and JavaScript

| Role | Candidates (recommended first) | Quiet command |
|---|---|---|
| Format | **prettier**; biome | `prettier --check --log-level warn .`; `biome format .` |
| Lint | **eslint**; biome, oxlint | `eslint --quiet .` (hides warnings: a rule that must block is set to `error`); `biome lint --diagnostic-level=error .` |
| Typecheck | **tsc** | `tsc --noEmit --pretty false` |
| Test | **vitest**; jest, `node --test` | `vitest run --reporter=dot --silent`; `jest --ci --silent`; `node --test --test-reporter=dot` |
| Runner | the package manager | `npm run --silent <script>`; `pnpm --silent <script>` |

## Deno

| Role | Tool | Quiet command |
|---|---|---|
| Format | deno fmt | `deno fmt --check --quiet` |
| Lint | deno lint | `deno lint --compact` |
| Typecheck | deno check | `deno check --quiet .` |
| Test | deno test | `deno test --quiet --reporter=dot` |

## Go

| Role | Candidates (recommended first) | Quiet command |
|---|---|---|
| Format | **gofmt**; goimports | recipe body `out=$(gofmt -l .); printf '%s' "$out"; test -z "$out"` (prints the unformatted files and fails when any exist) |
| Lint | **golangci-lint**; go vet, staticcheck | `golangci-lint run`; `go vet ./...` |
| Typecheck | the compiler | `go build ./...` |
| Test | **go test** | `go test ./...` (never `-v` in a gate) |

## Rust

| Role | Candidates | Quiet command |
|---|---|---|
| Format | rustfmt | `cargo fmt --check` |
| Lint | clippy | `cargo clippy -q --message-format=short -- -D warnings` |
| Typecheck | the compiler | `cargo check -q --message-format=short` |
| Test | cargo test | `cargo test -q` |

## JVM, .NET, Ruby

| Ecosystem | Role | Candidates (recommended first) | Quiet command |
|---|---|---|---|
| Gradle | all | **the project's Gradle tasks** (spotless, detekt or checkstyle, test) | `./gradlew -q --console=plain <task>` |
| Maven | all | **the project's plugins** | `mvn -q -B <goal>` |
| .NET | format | **dotnet format** | `dotnet format --verify-no-changes --verbosity quiet` |
| .NET | lint, typecheck | **the build with analyzers** | `dotnet build -warnaserror -v q -nologo` |
| .NET | test | **dotnet test** | `dotnet test -v q --nologo` |
| Ruby | format, lint | **rubocop**; standardrb | `rubocop --format emacs` |
| Ruby | test | **rspec**; minitest | `rspec --format progress` |

## Secret scan and files without a language

| Role | Candidates (recommended first) | Command |
|---|---|---|
| Secret scan | **betterleaks**; gitleaks, TruffleHog | `betterleaks dir . --no-banner --redact`; `gitleaks dir . --no-banner --redact`; `trufflehog filesystem . --fail --no-update --results=verified,unknown` |
| Shell | **shellcheck** | `shellcheck -f gcc <files>` |
| YAML | **yamllint** | `yamllint -f parsable .` |

Install paths for the scanners: betterleaks and gitleaks ship release
binaries on their GitHub release pages (verify the published checksum);
TruffleHog ships release binaries and a container image. Installing a tool
into the agent environment is the environment layer's work; this layer
names the tool and its version.

## When a tool has no quiet mode

Keep the native output and add one sentence to the knowledge file:
"`<tool>` prints full logs; no compact flag exists; accepted." Do not
write a parser, filter, or `| grep` wrapper; a scoped command (one file,
one package) is the only other remedy. [§3.1]
