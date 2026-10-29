# Harness Plan: {{PROJECT}} <!-- # CONFIGURE: {{PROJECT}}: the repository name. -->

Approving this plan authorises creating or changing exactly the files listed
below. Publishing, changing a remote setting, deleting work, and widening
what agents may do on their own are each asked separately when the build
reaches them.

## Goal and non-goals

- Goal: {{GOAL}} <!-- # CONFIGURE: {{GOAL}}: the goal as the user confirmed it, in their words where possible. -->
- Not policed: {{NOT_POLICED}} <!-- # CONFIGURE: {{NOT_POLICED}}: what the harness will not enforce, for example "code style the project never enforced". -->
- Human-only: {{HUMAN_ONLY}} <!-- # CONFIGURE: {{HUMAN_ONLY}}: what stays with people, for example "merging, releases, remote settings". -->
- Not changed in the project: {{NOT_CHANGED}} <!-- # CONFIGURE: {{NOT_CHANGED}}: project changes outside this build, each with the user's answer on recording it as a separate change. -->

## Project profile

- Classification: {{CLASSIFICATION}} <!-- # CONFIGURE: {{CLASSIFICATION}}: greenfield or brownfield, with the evidence. -->
- Stack and layout: {{STACK}} <!-- # CONFIGURE: {{STACK}}: languages, frameworks, top-level layout, each with where it was seen. -->
- Commands and checks kept as sources of truth: {{COMMANDS}} <!-- # CONFIGURE: {{COMMANDS}}: task runner, recipes, CI jobs, hooks already in use; "none" for greenfield. -->

## Variables

| Variable | Value | Settled by |
| --- | --- | --- |
| error cost | {{ERROR_COST}} | {{ERROR_COST_SOURCE}} | <!-- # CONFIGURE: value, then observed (with evidence), confirmed inference, or user answer; same for every row. -->
| maintenance horizon | {{HORIZON}} | {{HORIZON_SOURCE}} | <!-- # CONFIGURE: as above. -->
| environment isolation | {{ISOLATION}} | {{ISOLATION_SOURCE}} | <!-- # CONFIGURE: as above. -->
| autonomy | {{AUTONOMY}} | {{AUTONOMY_SOURCE}} | <!-- # CONFIGURE: as above. -->
| team size | {{TEAM}} | {{TEAM_SOURCE}} | <!-- # CONFIGURE: as above. -->

## Grades

| Layer | Exists now | Grade | Driven by | Evidence and constraining non-goals |
| --- | --- | --- | --- | --- |
| environment | {{ENV_NOW}} | {{ENV_GRADE}} | {{ENV_DRIVERS}} | {{ENV_EVIDENCE}} | <!-- # CONFIGURE: one row per layer; "Exists now" is "nothing" for greenfield; grade omitted, light, medium, or thick as the user confirmed. -->
| knowledge and routing | {{KR_NOW}} | {{KR_GRADE}} | {{KR_DRIVERS}} | {{KR_EVIDENCE}} | <!-- # CONFIGURE: as above. -->
| hard-boundary | {{HB_NOW}} | {{HB_GRADE}} | {{HB_DRIVERS}} | {{HB_EVIDENCE}} | <!-- # CONFIGURE: as above. -->
| authority | {{AU_NOW}} | {{AU_GRADE}} | {{AU_DRIVERS}} | {{AU_EVIDENCE}} | <!-- # CONFIGURE: as above. -->
| specification and completion | {{SC_NOW}} | {{SC_GRADE}} | {{SC_DRIVERS}} | {{SC_EVIDENCE}} | <!-- # CONFIGURE: as above. -->
| entropy | {{EN_NOW}} | {{EN_GRADE}} | {{EN_DRIVERS}} | {{EN_EVIDENCE}} | <!-- # CONFIGURE: as above. -->
| platform lifecycle | {{PL_NOW}} | applies | remote on {{PLATFORM}} | {{PL_EVIDENCE}} | <!-- # CONFIGURE: delete this row and the platform lifecycle section when the remote is neither GitHub nor GitLab or there is none. -->

## Layers

### Environment

- Built by: {{ENVIRONMENT_BUILDER}} <!-- # CONFIGURE: the installed skill whose description claims this layer, or "none installed; built from the methodology manual". -->
- Decisions: {{ENV_DECISIONS}} <!-- # CONFIGURE: isolation choice and the audit items accepted or trimmed. -->
- Files: {{ENV_FILES}} <!-- # CONFIGURE: one path per line, "create" or "change", one-line purpose. -->

### Knowledge and routing

- Built by: {{KNOWLEDGE_AND_ROUTING_BUILDER}} <!-- # CONFIGURE: as above. -->
- Decisions: entrypoint `AGENTS.md`, at most 120 lines; `CLAUDE.md` imports it. {{KR_DECISIONS}} <!-- # CONFIGURE: other choices: knowledge directory, project skills to write. -->
- Files: {{KR_FILES}} <!-- # CONFIGURE: as above. -->

### Hard-boundary

- Built by: {{HARD_BOUNDARY_BUILDER}} <!-- # CONFIGURE: as above. -->
- Decisions: task runner {{RUNNER}}; secret scanner {{SCANNER}}; lint and type-check tools {{LINT_TOOLS}}; management-script language {{SCRIPT_LANGUAGE}}; plugin reference scripts {{REFERENCE_SCRIPTS}}. <!-- # CONFIGURE: each as the user chose; reference scripts "used as they are" or "rewritten in <language>". -->
- Files: {{HB_FILES}} <!-- # CONFIGURE: as above. -->

### Authority

- Built by: {{AUTHORITY_BUILDER}} <!-- # CONFIGURE: as above. -->
- Decisions: deny list {{DENY}}; allow list {{ALLOW}}; approval mode {{APPROVAL}}; commit convention {{CONVENTION}}, no AI attribution; {{CONCURRENCY}}. <!-- # CONFIGURE: as the user chose; {{CONCURRENCY}}: "one agent at a time, so no concurrency rules" unless the user answered that several agents write at once. -->
- Files: {{AU_FILES}} <!-- # CONFIGURE: as above. -->

### Platform lifecycle

- Built by: {{PLATFORM_LIFECYCLE_BUILDER}} <!-- # CONFIGURE: as above. -->
- Decisions: GitHub Flow; merge methods {{MERGE_METHODS}}; labels `type:`, `area:`, `spec:`; bug, feature, and task forms; one request template; no Projects boards or Milestones; releases on tags. <!-- # CONFIGURE: {{MERGE_METHODS}} as the user chose (recommended: squash only); record any deviation the user kept after the challenge. -->
- Files: {{PL_FILES}} <!-- # CONFIGURE: as above. -->
- Remote actions, each asked when reached: {{PL_REMOTE}} <!-- # CONFIGURE: label sync and pushes only, each shown as a dry run first; branch protection, secret scanning, and other repository settings go to Human-only actions. -->

### Specification and completion

- Built by: {{SPECIFICATION_AND_COMPLETION_BUILDER}} <!-- # CONFIGURE: as above. -->
- Decisions: carrier {{CARRIER}}; specifications only for parts under change; handoff files in {{HANDOFF_DIR}}. <!-- # CONFIGURE: {{CARRIER}} and {{HANDOFF_DIR}} as the user chose; recommended `.agents/handoff/`, ignored by git. -->
- Files: {{SC_FILES}} <!-- # CONFIGURE: as above; include `.gitignore` when the handoff files live in the repository. -->

### Entropy

- Built by: {{ENTROPY_BUILDER}} <!-- # CONFIGURE: as above. -->
- Decisions: {{EN_DECISIONS}} <!-- # CONFIGURE: light: sync reminder in the entrypoint; medium: Keep In Sync table or sync skill as chosen, plus the harness self-check; thick: also the second check tier and periodic cleanup. -->
- Files: {{EN_FILES}} <!-- # CONFIGURE: as above. -->

## Commits

Each layer ends in a checkpoint commit in the recorded convention with no
AI attribution. Nothing is pushed unless the user decides so at that step.

## Human-only actions

- {{HUMAN_ACTION}} <!-- # CONFIGURE: one line per platform or remote setting a person applies, with the exact setting; delete the section when there are none. -->

## Open assumptions

- {{ASSUMPTION}} <!-- # CONFIGURE: one line per assumption still unconfirmed and what it would change; delete the section when there are none. -->

## Suggestions for separate changes

- {{SUGGESTION}} <!-- # CONFIGURE: migrations and public-file edits for the team to decide; delete the section when there are none. -->
