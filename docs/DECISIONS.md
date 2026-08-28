# Decisions

## ADR-0001: HostProto is semantics, not a wire protocol

**Context.** browser-workbench proved a typed observation/action protocol on a
real engine. The next step could be a third protocol beside MCP and A2A, or a
semantic layer both carry.

**Decision.** Semantics. Canonical JSON Schemas used directly as MCP tool
schemas and as an A2A profile extension. No discovery, transport, scheduler,
or task store in this repository — their appearance is a kill-gate event.

**Consequence.** The browser becomes one conformance backend. The
intellectual property is the nine semantics in `THESIS.md`, nothing else.

## ADR-0002: Playwright becomes the reference adapter; WebKitGTK becomes the challenger

**Context.** browser-workbench held that the Playwright oracle is never core.
That rule protected a native-engine claim. The claim here is different.

**Decision.** The headless MCP reference adapter is Playwright. The native
WebKitGTK lane keeps its conformance evidence and now cross-checks Playwright.

**Consequence.** The slice-6 differential machinery inverts its baseline. The
"oracle is not proof" caveat still holds in both directions.

## ADR-0003: the DAP spike runs before the A2A worker

**Context.** The A2A worker is projection; it cannot fail in a way that tests
the thesis. A debug session can: frames and threads invalidate on resume,
observations are revisioned by stop/continue, and operations are
state-dependent.

**Decision.** Step 3 (DAP on paper and in `examples/`) precedes step 4.

**Consequence.** Kill gates 1, 7, and 8 get their first real test within the
first two weeks rather than after the worker exists.

## ADR-0004: unverified spec claims gate deletion

**Context.** The plan cites MCP 2026-07-28 and A2A v1.0 features that have
not been checked against the specs in this repository.

**Decision.** `PLAN.md` step 0 lists each assumed feature with status
`unverified`. No HostProto abstraction is deleted on the strength of a
feature until its row is marked verified with a spec section and date.

**Consequence.** The alignment pass may keep pieces the plan expected to
delete. That is the correct outcome if the spec is thinner than assumed.

## ADR-0005: step 0 outcome — nothing is deleted, three things are constrained

**Context.** All eight assumed MCP 2026-07-28 and A2A 1.0.0 features were
verified against the specifications on 2026-08-28 (`PLAN.md` step 0 table
carries the citations).

**Decision.**

1. HostProto keeps its `handles` schema. MCP removed sessions but defines no
   handle concept; its stateful-tools guidance is non-normative and treats a
   handle as an ordinary string. Opacity, expiry, and writer fencing are
   HostProto's to specify.
2. Surface-change notification is expressed as an MCP **resource
   subscription** on a surface resource, because `subscriptions/listen` admits
   no other event type. No HostProto event channel is added.
3. Task *listing* is not projected through MCP (`tasks/list` was removed).
   `ListTasks` is A2A's, backed by the domain runtime. This sharpens the
   responsibility split rather than weakening it.
4. Schemas are used verbatim in MCP tool definitions, bundled to satisfy MCP's
   `$ref` resolution rules. The canonical files keep cross-file `$ref`.

**Consequence.** The alignment pass (step 1) deletes no HostProto
abstraction. The plan's assumption that duplicated discovery, task, transport,
and content abstractions exist to be deleted was wrong in one direction: there
were none to delete because browser-workbench never built them. What remains
is renaming and de-browsering.

**Guard.** Verification is dated. A later spec revision re-opens step 0.

## ADR-0006: the 0.1.0 alignment added four semantics the browser-workbench lineage had lost

**Context.** browser-workbench inherited hostproto 0.1.0's corpus but not all
of its temporal rules. Mapping 0.1.0 directly exposed four things the
schemas here did not say: an operation's terminal outcome (including
`superseded` and `unknown`), typed suppression records, surface lifecycle,
and capability degradation as a recovery cause.

**Decision.** All four are added: `Receipt.outcome` (required), a `deviation`
schema whose `suppression` kind requires `rule_id` and `raw_ref`,
`SurfaceHandle.lifecycle`, and `capability_degraded` as both an error code
and a recovery cause with `immutable_per_run` on the profile.

**Consequence.** Eleven schemas. `Receipt.outcome = unknown` with
`executed = false` is now the legal shape for "the deadline elapsed after the
host was invoked" — the case both prior projects handled in prose only.

**Guard.** The deviation schema is the one place a "we dropped it" can be
recorded. A `deviations` array is required nowhere, so the guard is
conformance tooling counting suppressions per run, as 0.1.0 required.

## ADR-0007: step 2 confirmed the mapping on the wire, with two corrections

**Context.** The reference adapter (hostproto-mcp-playwright) put the bundles
on a real MCP 2026-07-28 connection using SDK v2.0.0.

**Decision.** Two rows of the step-0 table are amended from wire evidence:
`resources/subscribe` is absent on the era and resource subscriptions are URI
arrays in the `subscriptions/listen` filter; `server/discover` returns
`supportedVersions` and identity rides `_meta`. No schema changed. The
adapter's own `docs/DECISIONS.md` ADR-0003 holds the full list.

**Consequence.** Handles, revisioned observation, target invalidation,
preconditions, receipts with `outcome`, evidence refs, the earned capability
profile, and `error.host_invoked` all crossed the wire unchanged. Kill gates
2 and 6 did not fire: no payload degenerated to free-form JSON, and the
adapter needed no escape hatch.

**Guard.** Step 3 (DAP spike) is next and is where gate 1 gets tested.

## ADR-0008: the DAP spike did not fire gate 1

**Context.** Step 3 expressed a Debug Adapter Protocol session — threads,
frames, variables, breakpoints, stepping, `runInTerminal`, exit — in the
eleven schemas as they stood after step 1 (`docs/DAP_SPIKE.md`).

**Decision.** No envelope change. One clarification to `observation`:
`bounded.omitted` counts what was not returned for any reason, and a non-loss
omission (a projection the host cannot serve in its current state, such as
frames while running) keeps `lossy: false` and must be explained by a
deviation. One rule generalized from both lanes: **the cursor is
host-assigned over normalized events; a host's own ordinals (DAP `seq`,
engine callback ordinals) are raw provenance.** Revision is per surface;
`allThreadsStopped` stamps each affected surface.

**Consequence.** Kill gates 1, 7 and 8 did not fire; gate 2 did not fire.
Step 5, a DAP runtime, is admissible, targeting debugpy first. The DAP
`Breakpoint.verified` flag gives receipts a stronger verification oracle
than the browser lane has, which is worth noting as evidence *for* the
receipt design rather than merely compatibility with it.

**Guard.** A spike proves the schemas can describe a debugger. Only the
runtime proves an adapter can honour them — in particular
`target_invalidated` before send for a real `variablesReference` after
`continue`.

## ADR-0009: step 4 — the worker is projection, and projection held

**Context.** The A2A host-worker (hostproto-a2a-worker) put one delegated
skill on A2A 1.0 with the MCP adapter inside and a minimal domain runtime
as the authoritative run owner.

**Decision.** No schema change. Three things confirmed on the wire:

1. The profile extension is a contract, not documentation: A2A refuses a
   caller that does not declare a `required` extension. The card's params
   carry this repository's commit and every bundle digest, so a client can
   verify each HostProto object it receives.
2. The three task notions stayed correlated, never merged. The run carries
   the task id and the HostProto handles; the task carries the run id in
   metadata; the adapter knows neither. No `Task` type appeared here.
3. A HostProto interruption at the primitive level (a `decision_token`
   held by the adapter) is an `INPUT_REQUIRED` at the assignment level with
   the same payload, as `RESPONSIBILITY_SPLIT.md` predicted.

**Consequence.** Kill gates 3, 4 and 5 did not fire: the run store is the
worker's, one skill covers many primitives, one task covers many MCP calls.
One adapter gap noted, not a semantic: the host-side `await` is all-of, and
"idle **or** dialog opened" is what a worker actually waits for.

**Guard.** The domain runtime is in-memory and single-process. Replacing it
with ActionQ must not change a single line of `executor.ts`'s projection;
if it does, the split was wrong.

## ADR-0010: step 5 — the second host class runs on the same envelope

**Context.** The DAP runtime (hostproto-dap-debugpy) put a real debugger
behind the eleven bundles, with the browser adapter's structure kept
file-for-file: a client that only frames messages, a host that owns the
semantics, a server that only projects.

**Decision.** No schema change. Gate 1 is now tested at runtime, not on
paper: handles, revisioned observation with a host-assigned cursor,
revision-scoped targets refused before send, preconditions, receipts with
`unknown`, evidence refs, recovery, and an earned capability profile all
crossed the wire for a debugger exactly as for a browser. Gate 8 held: the
`dap/v1` profile earns `runtime` per capability by execution, and
availability comes from the adapter's own `initialize` answer.

**Consequence.** Two host classes, one envelope, one worker profile. The
`creating` surface lifecycle — needed because debugpy asks the client to run
the debuggee before it reports initialized — is a state the schema already
had; no escape hatch (gate 6). One spike case is unreachable on debugpy
(`Breakpoint.verified: false` at set time); the receipt instead records the
adapter's relocation as a deviation, which is a stronger record than the
spike expected.

**Guard.** Step 6 (native WebKitGTK) stays optional. The next question is
not a third host class but a second debugger: if a non-debugpy adapter needs
a different envelope, gate 1 fires late.

## ADR-0011: gate 1 tested late — a second debugger, same envelope

**Context.** ADR-0010 named the next real test: a non-debugpy DAP adapter.
hostproto-dap-delve was built the same day as a copy of the debugpy adapter.

**Decision.** No schema change. The measured diff is transport (`connect`
beside `spawn`), launch (`go build` inside `launch`, cwd = module),
and one normalization (debuggee stdio arrives on the adapter's stdio, not
as DAP `output`; it is folded into the same event stream and the profile
says `provider: host, semantics: normalized` for `observe.output`). Two
adapter differences went the other way from debugpy without touching a
schema: Delve reports `verified: false` honestly, and `next` is not
pre-empted by a nested breakpoint — the receipt records agreement.

**Consequence.** Three host classes counting the browser, two debuggers,
one envelope. Three fixes found on Delve were folded back into debugpy,
which is the shape a shared `hostproto-dap-core` would take if a third
adapter appears; it is not extracted yet because two is not a pattern.

**Finding, retracted the same day.** A first version of this ADR claimed
Delve acknowledged a `setVariable` the debuggee never saw, and that `next`
was not pre-empted by a nested breakpoint. Both came from an off-by-one in
the Go fixture's line comments: the "breakpoint inside the call" sat on a
closing brace (Delve reported `verified: false` and the receipt carried
the deviation, unread), and the "stop before the call" was the line after
it. With correct lines Delve behaves exactly like debugpy on both the
development toolchain and release Go 1.25.1. What survives is the
mechanism that exposed the error — the program's own output kept as
evidence beside the receipt — and the read-back that now earns `verified`
on `set_variable` in both adapters. The retraction is recorded rather than
rewritten because the failure mode is the one HostProto exists to catch,
and it caught its own author.

**Guard.** Every receipt deviation in a test's *setup* is asserted, not
just those in the step under test.

## ADR-0012: hostproto-dap-core — the DAP semantics once, as a stated promise

**Context.** ADR-0011 declined to extract a shared core because "two is not
a pattern". The user asked to pre-generalize anyway, as a *promise*: state
what every DAP binding gets and what it must supply, and test that promise
without any engine.

**Decision.** [hostproto-dap-core](https://github.com/bayleafwalker/hostproto-dap-core)
holds the host, the MCP surface, the DAP client and the schema pin. A
debugger is an `EngineBinding`: how to start it, its `initialize` and
`launch` arguments, its identity, what it cannot do, and whether handles
must return before the launch completes. The seam is exactly the measured
diff between the two adapters (ADR-0011): debugpy is 27 lines, Delve 48.
The promise is written down (`docs/PROMISE.md`) and tested against a
scripted DAP engine over loopback — nine cases covering revision, refusal
before send, pre-emption, `unknown`, omitted-not-lost, the no-`continued`
grace path, read-back, host requests, and recovery — so a semantic change
needs a fake-engine case before a real engine confirms it.

**Consequence.** Bindings pin the core by git commit; the core pins the
bundles by digest. A binding may not compute a revision, mint a target,
decide `verified`, or add a projection or intent kind — that is either a
core change with a promise test or a HostProto change with an ADR here.
No schema changed.

**Guard.** The fake engine is the only place a DAP quirk may be simulated;
a quirk that cannot be expressed there is a real-engine fact and stays in
that binding's `docs/DECISIONS.md`.

## ADR-0013: the promotion target is host-interaction evidence, not the EvidenceSet

**Context.** After step 5 the track has proven one envelope across two host
classes but has no consumer that is not itself. The candidate consumer is
Vuoro's `EvidenceSet`. A first scope proposed HostProto as that set's
reference wire format.

**Decision.** Narrowed. HostProto is the reference *ingress* format for
host-interaction claims and effect-receipt evidence within an EvidenceSet,
and nothing more. An EvidenceSet also carries Git revisions, tests,
reports, reviewer evidence, command captures and validity windows; owning
those would be the schema expansion gate 2 exists to stop. Every HostProto
element maps to a *claim* (`docs/EVIDENCESET_VALIDATION.md`); `EffectGrant`
is authority from ActionQ/federation and `Decision` is Vuoro's judgment —
neither is ever asserted by HostProto.

The validation uses two ingress lanes into one consumer — existing auditctl
command captures and existing browser/debugger traffic. A command/PTY host
adapter is explicitly out of scope; building one would test adapter
authoring, not the consumer.

The promotion criterion is structural, not a branch count: zero checks on
profile name, adapter kind or host class in the core reducer and decision
path, with profile decoding confined to registered ingress edges; plus one
avoided blind rerun, one triggered reacquisition and one reconciled
uncertain outcome on real traffic.

**Non-goal, recorded.** Target and precondition checks are local
optimistic-concurrency controls enforced by the adapter or the target. They
create no cross-host authority or fencing layer. Resource-graph and
effect-intent projections are advisory evidence.

**Consequence.** Compatibility semantics are not declared at `v0.1.0`; they
are derived in step 7.4 from what the consumer needed. Valuation is reduced
to two figures: internal utility (3/10 → up to 8/10) and portfolio evidence
(8/10 → 9/10 on either branch).

## ADR-0014: step 7 verdict — promoted as the reference host-interaction evidence profile

**Context.** ADR-0013 set the binding criterion: zero checks on profile
name, adapter kind or host class in the core EvidenceSet reducer and
decision path, plus one avoided blind rerun, one triggered reacquisition
and one reconciled uncertain outcome, on real traffic.

**Evidence.** `vuoro/packages/vuoro-evidence` (a3aadb8, 24 tests, 384 in
the workspace). `tests/test_boundary.py` scans `core/` for any
profile/adapter/host vocabulary and forbids importing `ingress/`; it passes,
and it caught two docstrings on the way. Real traffic recorded by
`scripts/record-session.mts` in four repos — Chromium (79f72a5), debugpy
(c5f5b97), Delve (b3e9006), and an A2A-carried run through the worker
(97a7b7c) — replayed through one ingress into one reducer alongside a
2026-08-08 outctl capture manifest:

| Required | Observed |
| --- | --- |
| Avoided blind rerun | real click completed → `ACCEPT`; capture inside its window → `ACCEPT`; five A2A receipts → `ACCEPT` |
| Triggered reacquisition | real stale click/frame refused with `host_invoked:false` → `REACQUIRE`, grant `unused`; windowed receipt past `valid_until` → `EvidenceExpired` |
| Reconciled uncertain outcome | real `outcome:unknown` continue (debugpy and Delve) → `uncertain_use`, `RECONCILE(requires_observation)`; next real observation confirms → `USED`/`ACCEPT`; a later contradicting observation → `REJECT` |

The debugpy correlator ran unchanged on Delve; the MCP session loader ran
unchanged on the A2A run (receipts in status updates, observations and
evidence refs in artifacts). One ingress fix was needed during step 7.4 —
`evidence-ref/v1` had no branch in the loader — and it was at the edge.

**Decision.** Promote. HostProto is the reference ingress format for
host-interaction claims and effect-receipt evidence within a Vuoro
EvidenceSet (the ADR-0013 boundary, unchanged). Compatibility rules are
derived from what the consumer needed, and only that:

1. **Correlation is by `action_id`, and an error must be delivered in reply
   to the intent it refuses.** `error/v1` carries no `action_id`; the
   consumer took it from the call log. On MCP this pairing is the call; on
   A2A the worker must keep it. A future minor may add an optional
   `action_id` to `error/v1`; nothing may depend on it before then.
2. **Freshness is `(surface, revision)` and nothing else.** The consumer
   used no other field for staleness. Revision must remain monotonic per
   surface (kill gate 7 restated as a compatibility rule).
3. **`outcome` is interpreted as: `completed` → effect happened; `failed`,
   `stopped`, `superseded` → host was invoked, effect did not stand (grant
   *used*); `unknown` → uncertain (grant *uncertain-use*, no replay without
   an observation).** `attempted:false` or `accepted:false` → nothing was
   invoked (grant *unused*).
4. **Observation confirmation is a consumer-side predicate over
   `observation.data`.** `receipt.state_after` could not be compared to an
   observation directly because its digest algorithm is the adapter's. Until
   an adapter declares the algorithm in its capability profile, consumers
   must not compare `state_*` digests across objects.
5. **`evidence-ref.ref` is the content address.** The consumer used it as
   the item digest; adapters must keep it `sha256:` over the bytes.
6. **Decision tokens and their resolutions are not evidence.** The A2A
   decision message never became an item; only the receipt of its effect
   did. No HostProto object may carry a `Decision`.

**Consequence.** `hostproto-semantics` is canonical at `v0.1.0`; the `$id`
stays on GitHub Pages: the freeze-branch objection to a Vuoro-owned URI is
gone, but nothing depends on `$id` resolving (adapters pin by digest) and
no consumer outside these repos needs the Vuoro identity yet. Move to
`schemas.vuoro.cloud/hostproto/v1/` only when one does, or when Vuoro's own
schemas move to a `schemas.` host. Rule 4 is a debt: the capability profile should name
the state-digest algorithm in the next minor. `vuoro-evidence` is the first
consumer and its boundary test is the standing enforcement of gate 2 from
the consumer's side.

**Guard.** A change to `core/` in `vuoro-evidence` that needs host
vocabulary is a HostProto semantics gap and comes back here as an ADR, not
as a branch in the reducer.
