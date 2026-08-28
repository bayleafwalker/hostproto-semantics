# EvidenceSet validation — the phase after step 6

Four to six weeks, followed by a binding decision. Scope agreed 2026-08-28
(ADR-0013). This phase decides whether HostProto is promoted or frozen; it
does not extend the protocol.

## What is being valued

Only two outcomes matter. Everything else the track might produce is
incidental.

| Value | Current | After validation |
| --- | ---: | ---: |
| Internal utility | 3/10 | up to 8/10 |
| Portfolio evidence | 8/10 | 9/10, whether promoted or frozen |

Internal utility rises only if a consumer that is not HostProto needs the
envelope. Portfolio evidence rises either way: promotion yields an
integration result, freezing yields a credible negative result with a
stated reason.

## The promotion target, bounded

HostProto is **not** the reference wire format for the entire
`EvidenceSet`. An `EvidenceSet` also holds Git revisions, tests, reports,
reviewer evidence, command captures, and validity windows. Promoting
HostProto that broadly would invite exactly the schema expansion kill gate
2 guards against.

The precise target:

> HostProto is the reference ingress format for host-interaction claims and
> effect-receipt evidence within an EvidenceSet.

### Contract mapping

| HostProto element | Vuoro interpretation |
| --- | --- |
| Intent and declared effects | Effect-intent claim correlated with an externally issued `EffectGrant`; never the grant itself |
| Receipt lifecycle | Claim about attempted, accepted, executed, and verified effect use |
| `outcome: unknown` | Uncertain grant use; reconcile before considering replay |
| `host_invoked: false` | Claim that the grant was not consumed by a host invocation |
| Evidence references and state hashes | EvidenceSet items; the collector adds provenance and validity metadata |
| Revision and cursor | Surface-local freshness evidence |
| Independent observation | Separate EvidenceSet item that may confirm or contradict the receipt |
| Decision | Vuoro's judgment over the evidence; never something asserted by HostProto |

Everything in the left column is a *claim*. Authority (`EffectGrant`) and
judgment (`Decision`) come from outside and stay outside.

### Non-goal, stated once

HostProto target and precondition checks are local optimistic-concurrency
controls, enforced by the actual adapter or target. They do not create a
cross-host authority or fencing layer. Resource-graph and effect-intent
projections remain advisory evidence.

## Steps

### 1. One-evening housekeeping

- Tag `v0.1.0`.
- Replace the `https://hostproto.invalid/...` placeholder `$id` URIs.
- Establish `hostproto-semantics` as canonical; archive the original
  `hostproto` repository (privately, per the standing decision).
- Do **not** declare compatibility semantics yet; they are derived in step 4
  from what the consumer actually needed.
- Record the non-goal above in `DECISIONS.md` (done: ADR-0013).

### 2. Build the consumer

One provider that ingests HostProto envelopes as host-interaction claims
inside Vuoro EvidenceSets. The core path must represent generically:

- stale or invalidated targets;
- precondition refusal;
- unavailable capabilities;
- persisted evidence;
- completed and failed effects;
- uncertain outcomes;
- independent confirmation or contradiction.

`EffectGrant` remains an authoritative input from ActionQ / federation.
HostProto only reports whether and how that authority appears to have been
used.

### 3. Exercise the valuable loop — two ingress lanes, one consumer

The live-infrastructure command scenario must **not** produce a third
HostProto adapter. There is no command/PTY host in this phase. Two existing
sources feed the same EvidenceSet implementation:

| Lane | Source | What it exercises |
| --- | --- | --- |
| Command captures | existing auditctl captures | cost-blind rerun and validity-window problem |
| Host-interaction receipts | existing HostProto browser and debugger traffic | generic receipt ingestion |

Through the auditctl lane, show that:

- valid evidence can prevent a blind rerun;
- expired evidence emits `EvidenceExpired` and justifies reacquisition;
- an uncertain effect marks the grant as uncertain-use;
- a fresh observation is acquired before any retry decision;
- contradictory evidence produces an explicit `Decision`.

Through the HostProto lane, route one real browser session
(`hostproto-mcp-playwright`) and one real debugger session (a
`hostproto-dap-core` binding) into the same provider. No additional host
adapter.

### 4. Decide, structurally

Raw branch count is gameable. The hard criterion:

> Zero checks on profile name, adapter kind, or host class in the core
> EvidenceSet reducer and decision path.

Profile-specific decoding may exist only at registered ingress edges.
Promotion additionally requires, on real traffic:

1. at least one genuinely avoided blind rerun;
2. one correctly triggered reacquisition;
3. correct reconciliation of one uncertain outcome.

| Result | Action |
| --- | --- |
| Criterion holds, all three observed | Promote HostProto as the reference host-interaction evidence profile; derive compatibility rules from what the consumer needed |
| Core logic needed host-specific semantics | Narrow, or freeze as a protocol study, with the offending semantics named |

## Portfolio write-up

Begins now, not after the verdict. The consumer verdict is its final
section. Promotion gives it an integration result; freezing gives it an
unusually credible negative result. Neither branch wastes the work.

## Dependencies and current state

- `EvidenceSet`, `EffectGrant`, `EvidenceExpired`, `Decision` exist today in
  Vuoro planning documents (`vuoro/docs/plans/`), not yet in code. Step 2
  therefore also fixes their first implementation; keep the reducer and
  the ingress edges in separate modules from day one so the step 4
  criterion can be checked mechanically (grep, or an import-boundary test).
- auditctl captures: `auditctl/docs/contracts/publisher-subprocess.md`
  (collector captures the observable half, canonically hashed).
