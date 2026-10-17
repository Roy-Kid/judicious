---
name: distill
description: Removes code that has no reason to exist while preserving behavior — pass-through wrappers, copy-pasted helpers, speculative extension points, unused options or parameters, unreachable branches, dead implementations and expired compatibility shims. Use when a critique finding or the user points at unnecessary complexity. Edits code; verifies with the project's tests.
argument-hint: "[path, symbol or critique finding]"
license: MIT
---


# distill

**Question:** What here can be deleted or simplified without changing behavior?

**Mode:** modifying. It edits code under **Appendix: Verification**.

## Input
- **Target:** a path, a symbol, or a finding from an earlier report. When the target is a finding, start from its Locations (see **Appendix: Report**).

## Procedure
1. **List the candidates**, with `path:line`, and name the anti-pattern behind each one (**Appendix: Anti-patterns**).
2. **Prove each candidate is removable:**
   - Find every reference, including dynamic ones: string lookups, entry points, config, re-exports, docs and tests.
   - Check whether it is public API. If it is exported or documented, apply the approval gate.
   - Check the pattern's "legitimate when" column. If an exception holds, keep the code and say why.
3. **Simplify:**
   - Inline forwarding layers.
   - Delete dead code, unreachable branches and unused parameters.
   - Collapse copies into the one that already exists.
   - Never add a new abstraction to do this.
4. **Keep:**
   - correctness and necessary error handling;
   - observable behavior and public contracts;
   - compatibility that a named consumer needs.
5. **Verify** with the project's checks.

## Output
```
Removed/simplified: path:line — what, and why it was safe (references checked)
Kept: path:line — exception that justified it
Verification: `<cmd>` → result (baseline → after); not verified: …
Net lines: −N
Next: …
```
- Next is usually `/judicious critique --changed`. If removing something exposed duplication, recommend `/judicious consolidate`.

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

## Appendix: Verification

These rules apply to every command that edits code.

### Before editing
- Find the project's own checks: test, build, lint and type-check commands from the README, CONTRIBUTING, CI workflows, the Makefile or the package manifest.
- Run the relevant tests first, and record the baseline result. A failure that already exists is not yours to explain away later.
- Ask for approval first, presenting the plan with its Locations, when the change would:
  - change or remove a public API or exported symbol;
  - touch more than about 5 files, or cross package or repository boundaries;
  - change behavior that consumers outside the repo may rely on;
  - go ahead without any test you can run.
- Otherwise, proceed.

### While editing
- Make small batches, each one verifiable on its own.
- Preserve correctness, error handling, observable behavior and public contracts, unless the finding is exactly about changing them.
- Use the host's own editing and planning tools. Add no new infrastructure.

### After editing
- Re-run the same checks and compare them with the baseline.
- For every fixed defect, add or update one regression test that fails without the fix.
- Report every command you ran and its result. If you could not run something, say "not verified" and give the reason. Never claim an unverified change works.

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
