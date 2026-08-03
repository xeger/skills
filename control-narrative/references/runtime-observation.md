# Observing a deployed narrative

Read this before reading live values, trending metrics, or diagnosing the
runtime behavior of a deployed narrative — a blank card, a suspect zero, a
metric that "isn't working". Design-time work (composing, upserting,
validating) is covered by the other references; this file is about the
running system.

## Where narrative values live

Narrative metrics, conditions, and virtual outputs are **facility readings**,
not platform "synthetic readings" — the `*-synthetic-*` endpoints do not
apply to them.

## Resolving reading source IDs

`get-point-ids` / `internal-get-point-ids` are unreliable (504s / timeouts
observed 2026-08). Use the device listings instead, which carry the IDs
directly:

- **`list-controlled-devices`** → per device, `Metrics[]`, `Conditions[]`,
  `Outputs[]` each carry a UUID that **is** the reading source ID. A metric,
  condition, or virtual output is represented as a reading under that same
  ID. *Settings and raw I/O do not work this way.*
- **`list-all-controllers`** → controller `ControlPoints[]` with IDs, for raw
  field points (belt scales, totalizer pulses, run commands, …).

## Fetching historical values

`readings-historical-values` with `mode: "interactive"` (valid modes:
`default` / `interactive` / `background` — not `live`) and a window of a few
hours; longer windows fail with "query exceeds limit for cold storage".
Pass `include_scaled: true` when instrument health is in question (see Raw
vs. scaled below).

**The CLI renders the response envelope but drops the NDJSON body** — run
under `ck-ecp --debug` and parse the traced HTTP response instead.

## Streaming alternatives

(Source: `services/front/design/agentsubset/readings_websocket.go`.)

- `stream_latest_readings` — bidirectional WebSocket that needs a
  subscription payload (`source_ids` — empty means all — plus `include_raw` /
  `include_scaled`). A bare CLI invocation returns `{}` because no payload is
  sent.
- `stream_latest_readings_sse` — unidirectional SSE variant at
  `/orgs/{org_id}/agents/{agent_id}/readings/latest/stream-sse`; streams
  **all** readings with no subscription payload — the easier option.

Both emit only initial values and changes, plus keepalives, and require the
`readings.read` scope.

## Raw vs. scaled — read before judging any instrument

Every ATLAS sensor has a **raw** value, a per-sensor **offset**, and an
**adjusted/scaled** value. **Narratives consume the scaled value**, and so
should any analysis. Raw values misread as scaled are a recurring source of
phantom faults — "railed" negatives, impossible rates on stopped equipment —
that evaporate once the scaled value is pulled. Before declaring an
instrument broken, fetch the scaled reading
(`readings-historical-values` with `include_scaled: true`) and judge from
that. When auditing, record WHICH form each captured figure is; an audit note
that doesn't say is untrustworthy later.

Diagnostic signature of an unwired/inactive input: zero variance (min = max)
and raw orders of magnitude different from a known-healthy sibling channel.
A calibrated zero dithers; a dead input does not.

## Reading the results

Accumulator-style metrics (running totals) are **step values recorded only
on change** — a single flat row over a quiet period is normal, not missing
data. Rate metrics update every bucket. A *rate* with one row is suspicious;
a *total* with one row usually is not.

## Triaging a blank or suspect metric

A blank card can mean three different things, and guessing from the card
alone cannot separate them:

1. **No series yet.** A new or *renamed* metric has no history under its
   name — nothing existed before the deploy, so pre-deploy windows are
   legitimately empty.
2. **A genuine zero.** For pulse-fed accumulators, zero is the correct answer
   whenever no pulses have arrived since the last reset — e.g. plant down.
   Publishing a correct zero is healthy behavior that *looks* dead.
3. **A delivery problem.** The narrative can be publishing correct values
   while cards stay blank — the gap is downstream of the agent
   (transmission, ingest, or query), and such gaps can clear on their own.

Triage by querying the reading directly (IDs and endpoints above) and
trending it against its upstream source over the same window. If both ends
of the chain agree, evaluation and publishing are fine; keep looking
downstream.

Corollaries:

- **A passthrough metric's physics lives upstream.** Many exposed metrics
  are `input.X` passthroughs of a value computed on another instance.
  Renaming one is a labeling change only; changing what it *means* requires
  re-pointing its input mapping, not editing its expression. When one looks
  wrong, verify at both ends — its own reading and the upstream source's.
- **A correct zero is not proof it tracks.** Verifying a metric while the
  process is idle only establishes it publishes; re-check under load that
  the value climbs with its source before calling the deploy verified.
- Before re-investigating, check whether the hypothesis was already tested
  and refuted — record refuted hypotheses in the site's own docs so a later
  session doesn't churn instances "fixing" a non-bug.
