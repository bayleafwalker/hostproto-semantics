# HostProto — a protocol study with a consumer verdict

*Written 2026-08-28. The last section is the verdict; everything before it
was written to be true whichever way that section went.*

## The question

Agents act on stateful hosts — browsers, debuggers, terminals — through
tools that return strings. When the action's consequence matters, nothing
in that string says whether the host was actually invoked, whether the
thing acted on was still the thing observed, or whether the outcome is
known at all. HostProto asks one question: **can a single typed,
evidence-bearing envelope describe interaction with structurally different
hosts, without becoming a third wire protocol?**

The thesis (`THESIS.md`): MCP carries the primitives, A2A carries delegated
work, HostProto is the semantics both carry.

## What was built

Six repositories, one day's git history each pinned to the last by digest:

| Repo | Role |
| --- | --- |
| `hostproto-semantics` | eleven JSON Schemas (`intent`, `target-ref`, `precondition`, `receipt`, `observation`, `error`, `recovery`, `evidence-ref`, `deviation`, `handles`, `capability-profile`), bundled and content-addressed; the plan, the kill gates, fourteen ADRs |
| `hostproto-mcp-playwright` | reference adapter: six MCP 2026-07-28 tools whose schemas *are* the bundles, on real Chromium |
| `hostproto-a2a-worker` | an A2A 1.0 worker with one skill that carries HostProto objects verbatim in status updates and artifacts |
| `hostproto-dap-core` | the DAP semantics once, as a tested promise; a debugger is a 27–48 line `EngineBinding` |
| `hostproto-dap-debugpy`, `hostproto-dap-delve` | two unrelated debuggers on that core |

Everything is tested on the wire: real client, real server process, real
engine. 12 + 11 + 9 + 15 + 13 tests across the adapters; nothing between
client and engine is mocked.

## What the semantics are

- A **target** is observed at a **revision** of a **surface**; acting on it
  at a later revision is refused *before* the host is invoked
  (`target_invalidated`, `host_invoked: false`).
- A **precondition** is checked the same way; refusal is not failure.
- A **receipt** says, separately, whether the action was attempted,
  accepted, executed and verified — and its `outcome` may be `unknown`.
  Verification is *earned* by read-back, never declared.
- An **observation** is revisioned and cursored; when bounded it says what
  it omitted and what it lost.
- **Evidence** is content-addressed; **deviations** from the raw host
  stream name the rule that suppressed them.
- **Recovery** names its cause and what it needs; a human decision is a
  token, not a side channel.

## What was found

Kill gates were written before the work and checked at each step. None
fired. Two findings against the author's own assumptions are recorded
because the evidence forced them:

- The first Delve result — "Delve ignored a `setVariable` write" — was
  retracted the same day: an off-by-one in the fixture, exposed by the
  program's own output kept as evidence (ADR-0011). The receipt design
  caught its designer.
- A slice-5 differential had been silently `blocked` for an infrastructure
  reason nobody read (browser-workbench ADR-S6-03). "Blocked" is also where
  defects hide.

Wire facts not in any spec changelog were recorded as they were met:
`resources/subscribe` does not exist on the 2026-07-28 era; MCP defines no
handle concept; `tasks/list` was removed from the Tasks extension.

## The boundary that was tightened

A first proposal made HostProto the wire format of a whole `EvidenceSet`.
That was narrowed (ADR-0013): an EvidenceSet also carries Git revisions,
tests, reports, reviewer evidence and validity windows, and owning those
would be exactly the schema expansion the gates guard against. The
promotion target became:

> HostProto is the reference ingress format for host-interaction claims and
> effect-receipt evidence within an EvidenceSet.

Every HostProto element maps to a *claim*. Authority (`EffectGrant`) and
judgment (`Decision`) come from outside and stay outside.

## The validation

A consumer was built that is not HostProto: `vuoro-evidence`, a
host-agnostic reducer over claims with a rerun decision path
(`ACCEPT` / `REACQUIRE` / `RECONCILE` / `REJECT`), and registered ingress
edges — one for HostProto, one for command-capture manifests under
auditctl's validity-window rule. The promotion criterion was structural:
zero checks on profile, adapter or host class in the core, enforced by a
test that scans the source.

Real traffic was recorded from Chromium, debugpy, Delve and an A2A-carried
run, and replayed through that consumer.

## Verdict

**Promoted** (ADR-0014). The structural criterion held; the three required
observations — an avoided blind rerun, a triggered reacquisition, a
reconciled uncertain outcome — each occurred on real traffic, on two host
classes, three engines and two carriers. The one ingress defect found was
at the edge. Six compatibility rules were derived from what the consumer
needed and nothing more; one of them (state-digest algorithm not declared)
is an open debt on the capability profile.

What this result is not: it is not evidence that HostProto scales beyond
the hosts tried, and it is not a claim that the reducer is the right
EvidenceSet design for Vuoro. It is evidence that one envelope, unchanged
across two host classes, can be consumed by something that never had to
ask which host it came from.
