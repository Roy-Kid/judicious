# Judicious

JUDICIOUS reuse-first is active.

Before writing a new function, class, module, helper, CLI option, parser, retry or validation logic, or adding a dependency:
- Search outward from where you are: the current file and module, then the package API, then other workspace packages, then declared dependencies and the standard library.
- Reuse something only when its semantics, contract and dependency direction fit. A matching name does not mean matching behavior.
- Call the existing code directly. Don't add a forwarding wrapper.
- Don't extract a shared module just to save a few lines between independent units.
- If nothing fits, create the code where it belongs.
- In your final summary, name what you reused (with its path), or say what you searched and why new code was needed.
- If the decision is non-trivial or ambiguous, invoke the `reuse` skill.

## Skills

The commands are skills under `skills/<name>/SKILL.md`. The unified entry is the `judicious` skill (shown as `/judicious` in command examples; invocation syntax depends on the environment). It routes to `reuse`, `placement`, `critique`, `audit`, `init`, `distill`, `consolidate`, `harden`, and `polish`.

Load skills through the environment's supported mechanism or read their current `SKILL.md` files and follow them. No specific skill tool is required.

Merge this card into the project's recognized instruction file when the environment cannot inject it. Install steps are in `INSTALL.md`.
