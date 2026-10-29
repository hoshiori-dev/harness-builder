# {{PROJECT_NAME}} <!-- # CONFIGURE: {{PROJECT_NAME}}: the project's name. -->

{{PURPOSE}} <!-- # CONFIGURE: {{PURPOSE}}: one or two sentences: what the project is and who uses it. -->

## Always

- Never commit secrets, credentials, or personal data.
- Run `{{CHECK_RECIPE}}` before reporting work done; work with a red check is not done. <!-- # CONFIGURE: {{CHECK_RECIPE}}: the aggregate recipe, e.g. `just check`. -->
- {{ALWAYS_RULE}} <!-- # CONFIGURE: {{ALWAYS_RULE}}: one line per further rule whose breach harms regardless of task type (commit and publish limits, language, generated files). Keep every such rule; delete the line when there is none. -->

Top-level directories: <!-- # CONFIGURE: delete this line and the block below when an architecture document carries the map, and route to that document in When To Read What instead. -->

```text
{{DIRECTORY}}/    <- {{ROLE}}  # CONFIGURE: one line per long-lived top-level directory.
```

## When To Read What

| Situation | Read |
|---|---|
| {{SITUATION}} | `{{KNOWLEDGE_DIR}}/{{FILE}}.md` | <!-- # CONFIGURE: one row per knowledge file; {{KNOWLEDGE_DIR}}: the knowledge folder recorded in step 2; the situation repeats the file's "Read this when" line. Single-file harness: delete this row. -->
| {{CRITICAL_SITUATION}} | load the `{{SKILL}}` skill | <!-- # CONFIGURE: one row per process-critical project skill; delete otherwise. Delete the whole section when no row remains. -->

## Validation

| Check | Recipe |
|---|---|
| Everything CI runs | `{{CHECK_RECIPE}}` | <!-- # CONFIGURE: one row per recipe read from the task runner; recipe names, never the raw commands. -->

## Keep In Sync

<!-- harness: keep-in-sync -->
