# Entry record template

Write one per K-1, into the user's folder alongside the source PDFs. Name it `K1-<short-entity>-entry-record.md`.

Why this exists: next year someone — the user, their preparer, or a future agent — will need to know what was entered and why. The transcription tables make the entry auditable; the open-flags section is what actually gets read. Put real effort there and keep the rest mechanical.

Drop any section that doesn't apply. Don't pad with "N/A" rows.

---

```markdown
# <Partnership name> — <year> Schedule K-1 entry record

Source: `<filename>` (<n> pages<, includes Schedule K-3>)
Entered in: TurboTax Online <year> → Federal → Income → Schedule K-1 → <form type>
Date: <YYYY-MM-DD>

## Entity / partner

| Field | K-1 | Entered |
|---|---|---|
| Partnership name | | |
| EIN | | |
| Address | | |
| Partner type (G) | | |
| Domestic/foreign (H1) | | |
| Disregarded entity (H2) | | |
| Retirement plan (I2) | | |
| PTP (D) | | |
| Profit / Loss / Capital (J) | | |

## Item K — liabilities

| | Beginning | Ending |
|---|---|---|
| Nonrecourse | | |
| Qualified nonrecourse | | |
| Recourse | | |

## Item L — capital account

| Line | Amount |
|---|---|
| Beginning capital | |
| Contributed | |
| Current year net income | |
| Other increase (decrease) | |
| Withdrawals & distributions | |
| **Ending capital** | **** ✓ ties |

## Part III

| Box | Code | Amount |
|---|---|---|

## Statement A — QBI

| Item | Amount |
|---|---|

## Interview answers requiring judgment

| Question | Answer | Basis |
|---|---|---|

## Open flags — need review

<Numbered. For each: what the discrepancy is, both figures, what you did, what would resolve it,
and what the exposure is if it's wrong. A flag the reader can't act on isn't worth writing.>

---

*Not tax advice. Figures transcribed from the source PDF; judgment calls above were confirmed
with <user> during entry.*
```

---

## On the flags section

The difference between a useful flag and noise is whether the reader can act on it. Compare:

> Opening capital account didn't match.

against:

> **$1,154 opening capital account gap.** TurboTax pre-filled 2025 opening capital of **38,492** (2024 ending); the 2025 K-1 reports **37,338**. Entered the K-1 figure. Check whether last year's ending capital was mis-entered or the partnership restated. Item L is informational and doesn't affect the current-year calculation, so the exposure is to next year's rollforward rather than this year's tax.

The second tells the reader what to pull, what to compare, and how much it matters. That last part earns its keep — it's what lets someone triage five flags in thirty seconds.

## Multiple K-1s

When several are entered in one session, write one record per K-1 plus a short index listing each entity, its EIN, its source file, and its flag count. The index is what the user opens first.
