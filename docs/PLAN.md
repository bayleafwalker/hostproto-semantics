# Plan

Bounded generalization of HostProto for headless agent operations. The
browser becomes one conformance backend; the question is whether the
semantics survive a second, structurally different host.

## Step 0 — verify the spec claims (gates step 1)

The plan assumes specific features of MCP 2026-07-28 and A2A v1.0. None has
been verified in this repository yet. Each must be confirmed against the
linked spec section, with the section and revision recorded in
`DECISIONS.md`, before any HostProto abstraction is deleted on its account.

| Assumed feature | Where it matters | Status (verified 2026-08-28) |
| --- | --- | --- |
| MCP: implicit sessions removed; explicit server-minted handles for cross-request state | handles map 1:1 | **verified** — changelog 2026-07-28, major change 1 (SEP-2567); `server/tools` § Stateful Tools. *Nuance:* that section is non-normative and "the protocol has no concept of a state handle" — a handle is an ordinary string argument. HostProto's `handles` schema is therefore needed, not duplicated. |
| MCP: `server/discover`, per-request capability metadata | capability profile publication | **verified** — major changes 2 and 3 (SEP-2575); capabilities travel in `_meta` per request |
| MCP: `subscriptions/listen` | surface-change notifications | **verified with a constraint** — major change 4. Opt-in types are `toolsListChanged`, `promptsListChanged`, `resourcesListChanged`, `resourceSubscriptions` only. Host-state change must be modelled as a **resource subscription** on a surface resource; there is no arbitrary event channel. |
| MCP: elicitation (MRTR) for approval / auth / missing input | recovery → human | **verified** — major changes 7 and 8 (SEP-2322): `resultType: "input_required"`, `inputRequests`, retry with `inputResponses` + `requestState` |
| MCP Tasks extension: durable handles, polling, `input_required`, cooperative cancel | one async primitive | **verified with differences** — `io.modelcontextprotocol/tasks` (major change 6, SEP-2663): `tasks/get` polling, `tasks/update` for input, `tasks/cancel` cooperative, notifications via `subscriptions/listen`, server may return a task unsolicited. **`tasks/list` was removed** and SSE resumability was removed (major change 9): reconnection is by durable task id only, and *listing* tasks is not MCP's job — it is A2A's or the domain runtime's. |
| A2A v1: `ListTasks`, `GetTask`, `SubscribeToTask`, `CancelTask`, artifact updates, resubscription | domain-run projection | **verified** — A2A 1.0.0 "what's new": all four operations present (renamed from `tasks/*`), `TaskArtifactUpdateEvent` with `index`, tasks scoped to the authenticated caller |
| A2A v1: profile extensions constraining message parts to a domain schema | `hostproto-work-order/v1` | **verified** — extensions topic: profile extensions may "narrow the space of allowed values (for example, requiring all messages to use DataParts adhering to a specific schema)"; declared in `AgentCapabilities.extensions[]` with `required: true`. *Nuance:* the 1.0 spec names the container `Part` (text / bytes / structured data); `DataPart` is the older name. |
| A2A v1: signed Agent Cards | worker publication | **verified** — spec § 8.4, JWS (RFC 7515) over JSON Canonicalization (RFC 8785), `AgentCardSignature` |

Additional findings from the same pass:

- MCP `inputSchema` / `outputSchema` now accept any JSON Schema 2020-12 keyword and `structuredContent` any JSON value (minor change 10, SEP-2106), so `schemas/` can be used verbatim — **but** MCP imposes `$ref` resolution requirements. Cross-file `$ref` by `$id` (as `intent` → `target-ref` here) must be bundled or inlined in tool definitions. Step 1 adds a bundler.
- MCP `_meta` carries OpenTelemetry `traceparent` / `tracestate` (minor change 2). HostProto evidence refs should carry the trace id so receipts correlate with domain-run traces without a new field of their own.
- Roots, Sampling, and Logging are deprecated. Nothing here depended on them.

If a feature is thinner than assumed, HostProto keeps that piece and says so.

## Step 1 — protocol-alignment pass (3–4 days)

Map every browser-workbench type onto its HostProto schema
(`ALIGNMENT_MAP.md`), and every HostProto 0.1.0 type from the `hostproto`
repository's spec package (`HOST_PROTOCOL_V0`, `CAPABILITY_MODEL`,
`TEMPORAL_AND_STATE_SEMANTICS`, its four schemas), then onto MCP and A2A. Delete duplicated discovery,
task, transport, and content abstractions. Deliverable: `schemas/` complete
with examples and negative tests; the map has no row marked *unmapped*; a
bundler that inlines cross-file `$ref` for MCP tool definitions.

## Step 2 — headless MCP reference adapter (4–5 days)

Playwright, because it is a cheap live denominator. Expose create-context,
observe, act, wait, close as MCP tools using these schemas directly;
receipts as `structuredContent`; screenshots / DOM / traces as resources.
This inverts the browser-workbench rule that the oracle is never core
(`DECISIONS.md` ADR-0002): WebKitGTK becomes the challenger that checks
Playwright, not the reverse.

## Step 3 — DAP schema spike (3 days, before the A2A worker)

Express a debug session in these schemas on paper and in `examples/`:
threads and frames as targets that invalidate on resume; stopped / continued
as revisions; `stepOver` / `setBreakpoint` as intent; event stream as the
cursor. No runtime. This runs **before** the A2A worker because the worker is
projection and cannot fail interestingly, while DAP is where the envelope
either generalizes or does not (ADR-0003).

## Step 4 — A2A host-worker (3 days)

One Agent Card, one real workflow skill (for example
`inspect_web_application`), A2A task projected from a domain run, MCP
HostProto server used internally. Evidence manifest as an A2A artifact.

## Step 5 — DAP adapter (full)

Only if step 3 needed no envelope change.

## Step 6 — native WebKitGTK conformance

Retained while the human-and-agent Linux workbench is a product goal. No
longer required to prove the capability plane.

## Kill gates

Stop the generalization if any of these becomes true:

1. browser and DAP need different core envelopes;
2. the shared schema degenerates into arbitrary JSON payloads;
3. HostProto acquires its own scheduler, durable task store, or transport;
4. individual clicks or debugger steps become A2A skills;
5. every MCP call gets wrapped in an A2A task;
6. adapter-specific escape hatches become normal operation;
7. observation revision cannot be expressed uniformly — for instance a host
   with no single monotonic event order per surface;
8. runtime verification stops being earnable per adapter, so capability
   profiles can only be declared.

Gates 7 and 8 are the earliest signals; watch them during step 3.
