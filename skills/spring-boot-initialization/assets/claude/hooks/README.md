# Hooks

Hook scripts referenced from `.claude/settings.json`.

| Script | Event | What it does |
|---|---|---|
| `block-git-commit.sh` | `PreToolUse` (Bash) | Blocks `git commit/push/merge/rebase/cherry-pick/revert/am` and `gh pr create/merge`, so Claude never commits. The developer reviews and commits every change. |

Test it:

```bash
echo '{"tool_input":{"command":"git commit -m x"}}' | .claude/hooks/block-git-commit.sh; echo "exit $?"   # exit 2 = blocked
echo '{"tool_input":{"command":"git status"}}'      | .claude/hooks/block-git-commit.sh; echo "exit $?"   # exit 0 = allowed
```
