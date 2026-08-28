# Thesis

**HostProto defines typed, evidence-bearing interaction with stateful hosts.**

A stateful host is anything an agent must observe before it can act on it,
where the act changes what the next observation will show, and where a
reference obtained from one observation may be invalid by the time it is
used: a browser context, a debug session, an interactive process.

The claim is that one small set of semantics covers such hosts without
becoming host-specific:

1. **Handles** — host, context, surface — are opaque, server-minted, and can expire.
2. **Observations are revisioned.** Every observation carries the surface
   revision it was taken at and a cursor into an ordered event stream, so
   freshness is a comparison, not a guess.
3. **Target references are scoped to a revision** and are rejected *before*
   the host is invoked when the revision has moved. Invalidation is explicit,
   never silent retargeting.
4. **Preconditions are declared** by the caller and checked by the adapter
   before the host is touched.
5. **Intent is declared** as a closed family per adapter profile, so what was
   asked for can be compared with what was observed.
6. **Receipts** record attempted / accepted / executed / verified separately,
   name the events the action caused, and carry observed effects.
7. **Evidence is content-addressed**, raw and normalized are linked, and no
   reference implies authority to retrieve anything outside its bundle.
8. **Capability profiles are earned.** A capability is `runtime`-verified
   only by an operation that completed; declaration never upgrades it.
9. **Recovery is a defined state**, not an exception: expired handles, stale
   observations, and interrupted clients each have a named outcome.

## What this is not

- Not a wire protocol. MCP carries the primitives; A2A carries delegated
  work; the domain runtime owns execution lifecycle.
- Not a browser project. The browser was the first host and remains a
  conformance backend.
- Not a remote executor. A PTY adapter is deliberately excluded from the
  first challengers because it would drift there.

## What would falsify it

See the kill gates in `PLAN.md`. The short form: the browser adapter and the
debug adapter need different core envelopes; or the shared schema degenerates
into `{"type": "object"}`; or HostProto grows a scheduler, task store, or
transport of its own.

## Evidence so far

The browser-workbench repository executed these semantics — under browser
names — on a deterministic mock, on a real WebKitGTK engine (12 scenarios × 3
repetitions × 2 profile variants, deterministic), and cross-checked six of
the twelve scenarios against Playwright/WebKit as an external oracle with
zero differences. That is evidence the semantics work for one host class. It
is not evidence they generalize; that is what this repository exists to test.
