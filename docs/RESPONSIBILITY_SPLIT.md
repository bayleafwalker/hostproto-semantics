# Responsibility split

| Layer | Owns | Must not own |
| --- | --- | --- |
| **MCP** | discoverable primitive tools with typed `inputSchema`/`outputSchema`, `structuredContent`, resources and resource links, explicit server-minted state handles, subscriptions, elicitation for approval / auth / missing input, the Tasks extension for a primitive that is genuinely asynchronous | host semantics, workflow, execution lifecycle |
| **A2A** | agent discovery (Agent Card), coarse skills, delegated tasks, streaming, interruption (`INPUT_REQUIRED`, `AUTH_REQUIRED`), artifacts, resubscription, cancellation | primitive operations; one click or one debugger step is never a skill |
| **HostProto** | host / context / surface handles, observation revision and freshness, stable target references and their invalidation, preconditions, declared intent, receipts and observed effects, evidence and provenance references, adapter capability profiles, recovery states | discovery, transport, scheduling, durable task storage, retries |
| **Domain runtime** (ActionQ or equivalent) | authoritative execution lifecycle: claims, retries, cancellation, terminality | host semantics |
| **Adapters** | one host class each: browser, DAP, later others; the mapping from host events to HostProto observations and from HostProto intent to host operations | anything another adapter would also need — that is a HostProto defect |

## The three task notions are correlated, never merged

| | Scope | Owner |
| --- | --- | --- |
| **MCP Task** | one long-running capability invocation | MCP server (adapter) |
| **A2A Task** | one delegated assignment that may make many MCP calls | A2A host-worker |
| **Domain run** | the authoritative internal lifecycle behind an A2A task | domain runtime |

Each carries the others' identifiers for correlation. There is no universal
task table. A generic `Task` type appearing in `schemas/` is a kill-gate event.

## How HostProto reaches MCP and A2A

- The schemas in `schemas/` are used **directly** as MCP tool `inputSchema` /
  `outputSchema` fragments and as the payload schema of an A2A profile
  extension (working name `hostproto-work-order/v1`). They are not
  re-declared per transport.
- Screenshots, DOM / AX snapshots, traces, and evidence manifests are MCP
  resources and A2A artifacts, referenced by `evidence-ref`.
- A HostProto `recovery` outcome that needs a human maps to MCP elicitation
  at the primitive level and to A2A `INPUT_REQUIRED` at the assignment level.
