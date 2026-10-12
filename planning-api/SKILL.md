---
name: planning-api
description: Use when a technical strategist or an execution team member needs to do their part of a Planning API exchange for a quarterly or annual goal ("rock") — interviews the strategist until they can issue a crisp Outcome Contract (the "call": purpose, base/ideal end state, evidence, guardrails), or interviews the team until they can return crisp Execution Options (the "response": approach, resources, scope, effort, risks, off-ramps, suggestion). Also reviews a drafted call or response. Triggers on "planning API", "outcome contract", "execution options", "off-ramps", "base end state", "help me write my rock", or when Strategy and a team need to agree on what success means before deciding how to get there. Overlays the individual-goal-setting skill.
---

# The Planning API

## Overview

The Planning API is CrossnoKaye's interface between Strategy and Execution for goals and rocks. It is defined in the standards doc:

**[The Planning API](https://docs.google.com/document/d/1ILL-XBJ4RAidA6KsrMBovu3ruuF5rikb78IwKuk9j0o/edit?tab=t.0)** (Chris Rathgeb, Sept 2026)

That doc is the source of truth for *which fields exist*. If it and this skill disagree, the doc wins — re-read it when the user says it has changed, or when a field here looks unfamiliar to them.

The exchange has two messages:

| | Who sends it | Artifact | Says |
|---|---|---|---|
| **Call** | Strategy (the technical strategist, "TS") | **Outcome Contract** | What must be true, and why. Never how. |
| **Response** | Execution (the team) | **1–3 Execution Options** | How it could be done, and what each way costs. |

Strategy and Execution then choose an option together; contract + chosen option is the plan.

This skill does not write either message for the user. It **interviews** them — one field at a time, pushing back on vague answers — until the message is crisp enough to send, then renders it.

## Step 0 — Which side are you on?

Establish this before anything else. If it isn't obvious from the request, ask:

- **"I own the goal and need to hand it to a team"** → you are making the **call**. Go to *Making the call*.
- **"I've been handed a goal and need to say how we'd do it"** → you are writing the **response**. Go to *Writing the response*.
- **"I have a draft and want it checked"** → go to *Reviewing a draft*.

A TS sometimes sits on both sides. Run the two interviews separately and in order — finish the call before starting the response — so the *what* is settled before the *how* can leak into it.

## How to run the interview

These rules apply to both sides.

1. **Harvest first.** Read everything the user has already given (pasted goal, doc, ticket, notes) and pre-fill what you can. Show them what you extracted per field and mark each field *answered*, *partial*, or *missing*. Never re-ask an answered question.
2. **Ask in field order, a few questions at a time.** One field per turn, or two when they are tightly coupled (Base + Ideal; Risks + Off-ramps). Do not dump the whole questionnaire.
3. **Test every answer against its crispness test.** If it fails, say specifically why and ask the follow-up probe. Do not accept an answer to be polite, and do not move on with a silently weak field.
4. **Play the answer back in contract wording.** After each field, restate it as it would appear in the artifact and get a yes/no. People spot errors in a restatement that they miss in their own words.
5. **Never invent content.** No fabricated baselines, targets, dates, estimates, names, or availability. If the user doesn't know, record `TBD (owner, by when)`. You may offer *candidate* phrasings or *categories* to consider, clearly labeled as suggestions.
6. **Loop until done.** The message is ready when every field passes its test, or fails only by an explicit `TBD` the user has chosen to send with. State which it is. Then render the template.
7. **Keep the running draft visible.** After every couple of fields, show the artifact so far, so the user always knows how close they are.

**Goal quality comes from `individual-goal-setting`.** Load it alongside this skill. Its principles (output not activity, leading not lagging, no invented numbers) and criteria checklist are what "crisp" means for Purpose, end states, and Evidence. Run *this* interview, not its worksheet as a second one; the mapping at the bottom shows which worksheet questions each field covers.

## Making the call (Strategy → Outcome Contract)

One contract per goal or rock. Five fields, all required. Start by asking for the goal as currently worded, then work down.

### 1. Purpose
*Why this matters — the business, customer, or engineering problem being solved.*

Ask:
- What problem exists today, and who feels it?
- What happens if we don't do this, this quarter?
- Which company goal does this serve?

**Crisp when:** it names a problem and who has it, not a deliverable; someone outside the team would understand why it beats other uses of the quarter.
**Probe if weak:** "That describes something we'd build. What gets better, and for whom, once it exists?"

### 2. Base end state
*The minimum set of conditions that must be true to call the effort successful.*

Ask:
- At the end of the period, what must be true that isn't true today?
- If only one of those came true, would you still call it a success? Which one?
- Is there anything here you'd be disappointed, but not surprised, to miss? (That belongs in Ideal.)

**Crisp when:** each item is a condition that will be plainly true or false on the date — not work performed; the list is the genuine minimum; there is a date.
**Probe if weak:** "That's a task. If the team finished it and nothing else changed, would you be satisfied? What would you look at to decide?"

### 3. Ideal end state
*Additional conditions to aim for if capacity, time, and risk allow.*

Ask:
- If this went better than expected, what else would be true?
- Where does it stop — what is explicitly *beyond* ideal and out of bounds?

**Crisp when:** it is distinct from Base, is itself a checkable condition, and has an upper bound. "None — Base is the whole goal" is a valid answer if stated explicitly.
**Probe if weak:** "'As much as possible' can't be planned against. What's the next concrete condition past Base?"

### 4. Evidence of success
*Measurements that tell us the end state has actually been achieved.*

Ask:
- For each Base condition: what would you look at to know it's true? Where does that number live today?
- What is it now (baseline) and what must it be (target)?
- What could we see in the first few weeks that tells us we're on or off track?
- If the measurement doesn't exist yet, who builds it, and is that part of this goal?

**Crisp when:** every Base condition has a measurement with a baseline, target, and date; at least one leading indicator is named; any measurement that doesn't exist has an owner.
**Probe if weak:** "If two people disagreed at quarter end about whether this succeeded, what would settle it?"

### 5. Guardrails
*Constraints and non-negotiables — architectural, experience, security, cost, timing, etc.*

Ask:
- What would make a result unacceptable even if it hit every Base condition?
- Walk the categories: architecture/platform, customer or operator experience, safety and security, cost/budget, dates and external commitments, compatibility, team or ownership boundaries. Anything in each?
- For each: is it truly non-negotiable, or a strong preference?

**Crisp when:** each guardrail is a constraint on the solution, not a solution; each is non-negotiable; the list isn't empty without an explicit reason.
**Probe if weak:** "'Use X' is an approach. What are you protecting by requiring X? State that, and let the team decide whether X is how to honor it."

### Before rendering: the how-leak check

Re-read the whole draft for *how*: technology choices, task sequences, named assignees, architecture. For each, ask the user: non-negotiable (→ rewrite as a Guardrail stating what it protects) or preference (→ remove; mention it to the team informally)? List what was removed. The call says what and why; choosing how is the response's job.

### Template — the call

```
## Outcome Contract: <one-line goal, output-focused, with date>

**Purpose.** …

**Base end state.** (must be true by <date>)
- …

**Ideal end state.** (if capacity, time, and risk allow)
- …

**Evidence of success.**
- <Base condition> → <metric> from <baseline> to <target> by <date>
- Leading: <signal> visible by <week N>

**Guardrails.**
- …

**Open items.** <TBD (owner, by when)> — or "none"
```

## Writing the response (Execution → Execution Options)

**Input required: the Outcome Contract.** Ask for it. If there isn't one, do not reconstruct it from a verbal goal — send the user to their strategist, or run *Making the call* with whoever owns the goal.

### First: can you accept the call?

Before any options, read the contract with the user and ask:
- Could you tell, on the date, whether each Base condition is true? Which ones are ambiguous?
- Do any guardrails conflict with each other or with the Base end state?
- Does any guardrail dictate the approach, leaving you nothing to decide?
- Can the Evidence actually be measured?

If anything fails, the right response is **a pushback on the call**, not options built on a guess. Help the user write the specific question to send back to Strategy, and stop there until it's resolved (or the user decides to proceed with a stated assumption, recorded in the response).

### Then: find the options

Ask:
- What's the first way you'd do this?
- What would you do if you had half the time? If a key person weren't available? If you could buy or reuse instead of build?
- Which of these differ in a way your strategist would care about — speed, completeness, risk, cost?

One option is allowed when there is honestly one viable way; say why. Two or three should differ on an axis Strategy cares about, not be three flavors of one plan. The approaches must come from the team — you may suggest axes of variation, not invent options.

### For each option

**Approach** — *a proposed way to achieve the outcome while respecting the guardrails.*
Ask: In two or three sentences, how does this get to the Base end state? Which guardrails shape it?
**Crisp when:** a strategist can follow it without the team in the room; it reaches Base; it violates no guardrail.

**Resources** — *the people, skills, and capacity needed.*
Ask: Who, at what fraction of their time, for how long? Is any needed skill missing from the team? What are these people *not* doing instead?
**Crisp when:** capacity is stated per person or role, with known PTO and competing commitments accounted for; gaps are flagged.

**Scope** — *the specific work included in this option.*
Ask: What are the major pieces of work? What is explicitly out? What does this option include that the others don't?
**Crisp when:** in and out are both listed; no "etc."; it is distinguishable from the other options' scope.

**Effort** — *an effort estimation or expected completion date.*
Ask: When would this be done, or how big is it? How confident are you, and what would move the date?
**Crisp when:** there is a date or a size, a confidence level (high/medium/low), and the main thing the estimate depends on.
**Probe if weak:** "What would have to be true for that date to hold? Which of those are you least sure of?"

**Risks** — *uncertainties, dependencies, or ways this option fails.*
Ask: What don't you know yet? Which other teams, vendors, or sites must deliver something? If this option failed, what's the most likely reason?
**Crisp when:** it includes internal uncertainties as well as external ones; each dependency names who and what; the likeliest failure is stated.

**Off-ramps** — *predefined ways to reduce scope, and the impact on outcome and resourcing.*
Ask: If you were running late, what would you cut first? What does cutting it cost the outcome, and what does it free up? By when would you need to decide?
**Crisp when:** each off-ramp states what is cut, the effect on the Ideal/Base end state, and the capacity or time recovered. An off-ramp that gives up a Base condition must say so plainly — taking it means reopening the contract, not quietly proceeding.

### Once for the set: Suggestion
*Which option the team recommends.*

Ask: Which would you pick, and why? What would change your mind?
**Crisp when:** it names one option and gives a reason tied to the Purpose, the end states, or the Risks — not just "it's least work".

### Template — the response

```
## Execution Options for: <contract headline>

**Assumptions / open questions on the contract.** … — or "none"

### Option 1 — <short name>
**Approach.** …
**Resources.** …
**Scope.** In: … Out: …
**Effort.** <date or size> — confidence <high/med/low>; depends on …
**Risks.** …
**Off-ramps.**
- <cut> → outcome impact: … ; frees: … ; decide by: …

### Option 2 — …

**Suggestion.** Option N, because …
```

## Reviewing a draft

1. Identify whether it is a call or a response, and (for a response) get the call it answers.
2. Check each field against its **Crisp when** test.
3. Report per field: ✅ crisp / ⚠️ weak / ❌ missing, with the specific defect and the one question that would fix it.
4. Offer to run the interview on the failing fields. Propose rewrites only as labeled proposals — never silently rewrite, never fill gaps with invented content.

## After both messages exist

Strategy and Execution choose an option together. Record the chosen option's off-ramps as the pre-agreed scope-reduction path. The doc does not yet define what happens in flight (requirement changes, resourcing changes, declaring done) — a "Runtime API" has been proposed in its comments and left to teams. Don't stretch the Planning API to cover it; note the gap.

## Common ways a message isn't crisp

| Symptom | What to ask |
|---|---|
| Base end state is a task list | "If all of that got done and nothing changed, did we succeed?" |
| Ideal is "Base, but more" | "What's the next concrete condition, and where does it stop?" |
| Guardrail names a technology or design | "What does that protect? State the constraint, not the solution." |
| Guardrails empty | Walk the categories; "none" needs a stated reason |
| Evidence has no baseline | "What is it today, and where would I look it up?" — else `TBD (owner)` |
| Three options that are one plan | "Which of these would your strategist choose differently between?" |
| Effort with no confidence | "What would have to be true for that date to hold?" |
| Off-ramp silently drops Base | "That gives up a must-have — it's a renegotiation. Say so explicitly." |
| A number nobody actually knows | `TBD (owner, by when)` — never fabricate |

## Field ↔ individual-goal-setting worksheet

So the user is interviewed once:

| Outcome Contract field | Covers worksheet questions |
|---|---|
| Headline | 1 Current wording · 4 Tightening · 11 Enhanced wording |
| Purpose | 2 Intent & mission link · 3 Company-goal alignment · 6 User/customer impact · 7 Business impact |
| Base end state | 5 Activity → output · 10 Commitment level (must-do) |
| Ideal end state | 10 Commitment level (aspirational) |
| Evidence of success | 8 SMART tightening · 9 Leading indicators |
| Guardrails | *(not in the worksheet)* |

## When NOT to use

- Work under ~2 weeks or a single ticket — write the task.
- Status or progress updates on a plan already agreed — that's the undefined "Runtime API".
- Externally fixed deliverables (regulatory, contractual) where neither the end state nor the approach is negotiable — fill in the contract for the record; skip the options.
