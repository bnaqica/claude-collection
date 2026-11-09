# Software design principles

Every change follows these. When two pull against each other, prefer the simpler design.

## SOLID

- **Single responsibility**: a class has one reason to change. If describing it takes "and", split it.
- **Open/closed**: add behaviour with a new implementation of an existing abstraction rather than a growing `switch`.
- **Liskov substitution**: an implementation honours its interface's contract, with no surprise exceptions or no-ops.
- **Interface segregation**: keep interfaces small and focused on what their callers use.
- **Dependency inversion**: depend on abstractions at layer boundaries, and inject them.

## DRY

Each piece of knowledge lives in one place. Extract duplication once it's the same rule, not just similar-looking code.

## KISS

Pick the simplest thing that solves the actual problem. Readable beats clever, and fewer moving parts beats more.

## YAGNI

Build what's needed now. No speculative options, extension points or abstractions for requirements nobody has.
Where a rule in this repo requires a structure, follow the rule; YAGNI applies to anything beyond it.
