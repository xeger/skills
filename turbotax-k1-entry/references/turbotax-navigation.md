# TurboTax Online navigation

Observed in TurboTax Online 2025 (Premium). Intuit reshuffles the UI between seasons, so treat coordinates as illustrative and locate elements by reading the page.

## Getting to the K-1 interview

Login lands at `myturbotax.intuit.com`, then redirects into a session URL under `*.turbotaxonline.intuit.com/unified/<year>/index/tto?...`. The user signs in; you never enter credentials.

Path: **Federal → Income → Schedule K-1**, then a button per form type:

| Button | Form | Covers |
|---|---|---|
| Partnerships/LLCs | 1065 | partnership and multi-member LLC interests |
| S corporations | 1120S | S-corp shareholders |
| Estates or trusts | 1041 | beneficiaries |

### The flyout quirk

"Income" in the left rail opens a hover flyout rather than navigating. Clicking the label does nothing; clicking the chevron opens the menu, but a direct jump from the chevron to a menu item often fails because the intervening hover events never fire and the menu closes.

What works is hovering through the menu before clicking:

```
click chevron → hover mid-menu → hover near target → click target
```

Batch those four actions together. If the menu still closes without navigating, `find` the menu item and click by ref instead.

The menu also stays open on top of the newly-loaded page. Click empty space to dismiss it before working with the content underneath.

## The prior-year carryover gate

If the taxpayer had K-1s last year, TurboTax will not let you reach the summary screen until you've answered for every carried-over entity, one at a time:

1. **"In 2024 you received a K-1 from X. Did you receive that K-1 in 2025?"** — Yes/No.
2. **"Enter information now, or wait until later?"** — *Work on it Now* / *Wait Until Later*.

Answering **No** discards that entity along with its suspended losses and basis history. Only do that when the user has confirmed the interest genuinely ended. Match candidates by **EIN**, not by name.

**Wait Until Later** is the useful escape hatch: it keeps the entity and its carryovers, creates a stub on the summary screen, and moves on. Use it to defer everything except the K-1 you're working on now.

Once every carryover entity is answered, you reach **Partnership/LLC K-1 Summary** — a table of partnership name / tax ID with Edit and Delete links, plus **Add Another K-1**. This is the hub; everything after the first pass starts here.

## Screen order — partnership (1065) interview

Roughly this sequence. Screens appear or vanish based on earlier answers, so read each screen rather than counting steps.

1. **Review your Information** — carryover name/EIN/address confirmation. "No" opens the edit screen.
2. **Enter Partnership Name and Address** — Part I boxes A and B, plus which spouse the K-1 belongs to.
3. **Choose the Type of Partner** — three consecutive screens: retirement plan (box I2), limited vs general (box G), domestic vs foreign and disregarded entity (boxes H1/H2).
4. **Enter the Percentage of Your Share** — item J, six fields. Not mandatory; doesn't affect the calculation.
5. **Enter Your Liability Share** — item K, six fields.
6. **Enter Capital Account Information** — item L. See the ending-balance note below.
7. **Describe the Partnership** — PTP, foreign, ended in 2025, partial disposal, amended K-1, or none.
8. **Choose Type of Activity** — which of boxes 1 / 2 / 3 carries the income, plus a checkbox if more than one does.
9. **Real Estate Professional / material participation** — *judgment call, escalate.*
10. **Special Handling of Rental Activities** — *judgment call, escalate.* Applies to land rentals and self-rentals.
11. **Enter Box 2 Info** (or box 1 / box 3) — the primary income figure, with last year's shown alongside.
12. **Check boxes that have an amount** — a checklist gating which detail screens you'll see. Boxes 4–7 and 8–10 are grouped; 11 through 21 are individual.
13. **Detail screens** for each box you checked, in order.
14. **Describe the Partnership** (second one) — supplemental expenses, passive loss carryovers from last year, at-risk status, at-risk carryovers, health insurance.
15. **Report Carryovers – Regular Tax**, then **Any Other Carryovers?**, then the same pair again for **AMT**.
16. **Any QBI Carryovers?**
17. **199A screens** — source of the QBI, then Statement A detail, then uncommon adjustments, then the taxable-income threshold question.
18. Back to the carryover gate for the next entity, or to the summary.

## UI behaviours worth knowing

**Item L ending balance is not computed.** After you fill beginning, income, other, and withdrawals, the ending field still holds the prior-year figure. Set it explicitly.

**Box 20 grows a row at a time.** Three code/amount rows initially; filling the last one appends a blank. `find` the new refs rather than guessing coordinates.

**Checkboxes reflow the page.** Checking a box expands sub-fields and pushes everything below it down. Screenshot between checkbox clicks.

**Screen labels go stale after a rename.** Corrected names may not propagate to later screens in the same session. Trust the summary screen.

**Header figures update live.** The federal refund and state balance-due in the header recalculate as you enter. Watching them move is a free sanity check that data is actually saving — and if they don't move at all after entering income, something didn't take.

## Verification without re-walking the interview

**Tax tools → Tools → View Tax Summary** shows total income, AGI, QBI deduction, taxable income, and total tax on one screen. Fastest way to confirm the return moved and to check whether taxable income clears the QBI threshold.

**Tax tools → Tools → Preview my 1040** renders the 1040 worksheet, but the amounts sit in separate elements that `get_page_text` doesn't pick up — you have to screenshot and read. Use the tax summary first.

Note that the QBI deduction often shows as zero until every business income source is entered, because QBI nets across all of them. Don't chase it mid-stream; check it after the last K-1.
