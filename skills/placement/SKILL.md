---
name: placement
description: Decides where code should live — keep, move, extract into a shared unit, lower into a core layer or dependency (including across Python/Rust/WASM boundaries), or remove. Use when code may sit in the wrong module or package, when an upper package re-implements what its core library should own, or when a critique finding says to move or lower code. Read-only; returns a located migration plan.
argument-hint: "[path, symbol or critique finding]"
license: MIT
---


# placement

**Question:** Where should this code live?

**Mode:** read-only. This skill produces a decision and a migration plan. Editing happens after approval.

## Input
- **Target:** a path, a symbol, or a finding from an earlier report. When the target is a finding, start from its Locations (see **Appendix: Report**).
- Read both sides: the code where it lives now, and the candidate destination. For lowering, that means the core library's source and its bindings.

## Procedure
1. **State the responsibility** in one line. Name the unit that owns that domain according to the project docs and manifests.
2. **List the consumers**, with `path:line`. Include consumers in sibling repositories you can read.
3. **Check the destination** for an existing equivalent. If one exists, the answer is reuse, not a move.
4. For `LOWER`, run every check in **Appendix: Lowering**. For `EXTRACT`, apply **Appendix: Disqualifiers**.
5. **Decide:**

| Decision | When |
|---|---|
| `KEEP` | The current owner is right. |
| `MOVE` | Another existing unit owns this responsibility. |
| `EXTRACT` | At least two real consumers share the same semantics. |
| `LOWER` | The logic is domain-free, the lower layer owns the domain, and the boundary cost is justified. |
| `REMOVE` | Nothing needs it: there are no consumers, or the destination already provides it. |

## Output
```
Responsibility: …   Owner by project rules: …
Consumers: path:line, …
Decision: KEEP | MOVE | EXTRACT | LOWER | REMOVE   confidence: … (Appendix: Evidence)
Why: … (checks passed or failed, citing Appendix: Lowering)
Plan (not for KEEP), in order, each step independently verifiable:
1. <repo>:path:line → <repo>:path(:line) — what moves, new API name and signature
2. bindings/exports to add: path
3. callers to switch: path:line, …
4. what to delete afterwards: path:line
5. release/order constraints (e.g. molrs release before molpy pin bump)
Risks / unverified: …
Next: …
```
- Never edit files yourself.
- For `MOVE`, `EXTRACT`, `LOWER` or `REMOVE`, Next is "approve the plan → implement it with native planning", followed by `/judicious consolidate` for whatever duplicates the plan leaves behind, and `/judicious critique --changed`.

## Appendix: Lowering

Lowering is an architectural decision, not a code move.

### Checks
- **Domain-free:** does the logic have meaning on its own, without upper-layer policy?
- **Real consumers:** are there two or more consumers today, or a consumer in another package or runtime?
- **Ownership:** does the lower layer already own this domain, for example its formats, geometry or IR?
- **Direction:** would lowering make the lower layer depend on upper-layer types or policy?
- **Boundary cost:** what do ABI, FFI, WASM, serialization or binding work cost, compared with the reuse it buys?
- **API growth:** would the lower layer's API bloat for a single caller?
- **Testing, performance and release:** what changes, given that both repositories must release in lock-step?
- **Simpler path:** is it enough to reuse the existing lower-layer API without moving anything?

### Do not lower when
- The logic depends on upper-layer domain policy.
- Lowering would reverse the dependency direction.
- Consumers need different semantics.
- The cross-language cost exceeds the reuse benefit.
- Sharing is unproven.
- The only argument is "it could be faster in Rust".

## Appendix: Disqualifiers

Any one of these rules out reuse, merging or extraction. Record which ones you checked.

- **Semantic mismatch:** inputs, outputs, edge cases or invariants differ from the need. Example: a lossy slugifier named `normalize`.
- **Contract mismatch:** the error model, side effects or stability are unacceptable. Example: a private helper with no stability promise.
- **Invalid dependency direction:** reuse would make a lower or independent unit depend on a higher one, or create a cycle.
- **Lifecycle divergence:** the two sides change for different reasons or owners. Example: a frozen wire format versus a display string.
- **Boundary cost exceeds benefit:** crossing a process, language, ABI or deployment boundary costs more than the duplication it saves.
- **Unproven sharing:** only one real consumer exists today.
- **Policy leakage:** the candidate carries domain policy that the new context must not inherit.
- **Project constraint:** a README, architecture doc, CLAUDE.md, AGENTS.md or manifest rule forbids it.

When one of these holds, the usual answer is `CREATE`, `EXTEND` behind a separate entry point, or keeping the implementations apart.

## Appendix: Evidence

### Strength
- **Strong:** code you read, cited as `path:line` or a symbol. Also call sites, manifests, tests, and docs that state a rule.
- **Medium:** search hits you have not opened, and naming conventions combined with partial reads.
- **Weak:** names alone, or general experience. Never base a finding on weak evidence alone.

### Confidence
- **High:** the code and its callers are read, and no plausible exception remains.
- **Medium:** the core claim is verified, but consumers or edge cases are only partly checked.
- **Low:** an inference. Name the check that would settle it.

### Search outcomes
- `FOUND`: cite the location.
- `NOT_FOUND_IN_SCOPE`: nothing suitable within the stated scope. Never claim global absence.
- `UNKNOWN`: the search could not finish, for example because of generated code, dynamic dispatch, or missing tools.

### Coverage
- Always state what you searched or read, what you skipped, and what you could not see, such as external consumers or dynamic uses.
- Never present a semantic judgment as if it were static-analysis output.

### Evidence receipt
Emit one only when the result goes to another context, for example a subagent hand-off. Use these keys: `capability`, `scope`, `revision`, `decision`, `canonical`, `evidence`, `disqualifiers_checked`, `unknown`. A receipt is a claim, not a ruling: re-check it before acting on it.

## Appendix: Report

Every Judicious report follows these rules.

### Locate everything
- Each issue, candidate or change cites the exact `path:line` (or a line range) of every place involved. That covers the definition, the call sites to change, and the manifest or doc line.
- **Locations** is the to-do list for whoever acts on the finding. List every place that must change, not just one example.
- Never report an issue without a location. If you cannot locate it, say so and lower the confidence.
- When acting on an earlier report, start from its Locations. Re-read them to verify, but do not search for them again.

### End with the next step
- The last section is **Next**: one to three recommended commands, in order, each with its exact target and a one-line reason.
  - Example: `/judicious harden src/molpy/engine/_openmm.py:440-444`, because NVE silently runs a thermostat.
- Recommend only commands that exist. If the right move is a plain bug fix or a native plan, say that instead.
- If nothing is left to do, write `Next: none` and give the reason.
