# The Five Variables

Read when settling the variables in step 3, or when the user asks why a
question is being asked. The balance between constraining agents and leaving
them room to find better solutions is set by five independent variables, not
by a project type. [§1.1]

## How to settle each one

1. Look for the evidence listed below. When the repository states the value,
   record it as **observed** with where it was seen; do not ask.
2. When the evidence only suggests a value, write it as an **inference**:
   "I infer <value> from <evidence>; confirm or correct." The user's answer
   settles it.
3. Ask every remaining variable in **one round**, never one per turn. Each
   question carries its typical answers and what each answer pushes, taken
   from the tables below.

## Error cost

What a wrong change costs: lost data, a broken release, a day of cleanup, or
nothing beyond a revert.

- Evidence: rarely observable. A deploy pipeline, migrations, production
  configuration, or payment and user-data code suggest high; say so as an
  inference.
- Typical answers: "nothing, we revert" (low); "a day of cleanup, no data
  lost" (medium); "data loss, outage, or a security incident" (high).
- Pushes: hard-boundary and environment. Higher cost means machine checks
  and isolation, not conventions. [§6.1]

## Maintenance horizon

How long this code is expected to live.

- Evidence: age and steadiness of the history suggest long; a README calling
  it a demo, prototype, or experiment suggests short. Both are inferences.
- Typical answers: "discarded within a quarter" (short); "a year or two";
  "maintained for years" (long).
- Pushes: entropy and knowledge and routing. A short horizon lets entropy be
  omitted or light, because things are thrown away before they rot. [§6.1]

## Environment isolation

How much of a mistake the environment absorbs.

- Evidence: observable. A session running inside a devcontainer or container
  the repository declares is isolated; record it and do not ask. A
  devcontainer file the session is not running in is a fact to report and a
  question ("do agents run inside it?").
- Typical answers: "agents run on the host" (none); "in the devcontainer"
  (container); "in a disposable VM or cloud workspace" (strong).
- Pushes, inversely: hard-boundary and authority. Stronger isolation allows
  looser gates and a wider allow list. [§6.1]

## Autonomy

How long agents work without a person watching.

- Evidence: not observable; always ask unless the invocation sentence states
  it ("work unattended overnight" is unattended).
- Typical answers: "attended, I watch every session" (low); "I check in
  between tasks" (medium); "unattended for hours or overnight" (high).
- Pushes: authority, specification and completion, hard-boundary. Longer
  unattended time needs pre-authorised actions, checkable completion, and
  machine feedback. [§6.1]

## Team size

How many people rely on conventions holding.

- Evidence: distinct authors in `git log` give an inference, never a settled
  value: one author over the whole history is "single maintainer, confirm";
  a CODEOWNERS file or review rules suggest several.
- Typical answers: "just me"; "a small team, two to five"; "many people or
  outside contributors".
- Pushes: hard-boundary and knowledge and routing. More people make
  conventions less reliable, so agreements become files and checks. [§6.1]

## Question round shape

```markdown
I could not observe these from the repository; one answer each:

1. Error cost: what does a bad change cost here? Typical: "revert, nothing
   lost" (thinner checks), "a day of cleanup" (pre-commit and CI checks),
   "data loss or outage" (thick checks and isolation).
2. ...
```
