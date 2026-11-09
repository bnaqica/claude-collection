# Development workflow

OpenSpec decides what to build. Superpowers keeps the building disciplined. The two don't connect by themselves;
these rules connect them.

## Which path to take

| Work | Path |
|---|---|
| New feature, or a change to behaviour or an API | The OpenSpec steps below |
| Bug | `superpowers:systematic-debugging`; use OpenSpec only if the fix changes specified behaviour |
| Small change with no behaviour change | Make it directly, then verify |

## OpenSpec steps

1. **Explore (optional).** Use `/opsx:explore` to think through an unclear idea.
2. **Propose.** Run `/opsx:propose <feature>`. It writes `proposal.md`, `specs/`, `design.md` and `tasks.md` to
   `openspec/changes/<change-id>/`. Don't also use `superpowers:brainstorming` or `superpowers:writing-plans`:
   two plans for one feature drift apart. Specs describe behaviour rather than implementation.
3. **Review.** Stop until the developer has reviewed the proposal's scope and `tasks.md`.
4. **Apply.** Run `/opsx:apply`. For every task, invoke `superpowers:test-driven-development` before writing code, so
   the failing test comes first. `openspec/config.yaml` passes this to apply as guidance.
5. **Review.** When all tasks are complete, invoke `superpowers:requesting-code-review`, as described under Code review.
6. **Verify.** Follow `superpowers:verification-before-completion`, running `./gradlew spotlessApply build` and reading
   the result.
7. **Archive.** After the developer has reviewed the changes, run `/opsx:archive` as the last step. It merges the change
   into `openspec/specs/`. Skipping it leaves later sessions unaware of what was built.

## Code review

Any code review goes through `superpowers:requesting-code-review`, whether it comes from `/opsx:apply` or the developer
asks for one. That skill compares two commits, but nothing here is committed, so its diff would be empty. Replace its
git SHA steps and its `general-purpose` subagent with the `code-reviewer` agent, which reviews uncommitted changes.
Give the agent a description of what was built and the requirements, which for a feature is the path to
`openspec/changes/<change-id>/`. Everything else in the skill still applies, including fixing Critical and Important
issues before moving on.

## Where project rules override these tools

- **No commits.** Skip every commit step, as `.claude/rules/git-workflow.md` says, including the commit at the end of a
  TDD cycle.
- **Never delete code to satisfy TDD.** The TDD skill says to delete code written before its test. Nothing here is
  committed, so that work couldn't be recovered. If code has no test, write the test or ask the developer.
- **No worktrees or branch workflows.** Don't use `superpowers:using-git-worktrees` or
  `superpowers:finishing-a-development-branch`. Work stays uncommitted, so it has to be in the developer's working tree.
