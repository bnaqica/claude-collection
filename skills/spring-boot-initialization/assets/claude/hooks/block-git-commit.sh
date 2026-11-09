#!/usr/bin/env bash
# PreToolUse hook for the Bash tool.
#
# Project rule: Claude never commits. The developer reviews every change and
# commits it themselves. This hook blocks any git command that creates, rewrites
# or publishes commits, so the rule holds even if an instruction slips through.
#
# Exit code 2 = block the tool call and show stderr to Claude.

set -uo pipefail

input="$(cat)"
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"
else
  cmd="$input"
fi

# `git [global options] <subcommand>` anywhere in the line (after ;, &&, |, $( etc.)
# Only -C and -c take a separate value; every other global option is a single token.
git_opts='([[:space:]]+(-[Cc][[:space:]]+[^[:space:]]+|-[^[:space:]]+))*'
git_writes="(^|[;&|(\`[:space:]])git${git_opts}[[:space:]]+(commit|push|merge|rebase|cherry-pick|revert|am)([[:space:]]|\$)"
gh_writes='(^|[;&|(`[:space:]])gh[[:space:]]+pr[[:space:]]+(create|merge)([[:space:]]|$)'

if printf '%s' "$cmd" | grep -Eq "$git_writes|$gh_writes"; then
  cat >&2 <<'MSG'
Blocked by .claude/hooks/block-git-commit.sh: this project does not let Claude commit,
push, merge, rebase or open PRs. Leave the changes in the working tree, summarize what
changed, and let the developer review and commit them.
MSG
  exit 2
fi

exit 0
