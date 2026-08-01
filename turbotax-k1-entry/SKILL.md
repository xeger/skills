---
name: turbotax-k1-entry
description: Enter Schedule K-1 (Form 1065/1120S/1041) data into TurboTax Online through the browser, driven by cheap subagents. Use this skill whenever the user wants help getting K-1s into TurboTax, mentions K-1 PDFs from partnerships, LLCs, S-corps or trusts alongside tax software, asks about partnership income on their return, or has a folder of K-1s to work through — even if they don't say "TurboTax" by name or frame it as data entry. Also use it when the user asks why a K-1 amount isn't flowing correctly, or wants prior-year carryover figures checked against a current-year K-1.
---

# TurboTax K-1 entry

## What this skill is for

Getting Schedule K-1 data out of PDFs and into TurboTax Online accurately, fast, and cheaply. A typical taxpayer with a handful of partnership interests has 3–8 K-1s, each of which takes 20–30 browser screens. Doing that inline with an expensive orchestrator model is slow and wasteful; almost all of the work is mechanical.

The core idea: **the orchestrator does judgment, subagents do labor.** You (the orchestrator) never read a whole K-1 PDF into your own context and never click through the routine interview screens yourself. You dispatch that work to cheap models and spend your own tokens on the handful of decisions that actually require care.

## Model assignment

This split is the point of the skill. Respect it or the economics collapse.

| Work | Model | Why |
|---|---|---|
| PDF → structured JSON | **Haiku** | Pure extraction from machine-readable text. Parallelizable across every K-1 at once. No browser, no state. |
| Driving the TurboTax interview | **Sonnet** | Needs coordinate clicking, screenshot reading, and recovery when a screen doesn't match expectation. Haiku misclicks and loses the thread; Opus is overkill for "type 3311, click Continue." |
| Judgment calls, anomalies, talking to the user | **You (orchestrator)** | Carryover mismatches, passive-activity questions, anything where a wrong answer changes the tax. |

Spawn with the `model` parameter on the Agent tool: `model: "haiku"` for extraction, `model: "sonnet"` for browser work.

## Hard constraints

**One browser, one driver.** All browser subagents share a single Chrome tab. Never run two browser subagents concurrently — they will fight over the tab and corrupt each other's state. Extraction subagents are safe to parallelize because they touch no browser.

**Never type an SSN or TIN.** K-1s contain the taxpayer's Social Security number in Part II box E, and it appears again on any attached Schedule K-3. Extraction agents must redact it and browser agents must never enter it. If TurboTax asks for an SSN, stop and hand the keyboard to the user. Partnership EINs are fine — those are business identifiers, not the user's government ID.

**The K-1 is the authority, not the carryover.** TurboTax pre-fills fields from last year's return. When a pre-filled figure disagrees with the current-year K-1, enter the K-1 figure and flag the discrepancy — don't silently accept either one. These mismatches are how prior-year errors get caught.

**Escalate, don't guess.** Any screen asking about the taxpayer's own conduct or circumstances (material participation, hours worked, whether they disposed of an interest) is not derivable from the PDF. Subagents must stop and report; you ask the user.

## Workflow

### 1. Inventory and confirm scope

Run the triage script over the folder:

```bash
python <skill_path>/scripts/k1_scan.py ~/Downloads
```

It reports every K-1 with its entity name, EIN, page count, whether it's a final or amended K-1, whether a Schedule K-3 is attached with foreign activity, and which files are byte-identical duplicates. Downloading a K-1 twice is common and produces pairs like `Brown Deer.pdf` and `Brown Deer-1.pdf`; entering both would double the income.

Two things in that output change the plan if present:

- **Final K-1** means the interest terminated during the year. That's a disposition — it releases suspended passive losses and usually produces a capital gain or loss that needs the sale details, which aren't on the K-1. Raise it with the user before entering.
- **Amended K-1** means whatever was entered before is superseded.

Then ask the user which K-1s to process and in what order. Start with one end-to-end before batching, so they can sanity-check your interpretation of the forms before you commit twenty screens' worth of entry.

### 2. Extract, in parallel, with Haiku

Spawn one Haiku subagent per K-1 in a single message so they run concurrently. Give each the prompt in `agents/extractor.md` with the file path substituted in. Each writes a JSON file; you read the JSON, not the PDF.

Extraction is cheap enough that it's worth doing for every K-1 up front, even the ones you won't enter today — the JSON is the working record.

### 3. Get to the K-1 interview

Load the Chrome tools, then navigate. See `references/turbotax-navigation.md` for the exact path, the flyout-menu quirk that breaks naive clicking, and how TurboTax's prior-year carryover gate works before it will let you add anything new.

The user signs in themselves. Never enter credentials — if a password manager integration is available, that's the only acceptable path, and only for a sign-in the user asked for.

### 4. Enter one K-1, with Sonnet

Dispatch a Sonnet browser subagent using `agents/browser-driver.md`, handing it the extracted JSON and the answers to any judgment questions you've already resolved with the user. The subagent works one K-1 to completion, then reports what it entered plus anything that surprised it.

When it hits a screen it can't answer from the JSON, it stops and returns. You take the question to the user, then dispatch a fresh subagent to resume. Resuming is cheap; guessing is expensive.

### 5. Verify

Don't declare victory off the subagent's own say-so. Check the K-1 summary screen shows the right partnership name and EIN, and watch the refund/balance-due indicators in the TurboTax header move in a direction consistent with the income you entered. If the numbers didn't budge at all after entering a K-1 with income, something didn't save.

Then write the entry record (step 6), which is itself a verification pass — transcribing what you entered back out forces the mismatches into the open.

### 6. Write an entry record

Produce a markdown file per K-1 in the user's folder. This is the deliverable that outlives the session: it's what the user or their preparer reads next year, and it's the audit trail if a number is ever questioned. Use the template in `references/entry-record-template.md`.

The open-flags section matters more than the transcription. A K-1 that went in cleanly needs no explanation; the $1,154 capital-account gap does.

## Judgment calls that recur

These come up on nearly every partnership K-1. Know them cold so you can put a well-framed question to the user instead of a confused one.

**Material participation.** The K-1's own supplemental statement usually labels each activity PASSIVE or NONPASSIVE, and a small limited-partner percentage makes material participation implausible. Cite both when you ask — the user is confirming, not researching.

**Box 16 / Schedule K-3.** If box 16 is checked, TurboTax offers to walk you through Form 1116. Check whether the attached K-3 actually reports foreign-source income or foreign taxes — very often everything sits in the U.S.-source column and box 21 is blank, meaning there is no credit to claim and the Form 1116 interview produces an empty form. Intuit publishes guidance for exactly this case. Present both paths and let the user pick; don't decide unilaterally, because it's a deviation from what the form literally says.

**Passive loss carryovers in the wrong bucket.** TurboTax shows suspended losses split by box (Box 1 ordinary vs Box 2a rental). A carryover parked in the Box 1 column will not offset Box 2 rental income. If the activity is a rental but the carryover sits in Box 1, say so — but don't move it, because you can't see the prior-year Form 8582. Offer to leave it and flag, which risks only another year of suspension, versus moving it, which risks claiming a loss that isn't there.

**Capital account rollforward.** Item L should tie: beginning + contributed + current year income + other increase/(decrease) − withdrawals = ending. TurboTax's ending-capital field may not recalculate on its own; set it explicitly. If the arithmetic doesn't tie on the form itself, that's a partnership error worth telling the user about.

**Entity name typos in carryover data.** Match on EIN, not name. If the EIN matches but the name doesn't, it's the same entity with a prior-year typo — correct the name rather than creating a duplicate entity, because a duplicate orphans the suspended losses and basis history.

## Reference files

- `scripts/k1_scan.py` — folder triage: entities, EINs, duplicates, final/amended flags, K-3 foreign activity. Run first.
- `references/box-mapping.md` — every K-1 box and where it lands in the TurboTax interview, including the box 20 code list and the Statement A / QBI screens. Read before the first browser dispatch.
- `references/turbotax-navigation.md` — menu path, UI quirks, screen-by-screen order of the partnership interview.
- `references/entry-record-template.md` — the output format.
- `agents/extractor.md` — prompt for the Haiku extraction subagent.
- `agents/browser-driver.md` — prompt for the Sonnet browser subagent.

## Scope

Built and tested against **Form 1065** partnership/LLC K-1s in TurboTax Online. S-corp (1120S) and trust (1041) K-1s enter through sibling buttons on the same screen and follow a similar shape, but the box numbering differs — treat the mapping file as partnership-specific and verify against the form in front of you.

This skill handles data entry. It is not tax advice, and it should not be used to decide positions the user hasn't approved.
