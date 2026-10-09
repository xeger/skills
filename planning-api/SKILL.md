---
name: planning-api
description: Use when structuring, drafting, or reviewing a quarterly or annual goal ("rock") as a Planning API exchange between Strategy and Execution — writing an Outcome Contract (purpose, base/ideal end state, evidence, guardrails) or producing/critiquing 1–3 Execution Options (approach, resources, scope, effort, risks, off-ramps, suggestion). Triggers on "outcome contract", "planning API", "execution options", "off-ramps", "base end state", or when a strategist and a team need to agree on what success means before deciding how to get there. Always overlays the individual-goal-setting skill.
---

# The Planning API

## Overview

Strategy and execution often operate at the wrong level of abstraction. Strategy defines success too vaguely to support resourcing and tradeoffs, or too specifically by prescribing implementation. The result is churn, unclear ownership, and repeated alignment work.

The Planning API is an **interface contract** between the two sides. Strategy publishes an **Outcome Contract** that says what must be true and why. Execution responds with **1–3 Execution Options** that say how it could be achieved and what it costs. The two sides then choose an option together and that becomes the plan.

This skill imposes that contract as a constraint on goal discussions. It does not replace goal-quality reasoning — see *Relationship to individual-goal-setting* below.

## Relationship to individual-goal-setting

**Always load `individual-goal-setting` alongside this skill.** It owns goal *quality* (output over activity, SMART, leading indicators, no invented numbers). This skill owns goal *shape* (the fields each side must fill in and the handshake between them).

When both are active:

- The goal-setting worksheet's answers feed the Outcome Contract. Use the mapping table below rather than running two separate interviews.
- The goal-setting criteria checklist still applies to the *Evidence of success* field. An Outcome Contract whose evidence is activity-based or lagging-only is not ready.
- The goal-setting rule against fabricating baselines, targets, or commitments applies to every field on both sides of the API. Mark unknowns as `TBD` and say who owns resolving them.
- If the two skills seem to conflict, the Planning API decides *which fields exist*; individual-goal-setting decides *whether a field's content is good enough*.

### Worksheet → Outcome Contract mapping

| Outcome Contract field | Fed by goal-setting worksheet questions |
|---|---|
| Purpose | 2 Intent & mission link · 3 Company-goal alignment · 6 User/customer impact · 7 Business impact |
| Base end state | 5 Activity → output · 10 Commitment level (the **must-do** portion) |
| Ideal end state | 10 Commitment level (the **aspirational** portion), if any |
| Evidence of success | 8 SMART tightening · 9 Leading indicators |
| Guardrails | *(not covered by the worksheet — must be elicited separately)* |

Worksheet questions 1, 4, and 11 (current wording, tightening, enhanced wording) still run; the enhanced wording becomes the one-line headline of the Outcome Contract.

## The contract

### From Strategy: the Outcome Contract

One per Goal or Rock. All five fields are required.

| Field | Definition | Not ready if… |
|---|---|---|
| **Purpose** | Why this matters: the business, customer, or engineering problem being solved | It names a deliverable instead of a problem; it doesn't ladder to a company goal |
| **Base end state** | The minimum set of conditions that must be true to call the effort successful | It describes work done rather than conditions true; it contains "and/or"; it is secretly the ideal state |
| **Ideal end state** | Additional conditions to aim for if capacity, time, and risk allow | It is indistinguishable from base; it is unbounded ("as much as possible") |
| **Evidence of success** | Measurements that show the end state has actually been achieved | No baseline; no leading indicator; measurement doesn't exist and nobody owns building it |
| **Guardrails** | Constraints and non-negotiables: architectural, experience, security, cost, timing, etc. | It prescribes an implementation (that's an Approach, not a guardrail); it is empty ("no constraints" is almost never true) |

**The line Strategy must not cross:** the Outcome Contract says what and why. It never says how. If a draft contract contains a technology choice, a sequence of tasks, or a team assignment, move it to Guardrails only if it is genuinely non-negotiable; otherwise delete it and let Execution propose it in an Option.

### From Execution: 1–3 Execution Options

Each option is a self-contained proposal that satisfies the Base end state within the Guardrails. Each option has seven parts; the set has one Suggestion.

| Field | Definition | Not ready if… |
|---|---|---|
| **Approach** | A proposed way to achieve the outcome while respecting the guardrails | It violates a guardrail; it achieves something other than the base end state |
| **Resources** | People, skills, and capacity needed | Named people have no stated availability; a required skill isn't on the team and isn't flagged |
| **Scope** | The specific work included in this option | It can't be distinguished from the other options' scope; it hides work in "etc." |
| **Effort** | An effort estimate and/or expected completion date | There is no date and no size; the estimate has no stated confidence |
| **Risks** | Uncertainties, dependencies, and ways this option fails | Only external risks are listed; no dependency on another team is named |
| **Off-ramps** | Predefined ways to reduce scope, and the impact of each on outcome and resourcing | An off-ramp drops the *base* end state (that's failure, not an off-ramp); impact isn't stated |
| **Suggestion** *(once per set)* | Which option the team recommends, and why | No reason given; the reason is only "it's easiest" |

**Why 1–3 and not 1:** a single option forces Strategy into accept/reject. Two or three options expose the real tradeoff (speed vs. completeness vs. risk) so the choice is a *strategy* decision, not an engineering one. Options should differ in a way Strategy cares about — not three flavors of the same plan.

### The handshake

1. Strategy publishes the Outcome Contract.
2. Execution reads it and may push back on *the contract itself* (unclear purpose, conflicting guardrails, unmeasurable evidence) before writing options. Fix the contract first.
3. Execution publishes 1–3 Options with a Suggestion.
4. Strategy and Execution choose an option together. The chosen option plus the contract is the plan.
5. Record the chosen option's Off-ramps as the pre-agreed scope-reduction path; invoking one later is a notification, not a renegotiation.

## Workflow

Determine which side of the API the user is on, then run the matching mode. A technical strategist may legitimately sit on both sides; keep the roles separate in the output even when one person writes both.

### Mode A — Drafting an Outcome Contract (Strategy side)

1. Load `individual-goal-setting` and run its worksheet, batching questions.
2. Additionally elicit **Guardrails**. Ask: what would make a technically successful result unacceptable? (architecture, UX, security, cost, dates, compatibility, team boundaries)
3. Split the enhanced goal's commitment into **Base** (must-do) and **Ideal** (aspirational). If the user only has one, ask whether the stretch exists or whether the whole thing is base.
4. Strip any *how* that leaked in. List what you removed so the user can promote it to a guardrail if it is truly non-negotiable.
5. Render the contract in the template below. Apply the *Not ready if…* column; name any failing field.

### Mode B — Producing Execution Options (Execution side)

1. Require an Outcome Contract as input. If none exists, run Mode A first or ask for it — do not invent one from a verbal goal.
2. Check the contract for defects and surface them before drafting options.
3. Elicit 1–3 approaches from the user. Do not invent approaches the team hasn't proposed; you may *suggest* axes of variation (scope, sequencing, build vs. buy, team split) to help them find a second or third.
4. For each approach, fill the seven fields. Mark unknown effort, availability, or dependencies as `TBD (owner)`.
5. Ensure every option's Off-ramps preserve the Base end state. Ensure the Suggestion gives a reason tied to Purpose or Risks.
6. Render in the template below.

### Mode C — Reviewing a submitted contract or option set

1. Identify which artifact it is.
2. Check each field against the *Not ready if…* column and (for Evidence of success) the goal-setting criteria checklist.
3. Report per-field: ✅ ready / ⚠️ weak / ❌ not ready, with the specific defect and the question that would fix it.
4. Do not rewrite silently. Propose rewrites, labeled as proposals.

## Output templates

### Outcome Contract

```
## Outcome Contract: <enhanced goal headline>

**Purpose.** …
**Base end state.** (must-do, 100%)
- …
**Ideal end state.** (aspirational, ~70%)
- …
**Evidence of success.**
- Lagging: <metric> from <baseline> to <target> by <date>
- Leading: <signal> visible by <week N>
**Guardrails.**
- …
```

### Execution Options

```
## Execution Options for: <contract headline>

### Option 1 — <short name>
**Approach.** …
**Resources.** …
**Scope.** …
**Effort.** <size/date, confidence>
**Risks.** …
**Off-ramps.**
- <reduction> → impact on outcome: … ; impact on resourcing: …

### Option 2 — …

**Suggestion.** Option N, because …
```

## Common Mistakes

| Mistake | Result | Fix |
|---|---|---|
| Base end state written as a task list | Team finishes the tasks and nobody can say whether the goal succeeded | Rewrite each bullet as a condition that is true or false at quarter end |
| Ideal state that is just "base, but more" with no bound | Infinite scope creep under the banner of "ideal" | Give ideal its own measurable conditions and a stopping point |
| Guardrail that is actually an approach ("use Kafka") | Strategy has silently taken the engineering decision; execution options collapse to one | Ask: is this non-negotiable, or a preference? Preferences move to the Suggestion rationale |
| Empty guardrails | Execution proposes something strategically unacceptable; alignment work repeats | Prompt for the standard categories; "none" needs an explicit justification |
| One option presented as three | Strategy has no real choice; the exercise is theater | Options must differ on an axis Strategy cares about |
| Off-ramp that abandons the base end state | What's called a reduction is actually a failure mode in disguise | Off-ramps trim Ideal and Scope only; dropping Base is a renegotiation of the contract |
| Effort without a date or a confidence | The LOE can't be tracked and slippage is invisible | State size and/or date, plus confidence (high/med/low) and what would change it |
| Inventing a baseline, estimate, or availability to fill the template | Looks complete, rests on fiction | `TBD (owner)` — never fabricate (inherited from individual-goal-setting) |

## When NOT to use

- Work under ~2 weeks or a single ticket — the contract is overkill; write the task.
- Pure status or progress updates — that is the proposed "Runtime API" (requirements changes, done-ness, resourcing changes), which is not yet defined. Note the gap rather than stretching this contract to cover it.
- Externally fixed deliverables (regulatory, contractual) where neither end state nor approach is negotiable — fill the contract for the record, but skip the options exercise.

## Source

Chris Rathgeb, *The Planning API* (internal Google Doc, Sept 2026). Open items at time of writing: an "Effort / expected completion date" field was added in response to review; a "Runtime API" for in-flight changes was proposed and deferred to teams.
