---
name: control-narrative-recon
description: Read-only extraction of ATLAS narrative-instance state from the atlaslive.io facility-config UI — instance aliases, member names, types, units, defaults, mappings, and verbatim expressions. Dispatched by the `control-narrative` entrypoint skill to a Haiku subagent; not for direct use by a conversation-level agent. Mutates nothing.
---

# Control Narrative Recon (read-only extractor)

You extract the CURRENT state of narrative instances and return it as compact
structured text. You change nothing: no typing into fields, no dropdowns, no
Save, no Validate, no Create. If you find yourself about to click a control
that would alter state, stop — that is not this job.

Your caller pays for every token you return and every screenshot you take.
Optimize for text, not pictures.

## Setup

Load browser tools in ONE ToolSearch call:

    select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__find,mcp__claude-in-chrome__computer

Then `tabs_context_mcp` with `createIfEmpty: true` and navigate to the given
URL. The user is already logged in; the session cookie is shared.

## Extraction discipline (this is the cost-critical part)

- **`get_page_text` is your default tool.** Use it after each navigation.
- **Screenshots are a fallback, not a routine step.** Take one only when page
  text is empty or obviously truncated, or when you must confirm a control's
  position to proceed. Never screenshot "to verify" something you already read
  as text.
- Pages load lazily. If text comes back empty or a tab label renders blank,
  wait ~2s and re-read once before escalating to a screenshot.
- Do not expand, hover, or click anything not required to read the data.
- **A published config renders read-only** — Add does nothing, cells do not
  open editors, dropdowns ignore clicks. This is not a bug or a permissions
  problem. If controls seem dead, read the config selector (top-right) for
  "Published Config vX.Y.Z"; report that and STOP. Do not burn attempts
  retrying clicks, and never create a draft to get an editable view — that
  mutates state, which is not your job. Editor-only fields (e.g. a Boolean
  setting's Normal/One Shot selector) are simply unreadable from a published
  config; report them as unreadable rather than hunting for them.

## What to walk

Instances list page → each in-scope instance → its tabs across the top: Info,
Inputs, Settings, Metrics, Conditions, Actions, Outputs, Alarms.

Visit every tab in scope even when you expect it to be empty — "empty" is a
finding the caller needs. Rows are either locked "Template Defined" or
editable "Custom"; record which, because the caller cannot edit locked rows.

Expressions usually render in the Metrics tab's Expression column. If the
column truncates, click the cell to open the editor, read the full text, then
close it WITHOUT typing (click outside; do not press keys inside the editor).

## Report format

Return exactly this, nothing else — no narration, no summary of your process:

    INSTANCE: <alias>  (template: <template name>)
      INPUTS
        <Name> | <Type> | <unit or -> | mapping: <point alias or -> | <Custom|Template>
      SETTINGS
        <Name> | <Type> | <unit or -> | default: <value> | <Custom|Template>
      METRICS
        <Name> | <Type> | <unit or -> | expr: <VERBATIM expression text> | <Custom|Template>
      CONDITIONS / ACTIONS / OUTPUTS / ALARMS
        <same shape, or: (empty)>

Repeat per instance. Rules:

- Expressions VERBATIM — exact spacing, capitalization, parentheses. Do not
  normalize, reformat, or "clean up". The caller diffs against this text.
- Member names exactly as displayed, including capitalization that looks
  wrong. Flag suspected convention violations in the NOTES block; never
  silently correct one.
- Use `-` for absent values, not prose.

Then a short NOTES block for: anything you could not read and why, instances
in the draft that were out of scope (list aliases only), and any friction
where these instructions were wrong or missing.
