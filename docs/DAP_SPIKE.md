# Step 3 — the DAP spike

A Debug Adapter Protocol session expressed in the unchanged HostProto
schemas. On paper and in `examples/dap-sketch/`; no runtime. The question is
kill gate 1: does a debugger need a different core envelope than a browser?

## The mapping

| DAP | HostProto | Note |
| --- | --- | --- |
| adapter process | `HostHandle` | expires when the debuggee exits: `handle_expired` |
| launch / attach configuration | `ContextHandle` + writer fence | one client drives one session; a second is `writer_conflict` |
| thread | `SurfaceHandle` | lifecycle `open` → `terminated` on the `thread exited` event; `allThreadsStopped` stamps every surface |
| `stopped` / `continued` transitions | **revision** | increments on every running↔stopped transition of that thread |
| adapter message `seq` | raw provenance only | the **cursor** is host-assigned over normalized events, exactly as on the browser lane (Playwright has no event ordinals either) |
| `stackTrace` frames, `variablesReference` children | `TargetRef` with `role: frame` / `scope` / `variable` | DAP already scopes these to "while stopped"; HostProto makes that a revision and rejects use afterwards as `target_invalidated` **before** sending anything |
| `invalidated` event (areas: stacks, threads, variables) | revision bump | the adapter told us what browser lanes infer from a document commit |
| `stopped` state, `threadId` | `Precondition` assertable fields | `stopped`, `thread_id`, `revision` |
| `setBreakpoints`, `next`, `stepIn`, `stepOut`, `continue`, `pause`, `evaluate`, `setVariable` | `Intent.kind` in the `dap/v1` family | closed set in the capability profile |
| `Breakpoint.verified` | `Receipt.verified` | the adapter's own bound/unbound answer is the verification, per breakpoint; a partially bound set is `verified: true` with a `divergence` deviation naming the unbound one |
| step pre-empted by a breakpoint | `Receipt.effects` ≠ `Intent.declared_effects` + deviation | outcome stays `completed`; what was asked and what happened are both on record |
| `continue` timed out after acceptance | `Receipt.outcome: unknown`, `executed: false` | the program may be running; reconcile from the next observation |
| `runInTerminal` reverse request | `Intent.decision_token` (`host_request.resolve`) | the same host-owned-request shape as a script dialog |
| `output` after `terminated` | `Deviation{kind: suppression}` | rule id and raw ref required |
| raw DAP message log | `EvidenceRef` (`application/x-ndjson`) | there is no screenshot; the message log is the raw surface |
| `initialize` response capabilities (`supportsStepBack`, `supportsRestartFrame`, …) | `CapabilityProfile` availability | `unsupported` / `partial` come straight from the adapter; `runtime` is earned by execution as on the browser |
| debuggee exit | `Recovery{outcome: unrecoverable, cause: host_terminated}` | with the message log as evidence |
| stale observation after `continued` | `Recovery{outcome: reobserve_required, cause: stale_observation}` | |

## What strained, and what was decided

1. **State-dependent projections.** `frames` cannot be observed while a
   thread is running. Nothing in the browser lane is like that. Rather than
   add a "returned projections" field, the observation keeps `projections`
   as requested, counts the projection in `bounded.omitted`, and records a
   `divergence` deviation saying why. `lossy` stays `false` because nothing
   was lost. **Clarification to `observation`, not a change:** `omitted`
   counts what was not returned for any reason; a non-loss omission must be
   explained by a deviation. See `observation-running.json`.
2. **Per-thread vs whole-process revision.** `allThreadsStopped: true` means
   one event moves several surfaces. Decided: revision is per surface; the
   adapter stamps each affected surface. No cross-surface revision exists,
   and none is needed for gate 7.
3. **Breakpoint verification is per item.** A receipt is per operation.
   Decided: `verified` reflects that the operation's effect was observed at
   all; per-breakpoint `verified` lives in `effects`, and an unbound
   breakpoint is a named deviation. No sub-receipt type.
4. **The cursor is not DAP `seq`.** DAP `seq` is per sender across all
   messages. Using it as the surface cursor would have broken gate 7 for
   any multi-thread session. Decided: host-assigned per-surface cursor over
   normalized events; DAP `seq` is retained in raw provenance. This is the
   rule the browser lane already followed, now stated generally:
   **the cursor is always host-assigned; a host's own ordinals are raw.**

## Kill-gate verdict

| Gate | Verdict | Evidence |
| --- | --- | --- |
| 1 — browser and DAP need different core envelopes | **did not fire** | every DAP example validates against the unchanged schema its browser counterpart uses; `tests` assert this for all eleven |
| 7 — revision cannot be expressed uniformly | **did not fire**, with the cursor rule above | per-surface revision on stop/continue; host-assigned cursor |
| 8 — verification stops being earnable | **did not fire** | `dap/v1` profile earns `runtime` per capability by execution; `Breakpoint.verified` even gives receipts a stronger oracle than the browser has |
| 2 — schema degenerates to free JSON | not fired | `data` is per-projection and profile-shaped as before; no new `type: object` escape |

Step 5 (a DAP runtime) is therefore admissible. It should target debugpy
first (Python, matches the conformance tooling) and prove the
`target_invalidated`-before-send rule with a real `variablesReference`
after `continue`.

## What a DAP adapter must still define outside the schemas

Its projection shapes (`state`, `frames`, `scopes`, `variables`, `output`,
`breakpoints`), its intent parameter shapes, and its normalization rules
with ids — the same three things the browser adapter defines. Those are
profile documents, not HostProto changes.
