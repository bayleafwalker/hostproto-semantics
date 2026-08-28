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
