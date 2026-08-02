# Narrative domain model & expression semantics

Read this before composing or reviewing any member content.

## Domain model

A narrative instance is a per-device L1 program evaluated at ~1 Hz by the
ATLAS agent. Its members, by collection:

- **Inputs** — bound to device I/O points or to other instances' constructs
  via input mappings.
- **Settings** — constants; adjustable at runtime (e.g. by cloud L2 Python
  logic). Present tunable model parameters as settings, not literals. Types:
  `bool`, `number`, `enum`, `schedule`, `sequence`. A `bool` setting is
  additionally `normal` or `one_shot` (see below).
- **Computed metrics** — derived expressions. Also **Conditions** (named
  boolean expressions), **Actions** (state-machine transitions),
  **Virtual outputs** (state machines; can drive real outputs via output
  mappings), **Alarms**.
- Instances are created from **templates** (e.g. alias `generic_calculator`,
  "Generic Calculator System", for pure metrics+settings calculators).
  Template-defined members live in the template, not in the instance body;
  the instance may override them ONLY where the template declares an
  overridable, via the instance's `overrides` collection. Never specify an
  edit to a template-defined member that has no overridable — flag it
  instead.
- Instances are not silos: one instance's conditions, computed metrics, and
  outputs can feed another instance's inputs through input mappings
  (`kind: condition_name|computed_metric_name|output_name|setting_name` with
  a `source_name` naming the source instance). A rename can therefore break
  OTHER instances — check `internal-list-narrative-references`.

## Naming conventions (authoritative)

- Instance alias: `DEVICE_PURPOSE`, e.g. `conveyor_311BC02_mass_flow`
  (device aliases look like `conveyor_311BC02`).
- ALL members — inputs, settings, metrics, outputs — are **PascalCase**:
  `Motor1Current`, `Gain`, `EmptyCurrent`, `MassFlowRate`.
- Do NOT infer conventions from existing instances (e.g.
  `quarry_1_global_constants`) — several are known-bad examples. Current
  state reports what IS, not what SHOULD BE. Flag violations; never silently
  correct them.

## Expression semantics

- Namespaced references: `input.X`, `setting.X`, `metric.X`, `output.X`.
- **One-cycle delay**: every reference resolves to the PRIOR cycle's value.
  Self-reference is therefore the accumulator idiom:
  `metric.MassTotal + metric.MassFlowRate / 3600` integrates TPH → tons at
  1 Hz; `acc = acc + 1` is a counter.
- **One Shot settings are the user-facing reset/trigger idiom.** A `bool`
  setting with annotation `bool_setting_kind: one_shot` reads true for
  EXACTLY ONE scan cycle when pulsed, then self-clears. For edges of a
  *signal* (not a user action), the function vocabulary has `leo(name, bool)`
  (rising-edge pulse) and `teo(name, bool)` (falling-edge pulse). With both
  available, hand-built edge detection — a latch metric holding the previous
  value, `setting.X * (1 - metric.PrevX)` scaffolding — is a defect.
- **Booleans do NOT coerce to numbers.** The type checker is strict: mixing
  them raises `Incorrect operand types number and bool for <op>. Ensure both
  operands are numbers.` So `setting.Flag * x` and `1 - setting.Flag` are
  INVALID — a Boolean must be consumed by a conditional, never multiplied
  into arithmetic as a 0/1 gate.
  **Upsert does not type-check.** The API accepts expression text that
  `internal-validate-draft-site-narrative` later rejects. A successful upsert
  is never proof an expression is valid — only validate is.
- **Ternary `cond ? a : b` is the idiom for consuming a Boolean.** Reach for
  it FIRST; it says what it means and needs no numeric cast. Deployed,
  confirmed-valid reset-and-emit shape (Loadrite short-total), with a One
  Shot setting `Reset`:

      metric.Total = setting.Reset ? 0 : metric.Total + metric.Rate / 3600
      metric.Prior = setting.Reset ? metric.Total : metric.Prior

  Both read `setting.Reset` with the same delay, so the snapshot and the
  zeroing always land on the same cycle. Ternary also produces enum values:
  `input.boolInput ? "On" : "Off"` (string literals for `enum` members).
- `count_if(bool, ...) number` counts how many arguments are true. It works
  as a Boolean→number cast with one argument, but the ternary is the gating
  idiom — reserve `count_if` for actually counting.
- **The function vocabulary is enumerable — never guess it.** Run
  `ck-ecp internal-list-expression-functions --internal-org-id <id>` for the
  full list with signatures and doc strings. As of 2026-08 (office) it has
  42 functions: math (`abs acos asin atan ceil clamp cos exp floor is_inf
  is_nan log max min precision round sin sqrt tan truncate`), counting/
  selection (`count_if counter_up large small sequence_length
  sequence_lookup`), time (`current_hour timer timer_delay timer_pulse
  timer_retentive leading_silence`), edges/latches (`leo teo latch
  is_occurring`), control (`pid_v1 pid_v2 ramp`), alarms (`alarm_analog
  alarm_discrete`), diagnostics (`connection_status`). If a construct is not
  in the live list, say so rather than assuming.
- Prefer `clamp`/`max(0, …)` over conditionals for numeric limits.
- **Every `number` member requires a unit**; use `none` for dimensionless
  gains. Units are ShortName strings from `ck-ecp list-units` (193 of them):
  `°F`, `psig`, `%`, `sec`, `hr`, `count`, `none`. Pick ton vs tonne
  deliberately: US short ton is `ton` / `ton/h`; metric tonne is `t` / `t/h`
  (Loadrite at US sites reports US short tons → `ton`, `ton/h`).
