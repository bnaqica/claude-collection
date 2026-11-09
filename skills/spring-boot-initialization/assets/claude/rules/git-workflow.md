# Git: Claude never commits

The developer reviews every file and makes every commit themselves.

- Do **not** run `git commit`, `git push`, `git merge`, `git rebase`, `git cherry-pick`,
  `git revert`, `git am`, `gh pr create` or `gh pr merge`. `.claude/hooks/block-git-commit.sh`
  blocks them, and `.claude/settings.json` denies them.
- Do not stage (`git add`) unless the developer asks.
- Read-only git is fine: `status`, `diff`, `log`, `show`, `blame`.
- When a workflow or skill (including superpowers and OpenSpec) says to commit, skip that
  step: leave the changes in the working tree and list the files you changed.
- Finish each task with a short summary of what changed and why, so it is easy to review.
