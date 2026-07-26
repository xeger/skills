---
name: control-narrative
description: Entrypoint for ANY request touching ATLAS narrative instances (L1 control narratives) in the atlaslive.io facility-config UI — designing, creating, modifying, renaming, inspecting, or reviewing instances, inputs, settings, metrics, conditions, actions, outputs, or alarms. Load this FIRST whenever a request mentions a narrative instance, an atlaslive.io facility-config URL, or a member of one; it routes the work to the cheap subagent chain. Do not load control-narrative-recon, -design, or -implementation directly.
---

# Control Narrative (entrypoint / router)

You are the conversation-level agent. Your job is to ROUTE, never to execute.
Browser automation and design reasoning both happen in subagents, chosen for
cost. You hold only the user's intent and short structured reports.

## Hard rules

- **Never open a browser tab yourself.** Not to "just check", not to verify a
  subagent's report. Page content in your context is the single largest
  avoidable cost in this workflow.
- **Never load `control-narrative-recon`, `control-narrative-design`, or
  `control-narrative-implementation` into your own context.** They are
  subagent skills. Loading one means you are about to do the work yourself.
- **Never publish** a draft config. Validate ≠ publish. Publishing requires an
  explicit, unambiguous user instruction and is still a separate deliberate
  step you confirm first.
- Require terse, structured subagent reports. Every token a subagent returns
  is re-read on every subsequent turn of this conversation.

## The chain

Run these in order. Skip a stage only under the conditions named.

### 1. Recon — Haiku, read-only

Dispatch when you do not already have the current state of the instance(s)
verbatim in context. Skip only if a recon report earlier in THIS conversation
still describes the live state (no edits since).

    model: haiku
    prompt: Invoke the `control-narrative-recon` skill, then follow it.
            Target: <URL>. Scope: <which instances, or "all in the draft">.
            <Anything specific to extract.>

Returns a structured dump: instance aliases, members with type/unit/default/
mapping, and every expression verbatim. Read-only; it cannot mutate.

### 2. Design — Sonnet, no browser

    model: sonnet
    prompt: Invoke the `control-narrative-design` skill, then follow it.
            You have NO browser tools and must not request any.
            User's intent: <verbatim ask>.
            Current state (from recon): <paste the recon dump>.
            Emit the change-list in the format the skill specifies.

Returns an exact change-list. If the user's ask is a pure mechanical
transformation you can already state verbatim for every affected field — and
recon confirmed exactly which fields those are — you may skip this stage and
write the change-list yourself. When in doubt, dispatch; Sonnet reasoning is
cheaper than a wrong edit to a live control narrative.

### 3. Proof — you, no tools

Check the change-list against the user's ask item by item before anything
mutates. This is the last gate before live config changes. Look for: members
the user did not ask to touch, expressions whose references were not updated
to match a rename, missing units on Number members, anything the design agent
inferred rather than was told.

### 4. Implement — Haiku, one agent per instance

    model: haiku
    prompt: Invoke the `control-narrative-implementation` skill, then follow
            it. Target: <URL for this instance>. The user is already logged
            into ATLAS in Chrome.
            Change-list: <the fully resolved list for THIS instance only>.
            Apply it literally. Stop and report if the UI does not match.

Fan out across instances (they are independent). Serialize within an instance.
Only ONE agent runs Validate — dispatch it after the implementors report, or
name one implementor as the validator.

Escalate an implementor to Sonnet only after a Haiku attempt fails on UI
mechanics, and say what failed in the retry prompt.

### 5. Relay

Report to the user: what changed, the verbatim final text of touched
expressions, save/validate outcomes, and anything the implementors flagged.
Tell them nothing was published.

## Failure handling

- **Transient API error (529) mid-implementation**: resume the SAME agent via
  SendMessage — its transcript survives. Do not respawn; some edits may have
  landed. Tell it to re-read the page state before continuing.
- **Implementor stops on a UI mismatch**: that is correct behavior, not a
  failure. Feed the mismatch back through recon → design, do not tell the
  implementor to use its judgment.
- **Friction reports**: implementors report where their skill's instructions
  were wrong or missing. Fold these into the relevant skill file.
