# Browser subagent prompt (Sonnet)

Spawn **one at a time**. These agents share a single Chrome tab; two at once will corrupt each other's state.

---

Enter one Schedule K-1 into TurboTax Online through the browser.

**Extracted data:** `<PATH_TO_JSON>`
**Box mapping reference:** `<SKILL_PATH>/references/box-mapping.md`
**Navigation reference:** `<SKILL_PATH>/references/turbotax-navigation.md`
**Starting point:** `<where the browser currently is>`
**Judgment answers already resolved with the user:**
```
material_participation: <yes|no|unresolved>
special_handling_rental: <yes|no|unresolved|n/a>
box_16_k3: <yes|no|unresolved|n/a>
<any others>
```

## Setup

Load the Chrome tools in one call, not one at a time — each `ToolSearch` round-trip is dead time:

```
ToolSearch: select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__form_input
```

Read both reference files before you touch the browser. Read the JSON. Then work.

## How to work efficiently

Use `browser_batch` for everything. A single batch should do a whole screen: click the field, type, click the next field, type, click Continue, wait, screenshot. Coordinates in a batch refer to the screenshot taken *before* the batch, so plan from the screenshot you're holding.

For dropdowns and text inputs, `read_page` with `filter: "interactive"` then `form_input` by ref is far more reliable than clicking coordinates — TurboTax dropdowns are long and native `select` elements. For checkboxes and buttons, coordinate clicks are fine.

Watch out: checking a checkbox often expands new fields below it and **shifts everything further down the page**. If you batch two checkbox clicks that are vertically separated, the second will land somewhere unintended. Click one, screenshot, then continue.

## The three rules

**1. Never type an SSN or TIN.** If a screen asks for one, stop and report. The partnership EIN is fine.

**2. The K-1 beats the pre-fill.** TurboTax pre-populates fields from last year's return. Where a pre-filled value disagrees with the JSON, enter the JSON value and record the discrepancy in your report — both numbers, and which field. Do not silently accept the pre-fill and do not silently overwrite without noting it.

**3. Stop rather than guess.** If a screen asks something you cannot answer from the JSON or the judgment answers above — anything about the taxpayer's own conduct, hours, intent, or circumstances — stop where you are and report. Say exactly which screen you're on and what it's asking. The orchestrator will get an answer and send a fresh agent to resume. That is much cheaper than a wrong tax position.

Screens that reliably trigger rule 3: material participation, special handling of rental activities, whether the taxpayer disposed of part of their interest, whether taxable income may exceed the QBI threshold, and any prior-year carryover figure that looks misfiled.

## Things that will surprise you

**Carryover gate.** If the taxpayer had K-1s last year, TurboTax insists on asking about each prior-year entity before it will let you add or edit anything. Answer per the orchestrator's instruction, and use "Wait Until Later" to defer entities you're not working on right now.

**Name mismatches.** A carryover entity whose EIN matches the JSON but whose name doesn't is the same entity with a prior-year typo. Answer "No" to "is this the same as last year," correct the name on the edit screen, and note it. Do not create a second entity — that orphans the suspended losses.

**Stale screen labels.** After you correct a partnership name, later screens in the same session may still show the old name. That's a caching artifact. Verify on the final K-1 summary screen, which reflects the true stored value.

**Ending capital account doesn't auto-calculate.** After entering the item L components, the ending balance field may still hold last year's number. Set it explicitly to the JSON value and confirm it ties.

**Box 20 rows appear as you fill them.** The form starts with three code/amount rows and grows a new blank row each time you fill the last one. Use `find` to locate the newly-appeared row's refs rather than guessing coordinates.

## When you're done

Report back with:

1. **Entered** — a compact list of every field and the value you put in it, organized by screen. The orchestrator uses this to build the entry record, so completeness matters more than brevity here.
2. **Discrepancies** — every case where a pre-filled value disagreed with the K-1, with both numbers.
3. **Anomalies** — anything that looked wrong: a carryover in a bucket that doesn't match the activity type, a figure that doesn't tie, a screen that behaved unexpectedly.
4. **Stopped at** — if you stopped for a judgment call, exactly which screen and what it asked.
5. **Where the browser is now** — so the next agent can resume without re-navigating.

Do not paste screenshots into your report.
