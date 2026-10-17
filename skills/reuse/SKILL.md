---
name: reuse
description: Use before writing new code — adding a function, helper, class, module, CLI option, config loading, parsing, retry/backoff, validation, checksum or other utility logic, or a new dependency. Checks whether the codebase, its workspace packages, declared dependencies or the standard library already provide it, then decides reuse, extend or create. Read-only; the caller implements the decision.
argument-hint: "[need, symbol or path] [--changed]"
license: MIT
---


# reuse

**Question:** Does a capability that meets this need already exist, and should it be used?

**Mode:** read-only. This skill decides; the caller implements.

## Input
- **Target:** a need described in words, a symbol about to be created, or a file.
- **No target:** the pending change.
- **`--changed`:** every new unit in the git diff.
- First restate the need in one line: inputs, outputs, edge cases, call site. Judge candidates against that line, not against names.

## Search (nearest first; widen only when a lead points further)
1. The current file and its neighbours.
2. The current package's public API.
3. Other workspace packages or crates (manifests, exports, READMEs).
4. Declared dependencies and the standard library.
5. Transitive or vendored code, only with a concrete lead.
- Search by behavior: domain nouns, data formats, synonyms. For each hit, read its body, docstring and tests.
- Do not crawl third-party source.

## Evaluate each candidate
- **Semantics, including edge cases.** The same name does not mean the same behavior.
- **Contract:** is it public and stable, with acceptable error and return types?
- **Dependency direction:** is the dependency declared directly, or only transitively?
- **Lifecycle, coupling cost, and project rules** (README, architecture docs, manifests).
- Every row of **Appendix: Disqualifiers**.

## Decide
| Label | When |
|---|---|
| `REUSE` | An existing implementation meets the need as-is. Call it directly, with no wrapper. |
| `COMPOSE` | Existing pieces combined meet the need. |
| `EXTEND` | The right home exists but needs a small addition there. |
| `REPLACE` | An existing implementation should give way to a better existing capability. |
| `CREATE` | Nothing fits within the searched scope, or every candidate is disqualified. Say where the new code goes. |
| `UNRESOLVED` | The evidence is insufficient. Name the question that would settle it. |

Every decision needs a search outcome (see **Appendix: Evidence**): `FOUND`, `NOT_FOUND_IN_SCOPE` or `UNKNOWN`.

## Never
- Add a public API before searching.
- Re-implement an existing capability under another name, or copy a dependency's algorithm.
- Wrap an existing API in a forwarding-only wrapper.
- Reuse on name or signature similarity when the semantics differ.
- Claim something "doesn't exist" beyond the scope you searched.
- Extract a shared abstraction to remove a few lines between independent units. A small local copy is often right.

## Output
**When asked directly:**
```
Need: …
Searched: …   Outcome: FOUND | NOT_FOUND_IN_SCOPE | UNKNOWN
Candidates:
- path:line symbol — fits | disqualified: reason
Recommendation: 1–3 sentences
Unverified: …
Next: <e.g. implement at path:line, then /judicious critique --changed>
Decision: <LABEL>
```
- Every candidate and the recommended location get a `path:line` (see **Appendix: Report**).

**Inside an implementation task:**
- Don't stop to write a report. Act on the decision:
  - `REUSE` or `COMPOSE`: call the existing code directly. If the caller now uses a dependency it only had transitively, declare it.
  - `EXTEND`: make the minimal addition in place.
  - `CREATE`: write it where you said.
  - `UNRESOLVED`: ask the user.
- In the final summary, state the decision and what was reused (`path:line`) or why new code was needed.

## Uncertainty
- If two candidates are equally plausible and a wrong choice is costly, use `UNRESOLVED` and list both.
- If the need is ambiguous, ask one question first.
- If your tools are limited, report `UNKNOWN` rather than a confident `CREATE`.

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
