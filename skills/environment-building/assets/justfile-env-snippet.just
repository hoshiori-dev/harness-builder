# Every command run through a recipe is non-interactive: no pager, no
# credential prompt, no watch mode, no "[y/N]" confirmation. Agents run
# project commands through these recipes so the settings below apply.

export CI := "true"
export PAGER := "cat"
export GIT_PAGER := "cat"
export GIT_TERMINAL_PROMPT := "0"
# CONFIGURE: one export per ecosystem variable the project's tools read, or delete this line: {{ECOSYSTEM_VARIABLES}}
