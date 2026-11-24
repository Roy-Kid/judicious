---
name: audit
description: Read-only audit of a codebase's architecture and technical debt. Maps the project, reviews the highest-risk areas through critique, merges shared root causes, and classifies what remains. Use when asked to audit a repo, survey technical debt, or review architecture across modules. Read-only; reports evidence-backed findings and never edits.
argument-hint: "[path or proposal] [--proposal] [--changed] [--focus <topic>]"
license: MIT
---


# audit

**Question:** What architecture problems and technical debt does this codebase have?

**Mode:** read-only. Never edit, create or delete files.

## Loading skills
When this workflow uses another skill, load its current instructions and follow them with the supplied target and arguments. Use the environment's skill-loading mechanism when available; otherwise read the matching installed `SKILL.md` using file or resource access. In a source checkout, skills live at `skills/<name>/SKILL.md`. Resolve names within the Judicious package to avoid unrelated skills with the same name. No particular tool name or invocation syntax is required. If the required instructions cannot be accessed, report the missing skill and stop that dependent step; do not reconstruct it from memory.

## Input
- **Target:** a path, a package or crate, or the whole project.
- **`--changed`:** the git diff, plus the code it calls and the code that calls it.
- **`--focus <topic>`:** look at that topic first. It sets priority; it does not filter.
- **No target:** the whole project.

You coordinate. The area review is `critique`. This playbook maps, merges and classifies.

## Proposal mode
- Use this read-only mode with `--proposal`, a request to review or draft a plan, or when the target document or referenced conversation sets out proposed changes, even without `--proposal`. An explicit implementation request uses the normal workflow unless `--proposal` is set.
- Review the supplied plan against the affected areas, or use the normal scope and draft a prioritized set of changes from confirmed debt.
- Map proposed dependency and ownership changes alongside existing ones so cross-area consequences are covered.
- Keep proposal risks distinct from current debt when merging findings. Preserve each proposal anchor (`path:line`, section or step) alongside evidence from the current code. Use **Direction** for the ranked correction and how to validate it. If a plan needs changes, merge the area reviews into one **Revised proposal** with replacement text for the affected steps, verified Locations, concrete checks and open questions.

## 1. Map
- Read the project's own rules first: README, architecture or ADR docs, project instruction files, and the manifests.
- List the units, their public surfaces and their dependency edges.
- Mark the highest-risk areas: boundaries, duplicated domains, public APIs, and generated, FFI or serialization code.

## 2. Review
- Review at most 4 areas in this pass. Name every skipped area under Coverage, and offer to continue.
- For each area, load and follow `critique` with that path as its target. If proposal mode is active, pass `--proposal` and the relevant plan sections as well. Use the resulting report.

## 3. Merge and classify
- Merge findings that share a root cause across areas. Keep each distinct consequence as its own bullet.
- Give each merged finding one primary category:
  - **Duplication** — parallel implementations or APIs.
  - **Ownership** — a responsibility with no single owner.
  - **Architecture** — wrong dependency direction, a layer bypass, or a cycle.
  - **Abstraction** — a wrapper or generalization with no second consumer.
  - **Placement** — code living outside the unit that owns it, including a lowering candidate.
  - **Evolution** — a dead implementation, an unfinished migration, or a compatibility shim.
  - **Contracts** — inconsistent APIs, swallowed errors, or a lossy boundary.
- Re-read the code and any proposal passages behind each merged finding (**Appendix: Evidence**). Check for exceptions in **Appendix: Anti-patterns** and **Appendix: Disqualifiers**. When an exception is plausible but unchecked, keep the finding and lower its confidence.
- Rank by how far a change ripples and how silently it fails.
- A partial search says nothing about the code you did not read. Say so in Coverage.

## Output
In proposal mode, use the finding fields below for a **Proposal findings** section. Keep **Debt** and its count for findings about current code. Put any **Revised proposal** before **Next**.

```
Scope: …   Rules found: … | none

## Debt
### 1. <root cause>  [<Category>]  [high | medium | low] · confidence: high | medium | low
- Problem:
- Why it matters:
- Proposal: <decision and proposal location, when applicable>
- Evidence: path:line
- Locations: <existing path:line references and proposed paths or owners for new code>
- Could be justified if:
- Direction:
- Fix with: `consolidate` | `distill` | `harden` | `placement` | bug fix
- Unverified:

## Coverage
<areas read / areas skipped / not visible>

## Next
<1–3 commands, highest impact first, each with its exact target>

Debt: <n> (high <h>)
```
- Follow **Appendix: Report**.
- End with the `Debt:` line.

## Limits
- When a finding depends on intent you cannot see, lower its confidence and name what would confirm it.

## Appendix: Anti-patterns

These are signals to investigate, not rules to apply mechanically.

| Pattern | Symptom | Legitimate when | Usual remedy |
|---|---|---|---|
| Parallel Implementation | A second unit does the same job under another name. | Contracts really differ; a time-boxed migration; independent deployables. | Choose one canonical unit, migrate callers, delete the other. |
| API Proliferation | Public entry points with overlapping meanings (`get_`/`fetch_`/`load_`). | Convenience layers that delegate to one core; versioned APIs. | Keep one entry point; deprecate the rest on a schedule. |
| Shallow Wrapper | Forwards its arguments and adds no validation, policy, translation or test seam. | A real boundary such as an anti-corruption layer; a seam that tests use; a facade over an unstable API. | Call the underlying API directly, or give the wrapper a real job. |
| Shadow State | The same data is held in two places and nothing keeps them in sync. | A derived cache invalidated by a single owner; a deliberate snapshot. | One owner; everything else derived or invalidated from it. |
| Speculative Generality | A registry, plugin system, interface or knob with exactly one implementation. | A documented extension point that users rely on; a second implementation concretely planned. | Inline it until the second case arrives. |
| Premature Extraction | A shared module for one consumer, or for code that only looks alike. | At least two real consumers with the same semantics. | Keep it local; extract at the third consumer. |
| Premature Lowering | Policy pushed into a lower layer, or across FFI or WASM, without proven need. | The logic is domain-free and has proven consumers on several layers. | Lower only the domain-free core. |
| Missed Lowering | Domain-free logic, such as geometry, topology or I/O formats, implemented in an upper package even though the core library it builds on owns that domain or already has it. | The logic depends on upper-layer policy, or no other consumer exists. | Use the core's version, or move the logic down and expose it through bindings. |
| Architecture Bypass | Reaching past a layer: internals, forbidden dependency edges. | A documented escape hatch that re-applies the invariants. | Route the call through the owning layer; add a fast path there if needed. |
| Compatibility Accumulation | Deprecated aliases or shims with no owner or removal date. | A published API within a stated deprecation policy. | Check consumers, including external ones, then remove or set a date. |
| Dead Implementation | The old path is still present after its replacement shipped. | A rollback path kept for a stated period. | Delete it once dynamic references are ruled out. |

## Appendix: Disqualifiers

Any one of these rules out reuse, merging or extraction. Record which ones you checked.

- **Semantic mismatch:** inputs, outputs, edge cases or invariants differ from the need. Example: a lossy slugifier named `normalize`.
- **Contract mismatch:** the error model, side effects or stability are unacceptable. Example: a private helper with no stability promise.
- **Invalid dependency direction:** reuse would make a lower or independent unit depend on a higher one, or create a cycle.
- **Lifecycle divergence:** the two sides change for different reasons or owners. Example: a frozen wire format versus a display string.
- **Boundary cost exceeds benefit:** crossing a process, language, ABI or deployment boundary costs more than the duplication it saves.
- **Unproven sharing:** only one real consumer exists today.
- **Policy leakage:** the candidate carries domain policy that the new context must not inherit.
- **Project constraint:** a README, architecture doc, project instruction file or manifest rule forbids it.

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
- Cite existing locations at `path:line` (or a line range). Include the definition, the call sites to change and relevant manifests or docs. Give new files a proposed path or owner.
- **Locations** is the to-do list for whoever acts on the finding. List every place that must change, not just one example.
- Never report an issue without a location. If you cannot locate it, say so and lower the confidence.
- Start from the Locations in an earlier report or proposal. Re-read the source and resolve missing or stale references by following symbols and callers. State what remains unverified.

### End with the next step
- The last section is **Next**: one to three recommended commands, in order, each with its exact target and a one-line reason.
  - Example: `/judicious harden src/molpy/engine/_openmm.py:440-444`, because NVE silently runs a thermostat.
- Recommend only commands that exist. If the right move is a plain bug fix or a native plan, say that instead.
- If nothing is left to do, write `Next: none` and give the reason.
