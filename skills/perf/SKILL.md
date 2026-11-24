---
name: perf
description: Evidence-based performance review and optimization that benefits every case without system-specific tuning. Use when asked to find bottlenecks, reduce latency or memory use, or improve throughput and scaling. Reviews read-only by default; edits code only when optimization is requested, and verifies correctness and measured performance.
argument-hint: "[path, workload or proposal] [--proposal] [--changed] [--focus <topic>]"
license: MIT
---


# perf

**Question:** Which measured bottleneck can be removed with a general optimization that benefits every case?

**Mode:** read-only by default. Optimize only when requested; edits follow **Appendix: Verification**.

## Input
- **Target:** a path, workload, or finding from an earlier report. For a finding, start from its Locations (see **Appendix: Report**). A reported system identifies where to investigate; it never limits the optimization acceptance scope.
- **`--changed`:** review the diff and its affected execution paths.
- **`--focus <topic>`:** sets priority, not an exclusion.
- **No target:** use the workload described by the user or current change. If neither identifies a workload, ask which operation matters.
- Read project architecture, lifecycle rules, supported hardware and existing benchmarks. Use the host's tools; no dedicated agent or profiler is required.

## Proposal mode
Use this read-only mode with `--proposal`, a request to review or draft a plan, or when the target document or referenced conversation sets out proposed changes, even without `--proposal`. An explicit implementation request uses the normal workflow unless `--proposal` is set.

Use steps 1–3 to review any supplied plan against the measurements and affected code, citing its lines, sections or steps. Keep existing baseline measurements separate from expected gains. When a supplied plan needs changes, return a **Revised proposal** with replacement steps, verified Locations, the validation matrix and the experiments needed to resolve unverified claims. End the invocation before any candidate edit.

## Procedure
1. **Define the general improvement**, with `path:line`: which shared operation is wasteful, why removing that waste benefits every case, and which callers and supported configurations use it.
   - Never optimize for a particular molecule, material, named system, fixture, benchmark input, or known answer. Do not add case identities, hard-coded sizes or tuned thresholds to select a favorable path.
   - Every retained optimization must benefit all cases, not merely improve an average or one selected system. Do not accept a regression in any case in exchange for gains elsewhere; unchanged cases do not prove benefit.
   - A general algorithmic property may explain an optimization, but never use it to disguise a system-specific fast path. Keep the scientific method, accuracy, convergence criteria and supported input domain unchanged.
2. **Establish evidence.**
   - Define success: latency, throughput, peak memory, allocation traffic or scaling, with an explicit measurement boundary and representative input.
   - Reuse the project's benchmark and correctness checks. Record hardware, build flags, dependency versions, input size, thread/rank counts and relevant algorithm or convergence settings.
   - Distinguish setup from steady state and cold from warm runs. Include end-to-end costs as well as kernel timings; synchronize asynchronous work at the measurement boundary.
   - Profile before choosing an optimization. Repeat comparable runs enough to describe variation; report the measurement method and raw result location. Do not infer a bottleneck or speedup from source inspection alone.
   - If execution is unavailable, report static candidates and the experiment needed to confirm each. Do not invent timings or present estimates as measured results.
   - Define a validation matrix before editing from all existing cases and supported workload classes: sizes, shapes, methods, backends, hardware and thread/rank widths. Include edge cases and cold/steady execution where applicable; never choose only the cases that motivated the change.
   - Explain why the mechanism benefits the entire supported domain. Measurements cover the defined matrix; they cannot by themselves prove a universal claim. If any case or configuration is unmeasured, report coverage as incomplete and do not claim the optimization is accepted for all cases.
3. **Review the critical path.** Start with algorithmic work and data flow, then inspect the mechanisms relevant to the measured bottleneck:
   - Repeated computation, unnecessary materialization/copies, allocations inside hot loops, and setup repeated during execution. Hoist work only when input invalidation and ownership remain correct.
   - Memory locality, working-set size, strided access and bandwidth. A layout change needs evidence from real consumers, not a blanket preference for SoA or AoS.
   - CPU parallelism: serial fractions, load imbalance, synchronization, reductions, false sharing, NUMA placement and nested library threading. Missing OpenMP or SIMD is not itself a defect.
   - Vectorization: dependencies, aliasing, branch patterns and compiler reports. Prefer suitable existing primitives; use project-supported portable mechanisms when manual vectorization is justified.
   - GPU/accelerator paths: host/device transfers, allocation lifetimes, implicit synchronization, launch overhead, access patterns and atomic contention. Measure residency and overlap rather than claiming them from code shape.
   - Distributed paths: communication volume, collectives, overlap and scaling. Compare fixed-workload speedup separately from increasing-workload throughput.
   - Before recommending a new kernel or helper, search existing implementations and dependencies. Use `reuse` with `--proposal` when the choice is non-trivial.
4. **Optimize only when requested, outside proposal mode.** Choose a confirmed bottleneck. Locate the intended change and its callers, then follow **Appendix: Verification** before making a focused change in the owning layer. Preserve supported hardware, error behavior, resource lifetimes and numerical contracts. Do not impose architecture-specific flags or dependency versions across projects.
5. **Verify every case in the matrix.** Re-run correctness checks and compare identical benchmark settings to baseline, reporting each case separately with units and variation. Numerical reductions require justified tolerances; parallel changes need serial and parallel checks. Exercise affected downstream quantities, such as forces after an energy-path change.
6. **Accept only a general benefit.** Every case must pass correctness and demonstrate improvement beyond measurement noise in the stated target metric, with no regression in the other required metrics. A faster inner kernel with a slower complete call fails. If any case regresses, is unchanged, or lacks sufficient evidence, reject or revise the candidate; restore only your candidate edits and preserve unrelated work. In review mode, report the failed or incomplete acceptance without editing.

## Output
In proposal mode, report current findings and measurements, the proposed change and planned experiments, then end with **Next**. Record acceptance only after a candidate has been measured.

```
Scope: <paths, shared operation, supported domain, measurement boundary>
Findings: path:line — mechanism; measured | static candidate; confidence
General benefit: <why the mechanism benefits every case; no system-specific path>
Coverage: <complete case/configuration matrix; skipped or unverified cases>
Per case: <case, settings, baseline → after, units, variation, correctness>
Changed: path:line — what changed (optimization mode only)
Acceptance: accepted | rejected | incomplete — <reason; regressions or unchanged cases>
Verification: `<cmd>` → result (baseline → after); not verified: …
Next: …
```
- Next is the highest-value measurement or concrete fix; use `/judicious critique --changed` after structural changes. If nothing remains, say `Next: none` and why.

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
- Cite existing locations at `path:line` (or a line range). Include the definition, the call sites to change and relevant manifests or docs. Give new files a proposed path or owner.
- **Locations** is the to-do list for whoever acts on the finding. List every place that must change, not just one example.
- Never report an issue without a location. If you cannot locate it, say so and lower the confidence.
- Start from the Locations in an earlier report or proposal. Re-read the source and resolve missing or stale references by following symbols and callers. State what remains unverified.

### End with the next step
- The last section is **Next**: one to three recommended commands, in order, each with its exact target and a one-line reason.
  - Example: `/judicious harden src/molpy/engine/_openmm.py:440-444`, because NVE silently runs a thermostat.
- Recommend only commands that exist. If the right move is a plain bug fix or a native plan, say that instead.
- If nothing is left to do, write `Next: none` and give the reason.
