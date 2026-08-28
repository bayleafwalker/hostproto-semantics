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

# Alignment map: HostProto 0.1.0 → HostProto semantics

Source: the `hostproto` repository's spec package (`HOST_PROTOCOL_V0`,
`TEMPORAL_AND_STATE_SEMANTICS`, `CAPABILITY_MODEL`, four schemas). This is
the earlier, chrome-facing browser-host contract. Its lifecycle, terminality
and suppression rules were stricter than browser-workbench's and four of them
were missing here until this pass.

| HostProto 0.1.0 | HostProto semantics | Schema | Note |
| --- | --- | --- | --- |
| `session_id`, bridge session | `HostHandle` | `handles` | reconnect creates a new bridge, not a new host — matches |
| `view_id`, view lifecycle `creating/open/closing/closed/terminated` | `SurfaceHandle.lifecycle` | `handles` | **added by this pass**; id never reused, `closed` terminal |
| `session.get_state` snapshot + `seq` | `Observation` with `revision` + `cursor` | `observation` | reconnect = snapshot then events after `cursor.next` → `Recovery.reobserve_required` |
| host-assigned monotonic `seq`; raw ordinal separate | `cursor`; `EvidenceRef.source_refs` | `observation`, `evidence-ref` | partial order is the oracle, not callback sequence |
| `navigation_id` with terminal `success/failed/stopped/superseded` | `Receipt.outcome` | `receipt` | **added by this pass**: `completed/failed/stopped/superseded/unknown` |
| deadline → `outcome: unknown`, reconcile, finding | `Receipt.outcome = unknown` + `deviations[divergence]` | `receipt` | **added by this pass**; "a deadline does not prove the effect did not occur" |
| suppression record: raw ref, rule id, object ids, reason | `Deviation{kind: suppression}` | `deviation` | **added by this pass**; rule_id and raw_ref required |
| `view.open_requested` decision token, deadline, default deny; `decision_expired`, `decision_already_resolved` | `Intent.decision_token`, consumed once; `precondition_failed` with `data.reason` | `intent`, `error` | finer error codes not adopted; reason travels in `data` |
| capability `status/semantics/source/notes` | `availability/semantics/provider/notes` | `capability-profile` | `source: adapter` ≡ `provider: injected`; `experimental` → `stability` (**added**) |
| capabilities immutable after `welcome`; `backend.degraded` invalidates | `immutable_per_run`; `Recovery.cause = capability_degraded`; error `capability_degraded` | `capability-profile`, `recovery`, `error` | **added by this pass** |
| `navigation.stop` accepted ≠ stopped; terminal event is the oracle | `Receipt.accepted` vs `outcome` | `receipt` | matches |
| exactly-once terminality, request `cancel`, redelivery dedup | **stays in runtime / transport** | — | MCP request semantics + domain runtime |
| `hello`/`welcome` handshake, version selection | **replaced by MCP** `server/discover` + per-request `_meta` | — | verified step 0 |
| envelope kinds, JavaScript facade | **stays in adapter / chrome** | — | transport |
| evidence manifest, finding, trace record schemas | **stays in conformance tooling** | — | consumers of `evidence-ref`, not host semantics |
| explicitly absent in v0: downloads, permissions, dialogs, persistent profiles | present here via browser-workbench slices 3–4 | `intent`, `capability-profile` | v0's absence was by design; the browser profile now declares them |
