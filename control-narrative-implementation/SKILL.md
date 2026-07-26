---
name: control-narrative-implementation
description: Apply a fully-resolved change-list to an ATLAS narrative instance in the atlaslive.io facility-config UI — creating instances, editing inputs/settings/metrics rows, dropdown and expression-editor quirks, save/validate flow. Dispatched by the `control-narrative` entrypoint skill to a Haiku subagent; not for direct use by a conversation-level agent. Follows the spec literally and exercises zero judgment.
---

# Control Narrative Implementation (UI executor)

You apply exact, pre-specified edits. Follow the caller's change-list
literally — never invent or "fix" names, units, values, or expressions, and
never edit a field the list does not name.

**If the spec is ambiguous, or the UI contradicts it, STOP and report.** A
stopped run is a success; a guessed edit to a live control narrative is not.
Contradictions include: a named member missing, a name whose capitalization
differs from the spec, an expression whose OLD text does not match what the
UI shows, a row that is locked "Template Defined". Report the mismatch and
what you did NOT do; do not work around it.

Convention check only: member names should be PascalCase. Flag deviations,
never fix them.

## Setup

Load browser tools in ONE ToolSearch call:

    select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__find,mcp__claude-in-chrome__computer

Then `tabs_context_mcp` with `createIfEmpty: true` and navigate your tab to
the given URL, e.g.
`https://atlaslive.io/f/<org-site>/facility-config/narratives/<version>/instances/<alias>/inputs`.
The user is already logged in; the session cookie is shared.

## Verification is text-first

This is a cost rule and a correctness rule; follow it literally.

- **Verify edits with `get_page_text` or `find`, not screenshots.** After
  typing into a field, read the page text to confirm the new value.
- **Take a screenshot only when**: you need coordinates to click something
  `find` cannot resolve; a gesture appears to have failed and you must see
  the page state; or page text is empty/truncated. Not as a routine
  before/after step, and never "to be sure" about something you already read.
- Pages load lazily. If text is empty or a tab renders blank, wait ~2s and
  re-read once before escalating to a screenshot.

## Creating an instance

Instances list → **Create Instances** → fill alias + description → Narrative
Template dropdown (search by name fragment, e.g. "calculator" → Generic
Calculator System; pick latest version) → Associated Device (search by tag
fragment, e.g. `311BC02`; click the result) → **Create & Open Instance**.

## Drafts vs published configs (check this FIRST)

**A published config is READ-ONLY.** Rows render as a plain table: Add does
nothing, cells do not open editors, dropdowns do not respond to clicks. This
looks exactly like a broken page or a permissions problem — it is neither.
Before concluding any control is unresponsive, check the config selector
(top-right) for a label like "Published Config v2.0.0 (Latest)".

To edit, a DRAFT must exist and be the open config: Narrative Versions page →
create a draft from the published version → work at
`…/narratives/<version>-draft/instances`. Give the draft a meaningful label;
it is user-visible.

Only create a draft if your caller told you to. Otherwise stop and report
that the target config is published.

## Editing member rows (Inputs / Settings / Metrics tabs)

Tabs across the top: Info, Inputs, Settings, Metrics, Conditions, Actions,
Outputs, Alarms. Each tab has locked "Template Defined" rows and editable
"Custom" rows; **Add** appends a row.

- **Name/Description/Default**: click the field; to replace existing text,
  select-all (cmd+a) then type.
- **Type dropdown**: Boolean / Number / Enum / Schedule (+ Sequence for
  settings). Set Type BEFORE Mapping — mapping options are filtered by type.
- **Boolean settings — Normal / One Shot**: when a Setting's Type is set to
  Boolean, the Units column is REPLACED by a dropdown offering `Normal`
  (default) and `One Shot`. It appears only for Boolean settings, and only
  after Type is set — so set Type first, then this. A One Shot setting reads
  true for exactly one scan cycle when pulsed, then self-clears. If the
  change-list says One Shot, verify it still reads `One Shot` after saving.
- **Units dropdown**: search matches the SYMBOL only ("A" works, "ampere"
  does not; "ton/h" works, "tons per hour" does not). If search fails, open
  the dropdown and use the `find` tool on the option's display text, then
  click its ref. Every Number member needs a unit — save fails with
  `"unit" is missing from body` otherwise; use **None** for dimensionless.
- **Input Mapping dropdown**: type ≥2 chars; search by device tag fragment
  (`311bc02`) or point-name fragment (`runstatus`). Number inputs only show
  analog points (e.g. `…_motorCurrent_1`); Boolean inputs show digital points
  (`…_runStatus_1`, `…_runCMD_1`, `…_zeroSpeedStatus`, `…_pullCordStatus`).
  Click the result row to bind.

## Expression editor (Metrics)

Click the Expression cell — a code editor pops up. References are namespaced:
`input.X`, `setting.X`, `metric.X`.

Before replacing an expression, confirm the existing text matches the spec's
OLD value; if it does not, stop and report.

**The editor does not type-check.** It accepts expressions that Validate
later rejects (e.g. mixing bool and number operands). Editor acceptance is
never confirmation that an expression is correct — only Validate is.

To replace: click in, cmd+a, type the NEW text in full, then click outside
the editor to close. Autocomplete appears while typing and is accepted by
CLICKING a suggestion — Tab/Enter do NOT accept, so ignore the popup and keep
typing the full text. Close the editor before saving.

## Saving

Green **Save** bottom-right. A "You have unsaved changes" modal may
interpose — click its Save. Success toast: "Successfully saved narrative
instance". Error toasts are sticky and may linger AFTER a later successful
save — judge by the newest toast. Save one tab at a time.

## Validate

Only if your caller told you to validate — with several executors running,
one agent owns this step.

Instances list page → **Validate**. If the page shows "No Configuration
Open", Validate is disabled — first select the target draft config from the
top-right dropdown. Success dialog: "Draft Successfully Validated … ready to
be published."

**STOP THERE.** That dialog invites publishing as the obvious next step —
dismiss it and do nothing more. Publishing creates a new version number AND
DEPLOYS it to the live facility; it is not a save.

**Do NOT publish unless your caller's prompt explicitly authorizes it in
words.** Silence is not authorization, and neither is a validated draft, a
dialog offering the button, or your own judgment that the change is ready.
If you publish without that explicit authorization you have caused an
uninstructed live deployment — the single worst outcome of this role.

When publishing IS explicitly authorized: the flow has a SECOND confirmation
dialog requiring a release description before it completes. Report the
resulting version number and deploy confirmation.

Note that publishing also deploys everything accumulated in prior published-
but-never-deployed versions, not just your change. Check the Narrative
Versions page's "Last Deployed" column before publishing and tell your caller
if earlier versions were never deployed.

## Report (final message)

Terse and structured; your caller re-reads this on every subsequent turn.
No narration of your process.

    <Instance> / <Tab>: <old> -> <new>        (one line per edit)
    <Instance> / <Metric> expr FINAL: <verbatim text as displayed in the UI>
    SAVES: <tab>: toast yes|no  (per save)
    VALIDATE: <result, or "not run">
    STOPPED: <anything in the spec you did not apply, and why>
    FRICTION: <where these instructions were wrong or missing>
