# Alignment map: browser-workbench → HostProto

Source: `browser-workbench/spec/WORKBENCH_PROTOCOL_V1.md`,
`RUNNER_CONTRACT_V1.md`, `CAPABILITY_MATRIX_V1.json`, and the native slices
1–6 evidence. Every row must resolve to a schema or an explicit *stays in
adapter / stays in runtime* decision. *Unmapped* rows block step 1.

| browser-workbench | HostProto | Schema | Note |
| --- | --- | --- | --- |
| `session_id` | `HostHandle` | `handles` | one live host process |
| profile (`ephemeral` / `persistent`), lease | `ContextHandle` | `handles` | isolation + writer fencing |
| `page_id` | `SurfaceHandle` | `handles` | one observable/actionable surface |
| `generation` | `revision` | `observation` | increments on document commit or restore; DAP: on stop/continue |
| `event_seq`, `since_event`, `next_event` | `cursor` | `observation` | only ordered identifier |
| `target_id` + stamped `generation` | `TargetRef` | `target-ref` | scoped to revision |
| `stale_target` (rejected before backend) | `target_invalidated` | `error` | invalidation is explicit |
| `preconditions {url,title,generation}` | `Precondition` | `precondition` | adapter profile defines assertable fields |
| `intent.kind` families | `Intent` | `intent` | closed set per capability profile |
| receipt (`attempted/accepted/executed/verified`, `caused_event_ids`, `effects`, `state_before/after`) | `Receipt` | `receipt` | unchanged in substance |
| `artifact_ref` (`sha256:`), `raw_refs` | `EvidenceRef` | `evidence-ref` | content-addressed, no retrieval authority |
| capability matrix row (availability, provider, semantics, verification) + `RuntimeLedger` | `CapabilityProfile` | `capability-profile` | `runtime` only by execution |
| `lease_fenced`, `lease_conflict`, `integrity_mismatch`, checkpoint resume | `Recovery` outcomes | `recovery` | named states, not exceptions |
| `session.checkpoint` / resume | `Recovery.resume` | `recovery` | checkpoint is state, never approval |
| `page.await` conditions | `WaitCondition` | `observation` (`wait`) | host-side wait over the recorded stream |
| `deviations[]` | `Receipt.deviations` / `Observation.deviations` | both | surfaced, never dropped |
| run spec, gates, run result envelope | **stays in runtime** | — | execution lifecycle is the domain runtime's |
| `run.compare`, tolerances, suppressions | **stays in conformance tooling** | — | not host semantics |
| corpus, profiles, oracle classification | **stays in conformance tooling** | — | becomes the conformance suite |
| native adapter channel (stdin/stdout ordinal stream) | **stays in adapter** | — | transport is not HostProto's |
| `provider` (`engine` / `injected` / `host` / `oracle`) | `CapabilityProfile.provider` | `capability-profile` | kept; it is provenance |
| browser chrome, bridge | **out of scope** | — | product surface |

## What the browser names hid

- `generation` reads as "page generation" but is a surface revision; DAP's
  stop/continue cycle is the same thing.
- `lease` reads as browser single-writer, but is context-level writer fencing
  any host with side effects needs.
- `targets` were discovered by injected script on WebKitGTK and by the same
  script on the oracle; the *reference* semantics (scoped, invalidated) did
  not depend on how targets were found. That is the part that generalizes.
