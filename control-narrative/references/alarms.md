# Authoring alarms

Read this before adding or editing an `alarms` member. The stored shape is in
`instance-schema.md`; everything here is convention and constraint that the
shape does not tell you. Figures below come from a survey of the production
library: **886 template alarms + 310 custom (instance-level) alarms across 8
facilities**, plus what `internal-validate-draft-site-narrative` actually
enforces.

## The nine fields

    name, description, control_point, group_name, severity,
    message_template, activation_condition, deactivation_condition, tags{}

There is **no `alarm_name`** here. `alarm_name` exists only on an
`alarm_override` (in `overrides[]`), which carries `name` *and* `alarm_name`
as separate fields — do not copy that shape onto an alarm member.

## Hard constraints (validator-enforced, not style)

- **`control_point` is mandatory for an instance-level alarm.** Omitting it —
  or setting `tags.linked_object: ""`, which is what 261 *template* alarms do
  — fails validation with `alarm is missing linked object control point:
  linked object tag is missing`. Templates may leave it null because they
  cannot know a site's point aliases; instances may not. This is why all 310
  custom alarms in the library set it: the validator requires it.
- **`group_name` must exactly match a `Name` from `ck-ecp list-alarm-groups`**
  (that endpoint takes only `--token` — it is global, no org or agent). The
  eight: `EH&S`, `Refrigeration`, `Room Temps`, `Equip. Health`, `System`,
  `Escalations`, `Energy AI`, `CK Diagnostics`. Mind the literal ampersand and
  the period in `Equip. Health`. Zero free-form values in 1,196 alarms.
- **`severity` is one of three lowercase strings**: `critical`, `warning`,
  `caution`. Never an integer, never null.
- **`tags` duplicates two fields and must agree with them**: `tags.group` ==
  `group_name`, `tags.severity` == `severity`, `tags.linked_object` ==
  `control_point`, and `tags.linked_object_kind` is the literal
  `"control_point"`. All four keys, always.

## Conditions

`activation_condition` / `deactivation_condition` are **inline expression
text**, not bare member names — a reference always carries its namespace
prefix. The dominant shape (97% of custom alarms) is a single reference plus
its negation:

    activation_condition   "condition.FooAlarmActive"
    deactivation_condition "!condition.FooAlarmActive"

`deactivation_condition` is never null or empty in the entire library.

**Put the numeric comparison in a named condition, not in the alarm.**
`metric.` appears **zero** times in any alarm expression across all 1,196.
Alarms reference `condition.` overwhelmingly (plus `setting.`, `output.`,
`input.`).

### Hysteresis and debounce

Do **not** express hysteresis as two different thresholds on the alarm. Push
the timing into the condition with `timer_delay`, then let the alarm negate:

    timer_delay(condition bool, delay number, timeout number) bool
                                ^ trip delay    ^ clear delay

    CONDITION ExcessiveDowntime_condition
      timer_delay(setting.DowntimeAlarmEnabled && condition.DowntimeStatus,
                  setting.MaxDowntimeSP, setting.DowntimeClearDelaySP)

When the monitored quantity is already elapsed time, the trip delay **is** the
threshold — no metric comparison needed. This is the `discrete_runproof_alarms`
idiom ("failed to start after N seconds").

A minority two-condition form exists (`standard_vessel_pressure_alarms 5.0.0`)
where the deadband is applied only on the clearing side — legitimate for
analog setpoints with real hysteresis, but it is the 3% path and v2/v3 of that
same template shipped a double-negation bug (`!condition.XInactive` where
siblings use `condition.XInactive`). Prefer the `timer_delay` + `!` form.

Gate every threshold alarm on a `bool` enable setting (`*AlarmEnabled`,
`bool_setting_kind: normal`) — universal in the library. A literal `"false"`
in both condition fields is the local idiom for a parked/unwired alarm.

## message_template

Interpolation is `{token}` — **single braces, bare token**. The CLI's own
`--help` example shows `"{{.Name}} is {{.Severity}}"`; that Go-template syntax
appears nowhere in production. Ignore it.

Tokens: `{org}`, `{facility}`, `{device}`, `{dot}` (separator, always before
`{device}`), `{value}`, `{unit}`. Canonical form:

    "{org} {facility}: <Sentence describing the fault> {dot} {device}"

Some sites substitute a literal prefix (`"Innovative 2: …"`, `"Nordic 1: …"`).

**`{value}` / `{unit}` resolve against `control_point` only.** There is no
syntax for interpolating a computed metric, setting, or condition. If the
message needs a number, that number must be a control point — and if the bound
point is boolean, omit both tokens.

## Naming

`name` is the only name field and is the unique key within the instance.
`{device}` and `{control_point}` interpolate here as well as in the message.

- Templates: `"{device} <Title Case Fault Phrase>"`.
- Instances: either keep `{device}`, or spell it out (`"Compressor 1 Fault"`).
  Both are conventional; snake_case names are an outlier.

Backing conditions follow `<Thing>AlarmActive` / `<Thing>AlarmInactive`, or
`<Thing>_condition`.

`description` is null on 310/310 custom alarms — leave it null.

## Choosing a group and severity

Rough semantics from usage: `System` = the narrative complaining about its own
config (bad setpoint, manual mode); `Equip. Health` = a device faulted or
failed to start/stop; `Refrigeration` = a process value out of range; `EH&S` =
life safety. `CK Diagnostics` is unused; `Escalations` has one use in the whole
library — do not pioneer them.

`critical` means faulted equipment or an EH&S event. Degraded-but-safe is
`warning`. Multi-tier ladders climb `caution` → `warning` → `critical`.

## When the device has no control points

A `building`-kind device (site-level rollups like `quarry_1`) may have **zero**
control points, which collides with the mandatory-`control_point` rule. Borrow
the point that most nearly means the thing being alarmed. It is a UI linkage,
not a data dependency — the alarm logic does not read it — and loose
association is established practice (Watsonville links a pump `runCMD` to a
differential-pressure alarm; Loveland links `compressor_2_clearAlarmCMD` to a
fault alarm). Pick deliberately and say so in the change-list.

## Known traps

- **`alarmAnalog` vs `alarm_analog`**: production expressions use the
  camelCase spelling with an argument order that disagrees with the registered
  signature (trip delay passed in the `deadband` slot at Watsonville). Same for
  `alarmDiscrete`. Verify against `internal-list-expression-functions` rather
  than copying a live site; `timer_delay` has no such ambiguity.
- Alarms are invisible in an unmerged read. A `null` `Alarms` collection on an
  instance means "no *custom* alarms" — the template may define plenty. Merge
  per SKILL.md rail 6 before claiming a site has none.
