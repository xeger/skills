# K-1 (Form 1065) box → TurboTax mapping

Where each box on the form lands in the interview, and what to watch for.

## Contents

- [Part I — partnership](#part-i--partnership)
- [Part II — partner](#part-ii--partner)
- [Items J, K, L](#items-j-k-l)
- [Part III — income, deductions, credits](#part-iii--income-deductions-credits)
- [Box 20 codes](#box-20-codes)
- [Statement A — QBI](#statement-a--qbi)
- [Schedule K-3](#schedule-k-3)

---

## Part I — partnership

| Box | Screen | Field |
|---|---|---|
| A | Enter Partnership Name and Address | Partnership/LLC ID Number |
| B | same | Name, Address, City, State, ZIP |
| C | not collected | — |
| D (PTP) | Describe the Partnership | "This is a publicly traded partnership" |

A checked box D routes the K-1 through separate PTP handling — PTP losses are suspended per-partnership rather than pooled, so this checkbox has real consequences. Don't miss it.

## Part II — partner

| Box | Screen | Field |
|---|---|---|
| E | **never enter** | SSN/TIN — hand to the user |
| F | Enter Partnership Name and Address | "This K-1 is for" (taxpayer / spouse / both) |
| G | Choose the Type of Partner | Limited Partner or Other LLC Member / General Partner or LLC Manager |
| H1 | Choose the Type of Partner | Domestic Partner / Foreign Partner |
| H2 | Choose the Type of Partner | "Disregarded Entity" checkbox |
| I1 | not collected directly | — |
| I2 | Choose the Type of Partner | "My K-1 indicates that the partner is a retirement plan" |

Box F drives which spouse's name the activity attaches to on Schedule E. When a K-1 is issued to a jointly-held revocable trust, "Both of Us" is usually right, but it's the user's call — check what prior years used.

## Items J, K, L

**J — profit/loss/capital percentages.** Six fields, beginning and ending. TurboTax states outright that this is optional and doesn't affect the calculation. Enter it anyway; it's what makes the entry auditable against the form.

**K — liabilities.** Six fields across nonrecourse, qualified nonrecourse, and recourse. Only *ending nonrecourse* is mandatory. Qualified nonrecourse financing matters for at-risk purposes on real estate — a partner is generally treated as at-risk for their share of it, which is why a rental LP with qualified nonrecourse debt can still be fully at-risk despite little cash invested.

**L — capital account.** Six fields:

| Form line | Field |
|---|---|
| Beginning capital account | Opening Capital Account |
| Capital contributed during the year | Capital Contributed During \<year\> |
| Current year net income (loss) | Current Year Net Income (Loss) |
| Other increase (decrease) | Other Increase (Decrease) — negative for a decrease |
| Withdrawals and distributions | Withdrawals and Distributions — enter as negative |
| Ending capital account | Ending Capital Account |

Two traps. The opening balance is pre-filled from last year and frequently disagrees with the K-1 — enter the K-1 figure and flag the gap. And the ending balance does not recompute; set it explicitly and confirm the column ties.

## Part III — income, deductions, credits

Before the detail screens, a checklist screen — **"Check boxes that have an amount or are checked on the form"** — gates what you'll be asked. Check only what actually carries an amount; each check adds screens.

Grouping on that checklist: `Boxes 4 to 7`, `Boxes 8 to 10`, then `Box 11` through `Box 21` individually.

| Box | Screen | Notes |
|---|---|---|
| 1 | Enter Box 1 Info | ordinary business income; shows prior year alongside |
| 2 | Enter Box 2 Info | net rental real estate |
| 3 | Enter Box 3 Info | other net rental |
| 4a–7 | Enter Information from Boxes 4 – 7 | guaranteed payments, interest, dividends, royalties. Also has two "Interest from U.S. Obligations" lines for state-exempt portions — leave blank unless the K-1 breaks it out |
| 8–10 | Enter Information from Boxes 8 – 10 | capital gains, 1231 |
| 11 | code + amount rows | other income |
| 12 | single amount | section 179 |
| 13 | code + amount rows | other deductions |
| 14 | code + amount rows | self-employment earnings |
| 15 | code + amount rows | credits |
| 16 | yes/no | Schedule K-3 — see below |
| 17 | code + amount rows | AMT items |
| 18 | code + amount rows | A tax-exempt interest, B other tax-exempt, C nondeductible expenses |
| 19 | code + amount rows | A cash/marketable securities, B section 737, C other property, D deemed money, F/G for services |
| 20 | code + amount rows | see below |
| 21 | amount | foreign taxes paid or accrued |

Boxes 1, 2, and 3 are mutually exclusive as the *primary* activity — the "Choose Type of Activity" screen picks one, with a checkbox if the K-1 reports amounts in more than one.

### Box 16 and Schedule K-3

Answering **Yes** opens the Form 1116 foreign-tax-credit interview. Before answering, look at the attached K-3: if Part II shows all income in the U.S.-source column (a), no foreign-source columns carry amounts, and box 21 is blank, then there is no foreign tax to credit and the interview produces an empty form.

Intuit publishes guidance covering this case, and the screen itself links to "What if my Schedule K-3 has no foreign income or taxes?" Answering No is a documented workaround, not a fabrication — but it does deviate from what the checkbox literally says, so present both options to the user rather than choosing.

## Box 20 codes

TurboTax's dropdown labels differ from the K-1's own captions in places. Notable ones:

| Code | TurboTax label | Note |
|---|---|---|
| A | Investment income | |
| B | Investment expenses | |
| N | Business interest expense | informational for most individual returns; TurboTax says so on a follow-up screen |
| Y | Net investment income | |
| Z | Section 199A information | leave the amount blank — the detail goes on the Statement A screens |
| AE | Excess taxable income | |
| AG | Gross receipts for section 448(c) | |
| **AJ** | **Excess business loss limitation** | the K-1 captions this "aggregate business activity gross income / total deductions." Same code. TurboTax accepts one amount — enter gross income and note the deductions figure in the entry record |
| AO | PTP information | |
| ZZ | Other | |

The list is long; use `read_page` to pull the actual `option` values rather than scrolling.

Rows grow one at a time — the form starts with three and appends a blank each time you fill the last.

## Statement A — QBI

Reached via box 20 code Z. The flow:

1. **"Is the business that generated the Section 199A income a separate business owned by the partnership?"** — Statement A is headed with the entity's name; if that's the same partnership that issued the K-1, choose "The income comes from the partnership that generated this K-1."
2. **"We need some information about your 199A income"** — a checklist, each item expanding into fields:
   - business income (loss) → ordinary / rental / royalty / other income
   - 1231 gain (loss)
   - section 179 deductions
   - other deductions
   - W-2 wages
   - UBIA of qualified property
   - REIT dividends
3. **"Let's check for some uncommon adjustments"** — usually "None of these apply."
4. **Taxable-income threshold question** — whether income might exceed the year's 199A phase-in threshold. Check the tax summary if unsure; if all Statement A fields are already entered, the answer doesn't change the outcome.

Statement A's rental income figure often differs slightly from box 2 (box 2 may include a rounding or special-allocation line). Enter each where it belongs; don't reconcile them to each other.

## Schedule K-3

Box E of the K-3 lists which Parts apply. For a domestic partnership with no foreign operations, typically only Parts II and III, and everything sits in the U.S.-source column.

Fastest check on the extracted text:

```bash
pdftotext -layout k1.pdf - | grep -A30 "Part II   Foreign Tax Credit Limitation"
```

If every populated line falls under "(a) U.S. source" and the foreign-source columns are empty, there is no foreign activity to report.
