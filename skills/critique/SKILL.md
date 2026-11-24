---
name: critique
description: Structural engineering review of existing code or a proposed design before implementation. Finds duplicated responsibilities and parallel APIs, layer bypasses and wrong dependency direction, pass-through wrappers and speculative abstractions, shadow state, lossy boundaries, swallowed errors, and docs that promise checks which don't exist. Use when asked to review, critique or assess the design or architecture of code. Read-only; reports evidence-backed findings and never edits.
argument-hint: "[path, area or proposal] [--proposal] [--changed] [--focus <topic>]"
license: MIT
---


# critique

**Question:** What is structurally wrong with this code or proposed design, and why?

**Mode:** read-only. Never edit, create or delete files.

## Input
- **Target:** a path, a package or crate, or a named area.
- **`--changed`:** the git diff, plus the code it calls and the code that calls it.
- **`--focus <topic>`:** look at that topic first. It sets priority; it does not filter out other findings.
- **No target:** the current change. If there is none, ask what to review.

Map, review and verify the scope using the available capabilities. Independent reviewers can help with broad scopes, but delegation is optional.

## Proposal mode
- Use this read-only mode with `--proposal`, a request to review or draft a plan, or a target document or referenced conversation that sets out proposed changes. Identify plans from the intended behavior, design decisions or implementation steps in the targeted text, even without `--proposal` or a proposal label. An explicit implementation request uses the normal workflow unless `--proposal` is set.
- Use the supplied plan, or use the target code to draft corrections for confirmed findings. A document that only describes current behavior does not trigger proposal mode on its own. If the user asks to review a plan and it is missing, ask for it.
- Trace the proposed ownership, API and dependency changes against the affected code and project rules. Anchor each finding in the proposal at `path:line`, or use the section, step or quoted phrase for inline text. Cite existing definitions, callers and rules as separate code evidence.
- Apply the same lenses and disqualifiers. Confirm a design defect against the plan and any relevant existing contracts. Label predicted consequences and unverified assumptions, and distinguish them from defects already present in code.
- Use **Locations** for the affected code or proposed insertion points and **Direction** for the specific revision and how to validate it. Fill in missing or stale references by reading the named symbols, surrounding code, callers and relevant tests or project rules. Cite verified `path:line` references, with the symbol where helpful. Give new files a proposed path or owning module. Mark unresolved locations or assumptions and say what would confirm them.
- When a plan needs changes, return a **Revised proposal** with ready-to-use text for the affected steps, preserving the plan's intent and structure. Each changed step names the proposed action, its Locations and a concrete verification check. A location or design choice still in doubt belongs with the open questions, with the check or decision that would resolve it. A plan that already meets the requirements needs no rewrite.

## 1. Map (you)
- Read the project's own rules first: README, architecture or ADR docs, project instruction files, and the manifests (they define dependency edges).
- List the units, their public surfaces and their dependencies.
- Trace the main data and control paths far enough to know who owns each piece of state and each invariant.

## 2. Organize the review
- Split the scope into units of about 15 files or fewer each (a package, module or crate). A small scope is one unit.
- Review each unit and check duplication across units and against dependencies, including missed lowering. When delegation is available and appropriate, assign independent reviewers to units and a cross-cutting review. Respect the environment's concurrency limits.
- Each delegated review includes:
  - its paths, plus the paths of the dependency sources it may need;
  - in proposal mode, the relevant plan sections and the distinction between proposed behavior and existing code;
  - the project rules you found;
  - the lens table and the rules from step 4;
  - the finding fields from Output, with exact `path:line` Locations;
  - the instruction "read-only; return findings, not fixes".
- Without delegation, perform the same review directly. State actual coverage limits under Coverage; the absence of a delegation tool is not itself a finding or a reason to stop.

## 3. Collect candidates (generously, don't filter yet)
| Lens | Look for |
|---|---|
| Duplication | Two implementations, or parallel APIs, for one job. This includes re-implementing what a declared dependency already provides. |
| API consistency | Overlapping entry points whose naming, errors or return shapes disagree. |
| Boundaries | Layer bypasses, reaching into internals, dependency cycles, broken documented rules. |
| Abstraction | Pass-through wrappers, registries or interfaces with a single implementation, unused knobs. |
| State | The same data owned in two places. Show how the copies diverge. |
| Boundary fidelity | Data lost across serialization, FFI, an API or a cache: lossy types, dropped fields, a sync that adds but never removes. |
| Error contracts | Failures swallowed into empty or default results; sibling entry points reporting the same failure differently. |
| Sources of truth | The same source kept in several copies (templates, committed generated files); docs promising tests, CI checks or invariants that don't exist. |
| Evolution | Shims nobody owns, half-finished migrations, dead code. |
| Placement | Code in a unit that doesn't own that responsibility. Domain-free logic that belongs in a lower layer or core dependency (lowering), or policy pushed down too far. |
- **Appendix: Anti-patterns** lists the symptoms and exceptions for each pattern.

## 4. Verify (you)
- Re-check each returned finding in the code yourself. Drop any you cannot confirm.
- Confirm current-code findings in the bodies and callers, to the standard in **Appendix: Evidence**. For proposed behavior, verify the claim against the plan and the affected code you can inspect.
- Check its exceptions and **Appendix: Disqualifiers**. Use them only to remove false positives:
  - If the code proves an exception holds, drop the candidate and list it under "Not problems".
  - If an exception is plausible but unverified, keep the finding, lower its confidence, and name the exception.
- Similar-looking code with different contracts or lifecycles is not duplication.

## 5. Completeness sweep (you)
- Re-scan everything you read and ask: what would the owner want to know?
- Add anything that can make the system silently wrong, or that forces coordinated edits: data lost on a round trip, state never cleaned up, errors turned into empty results, safety claims with no check behind them.
- Missing a real problem costs more than reporting one extra low-severity finding.

## 6. Synthesize (you)
- Merge findings that share a root cause, but give every distinct consequence its own bullet.
- Rank by impact: how far a change has to ripple, and how silently things can go wrong. File count does not decide rank.
- Do not cap structural or correctness findings. A low-severity one takes 2–3 lines.
- "Minor" is for pure style only (naming, typos, comment wording), one line each.
- Finding nothing is a valid result. If so, say what makes the code sound.

## Output
```
Scope: …   Rules found: … | none

## Findings
### 1. <root cause>  [high | medium | low] · confidence: high | medium | low
- Problem:
- Why it matters: <concrete failure scenario>
- Proposal: <decision and proposal location, when applicable>
- Evidence: <path:line, call sites, manifest edges>
- Locations: <existing path:line references and proposed paths or owners for new code>
- Could be justified if: <exception, and whether you checked it>
- Direction:
- Fix with: `consolidate` | `distill` | `harden` | `placement` | bug fix
- Unverified:

## Minor
## Not problems
## Coverage
<read / skipped / not visible>

## Revised proposal
<replacement text for affected steps, if the supplied plan needs changes>

## Next
<1–3 commands, highest impact first, each with its exact target>

Findings: <n> (high <h>)
```
- Choosing `Fix with`:
  - `consolidate`: merge parallel implementations or APIs.
  - `distill`: remove wrappers, dead code or speculative layers.
  - `harden`: contracts, error handling, invariants, lossy boundaries.
  - `placement`: move or lower code into another unit or dependency.
  - **bug fix:** a plain defect.
- Follow **Appendix: Report**: every finding has Locations, and the report ends with Next.
- End with the `Findings:` line. Don't apply fixes yourself.

## Limits
- If the scope exceeds the available review capacity, start with the highest-risk area, state the limit, and offer to continue.
- If a finding depends on intent you can't see, lower its confidence and name what would confirm it.

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
