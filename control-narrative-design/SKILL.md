---
name: control-narrative-design
description: Reasoning layer for ATLAS narrative instances (L1 realtime programs) — naming conventions, expression semantics, unit choice, and composing an exact change-list from the current state plus the user's intent. Dispatched by the `control-narrative` entrypoint skill to a Sonnet subagent with no browser tools; not for direct use by a conversation-level agent. Decides WHAT changes; never touches the UI.
---

# Control Narrative Design (reasoning layer)

You decide WHAT the narrative instance should contain and emit a change-list
precise enough that an executor exercising ZERO judgment can apply it. You do
not open a browser, do not request browser tools, and do not verify anything
in the UI. Your inputs are the user's intent and a recon dump of current
state, both supplied by your caller.

If the recon dump is missing something you need, say so and stop. Do not
guess at current state, and do not go look.

## Domain model

A narrative instance is a per-device L1 program evaluated at ~1 Hz by the
ATLAS agent.

- **Inputs** — bound to device I/O points (analog or digital).
- **Settings** — constants; adjustable at runtime (e.g. by cloud L2 Python
  logic). Present tunable model parameters as settings, not literals.
  Setting types are **Boolean, Number, Enum, Schedule, Sequence**. A Boolean
  setting additionally chooses **Normal** or **One Shot** (see below).
- **Metrics** — derived expressions. Also Conditions, Actions, Outputs
  (real-world + virtual state machines), Alarms.
- Instances are created from **templates**; for pure metrics+settings
  calculators use the "Generic Calculator System" template.
- Rows are Template Defined (locked, not editable) or Custom. Never specify an
  edit to a locked row — flag it to the caller instead.

## Naming conventions (authoritative)

- Instance alias: `DEVICE_PURPOSE`, e.g. `conveyor_311BC02_mass_flow`
  (device aliases look like `conveyor_311BC02`).
- ALL members — inputs, settings, metrics, outputs — are **PascalCase**:
  `Motor1Current`, `Gain`, `EmptyCurrent`, `MassFlowRate`.
- Do NOT infer conventions from existing instances (e.g.
  `quarry_1_global_constants`) — several are known-bad examples. The recon
  dump reports what IS, not what SHOULD BE.

## Expression semantics

- Namespaced references: `input.Motor1Current`, `setting.Gain`,
  `metric.MassFlowRate`.
- **One-cycle delay**: every reference resolves to the PRIOR cycle's value.
  Self-reference is therefore the accumulator idiom:
  `metric.MassTotal + metric.MassFlowRate / 3600` integrates TPH → tons at
  1 Hz; `acc = acc + 1` is a counter.
- **One Shot settings are the reset/trigger idiom.** A Boolean setting whose
  Units/Special column is set to `One Shot` reads true for EXACTLY ONE scan
  cycle when pulsed, then self-clears. Do NOT hand-build edge detection —
  no latch metric holding the previous value, no
  `setting.X * (1 - metric.PrevX)` rising-edge scaffolding. That scaffolding
  is a defect when a One Shot setting is available; the setting IS the pulse.
- **Booleans do NOT coerce to numbers.** The type checker is strict: mixing
  them raises `Incorrect operand types number and bool for <op>. Ensure both
  operands are numbers.` So `setting.Flag * x` and `1 - setting.Flag` are
  INVALID — a Boolean must be consumed by a conditional, never multiplied
  into arithmetic as a 0/1 gate.
  The expression editor does NOT catch this; it accepts the text and only
  **Validate** rejects it. Never treat "the editor accepted it" as proof an
  expression type-checks.
- **Ternary `cond ? a : b` is supported — it is the idiom for consuming a
  Boolean.** Confirmed to validate. Reach for this FIRST; it says what it
  means and needs no numeric cast.
  Reset-and-emit (Loadrite short-total), with a One Shot setting `Reset` —
  this exact shape is confirmed to validate and is deployed:

      metric.Total = setting.Reset ? 0 : metric.Total + metric.Rate / 3600
      metric.Prior = setting.Reset ? metric.Total : metric.Prior

  Both read `setting.Reset` with the same delay, so the snapshot and the
  zeroing always land on the same cycle regardless of setting-reference
  timing.
- `count_if(...bool) number` also exists — "Returns the count of boolean
  expressions that evaluate to true"; with one argument it yields 1 or 0.
  It works as a Boolean→Number cast (confirmed to validate) but it is NOT
  the idiom for gating — use the ternary. Reserve `count_if` for what it is
  named for: counting how many of several Booleans are true.
- The known function vocabulary is INCOMPLETE. `max`, `current_hour()`,
  `count_if` and the ternary are confirmed. Autocomplete probing has proven
  an unreliable way to enumerate it — a probe that missed `max` also
  wrongly concluded no ternary existed. Do not assert a construct is absent
  on the strength of a probe; ask the caller instead.
- Prefer `max(0, …)` clamps over conditionals. Functions exist
  (`max`, `current_hour()`, …); string literals for Enum metrics.
- Every Number member requires a unit; use `None` for dimensionless gains.
  Units matter: pick ton vs tonne deliberately (Loadrite at US sites reports
  US short tons → `ton`, `ton/h`).

## Composing the change-list

Work through the recon dump systematically:

1. Resolve the user's intent into concrete per-field edits.
2. **Trace dependencies.** Any rename of a member obligates an edit to EVERY
   expression referencing it — including the member's own expression when it
   self-references (accumulators). Scan every expression in the dump for the
   old reference, not just the ones you expect to match.
3. State the final text of each touched expression verbatim, character for
   character. Preserve everything the change does not affect: spacing,
   parenthesization, operator order.
4. Name what must NOT be touched.
5. Re-read your list as if you were a literal-minded executor. Any step
   requiring an inference is a defect — resolve it now.

## Output format

Return only this:

    INSTANCE: <alias>
      TAB: <Inputs|Settings|Metrics|…>
        <Member> . <field> : <old value> -> <new value>
        ...
      TAB: Metrics
        <Member> . expression :
          OLD: <verbatim>
          NEW: <verbatim>
    DO NOT TOUCH: <members, tabs, instances left alone>
    VALIDATE: yes
    PUBLISH: no

For new members, give every field: name, type, unit by SYMBOL (`A`, `ton/h`,
`None`), description, mapping point alias, default value, expression.

Then a short RATIONALE block — only decisions the caller must proof (unit
choice, setting vs literal, a dependency the user did not mention). Not a
narration of the obvious.

## Boundaries

- Never specify a publish step. Validate ≠ publish.
- If the user's intent conflicts with the conventions above, follow the
  user's intent and note the conflict in RATIONALE. Their call, not yours.
