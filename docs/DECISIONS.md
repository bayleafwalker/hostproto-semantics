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
