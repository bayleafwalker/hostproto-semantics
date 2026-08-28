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
- Replace the `https://hostproto.invalid/...` placeholder `$id` URIs → `https://bayleafwalker.github.io/hostproto-semantics/schemas/v1/` (done; a move to `schemas.vuoro.cloud/hostproto/v1/` is a line item of the *promote* branch in step 4).
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
| Command captures | existing outctl capture manifests (`_artifacts/outctl-*/captures/*/manifest.json`) under auditctl's `harness.baseline` validity-window rule | blind rerun and validity-window problem |
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
- **Premise corrected 2026-08-28:** auditctl has no command-capture event
  type and no capture ref prefix; bulk payloads are `immutableRef
  kind=artifact` material by rule (`auditctl/ndjson.py`). The only real
  command captures are outctl manifests (retired binding, artifacts
  intact, schema-drifted: no argv recorded). The validity-window semantics
  are auditctl's, from the `harness.baseline` contract
  (`publisher-subprocess.md` §"silence is the in-window state"). The lane
  therefore ingests outctl manifests with a collector-declared window; the
  collector, not the capture, owns the window. Still no new host.
- "cost-blind rerun" is a coinage of this phase, not a term in the Vuoro
  corpus; the nearest normative wording is "emit `EvidenceExpired` rather
  than silently rerunning" (long-term-direction §5.1).
- Step 7.2 done 2026-08-28: `vuoro/packages/vuoro-evidence` — core
  (`model`, `reducer`, `decision`), ingress (`hostproto`, `command-capture`),
  17 tests including the mechanical boundary check.

## Step 3 record — 2026-08-28

Two real sessions were recorded by `scripts/record-session.mts` in
`hostproto-mcp-playwright` (79f72a5, Chromium, 10 calls) and
`hostproto-dap-debugpy` (c5f5b97, debugpy, 14 calls) and committed as
fixtures in `vuoro/packages/vuoro-evidence/tests/fixtures/`. Replayed
through `vuoro_evidence.ingress.hostproto.session_log` into the reducer the
command-capture lane also uses (vuoro `2ae1a8c`, 21 tests):

| Required observation | Where it occurred on real traffic |
| --- | --- |
| Avoided blind rerun | browser `a-click` completed (rev 2→3) → `ACCEPT`; outctl capture within its window → `ACCEPT` |
| Triggered reacquisition | browser `a-click-stale` `target_invalidated`, `host_invoked:false` → `REACQUIRE`, grant `unused`; a windowed receipt past `valid_until` → `EvidenceExpired(past_valid_until)` |
| Reconciled uncertain outcome | debugpy `a-continue-unknown` `outcome:unknown` → grant `uncertain_use`, `RECONCILE(requires_observation)`; the next real observation saw the program running → confirmed, `USED`, `ACCEPT`; the post-pause observation contradicts → `REJECT` |

Structural criterion so far: `tests/test_boundary.py` passes — no
profile/adapter/host vocabulary in `core/`, no import of `ingress/` from
`core/`. The only knowledge that had to live at the edge: how an
observation confirms a receipt (a predicate over observation data, supplied
by the correlator) and which action an error belongs to (the intent's
`action_id` from the call log — the error object itself carries none).

Not yet done for step 4: the same traffic from a second debugger binding
(Delve) and an A2A-carried session, to check that the ingress edge, not
just the core, is binding-agnostic; and the portfolio write-up.

## Step 4 record — 2026-08-28

Delve (`hostproto-dap-delve` b3e9006) produced the same 14-call shape as
debugpy and ran through the identical correlator. The A2A worker
(`hostproto-a2a-worker` 97a7b7c) produced a 27-record run — five receipts
in status updates, one `INPUT_REQUIRED` decision token answered over A2A,
thirteen observations and three evidence refs in artifacts — through the
unchanged session loader. vuoro `a3aadb8`, 24 tests.

**Verdict: promote.** ADR-0014 records the evidence and the six
compatibility rules derived from consumer need. Housekeeping's deferred
item — `$id` under `schemas.vuoro.cloud/hostproto/v1/` — is now authorised.
