# Extraction subagent prompt (Haiku)

Spawn one per K-1 PDF, all in the same message so they run in parallel. Substitute the two paths.

---

Extract structured data from a Schedule K-1 PDF. You are doing transcription, not interpretation — accuracy on every digit matters more than speed.

**Input PDF:** `<ABSOLUTE_PATH_TO_PDF>`
**Write JSON to:** `<ABSOLUTE_PATH_TO_OUTPUT_JSON>`

## How to read the file

Use `pdftotext -layout` via bash. The `-layout` flag preserves column positions, which is what makes a K-1 readable as text — without it the boxes interleave into nonsense.

```bash
pdftotext -layout "<PDF>" - | head -200
```

K-1 packages usually run 2–16 pages: the K-1 itself, then supplemental statements, then possibly a Schedule K-3. Read all of it. `pdfinfo` tells you the page count. The supplemental statements carry the detail behind every box marked `STMT`, and that detail is what TurboTax actually asks for.

If `pdftotext` returns little or no text, the PDF is a scan. Say so in your report and stop — don't guess at figures from a garbled OCR layer.

## Do not transcribe the SSN

Part II box E holds the taxpayer's SSN or TIN, and it repeats on any Schedule K-3. Write the literal string `"REDACTED"` in that field. Never put the digits in your JSON, your report, or any file. Partnership EINs (Part I box A) are business identifiers — transcribe those normally.

## Output shape

Write valid JSON matching this structure. Use `null` for boxes that are blank on the form — don't use `0`, because a blank box and a reported zero are different facts and TurboTax treats them differently. Strip commas and dollar signs; losses are negative numbers.

```json
{
  "source_file": "K1, Example Partners.pdf",
  "page_count": 16,
  "form_type": "1065",
  "tax_year": 2025,
  "final_k1": false,
  "amended_k1": false,

  "partnership": {
    "ein": "88-1375379",
    "name": "DCP TPH LLC",
    "address": "300 Colonial Center Pkwy, Ste 100N",
    "city": "Roswell",
    "state": "GA",
    "zip": "30076",
    "irs_center": "E-FILE",
    "is_ptp": false
  },

  "partner": {
    "ssn_or_tin": "REDACTED",
    "name": "TONY SPATARO, TRUSTEE OF THE...",
    "address": "7 Lassen Dr",
    "city": "Santa Barbara",
    "state": "CA",
    "zip": "93111",
    "partner_type": "limited",
    "domestic": true,
    "disregarded_entity": false,
    "entity_type": "INDIVIDUAL",
    "retirement_plan": false
  },

  "shares": {
    "profit_beginning": 1.612903, "profit_ending": 1.612903,
    "loss_beginning": 1.612903,   "loss_ending": 1.612903,
    "capital_beginning": 1.612903,"capital_ending": 1.612903,
    "decrease_due_to_sale_or_exchange": false
  },

  "liabilities": {
    "nonrecourse_beginning": null,             "nonrecourse_ending": null,
    "qualified_nonrecourse_beginning": 80135,  "qualified_nonrecourse_ending": 77866,
    "recourse_beginning": null,                "recourse_ending": null,
    "includes_lower_tier": false,
    "subject_to_guarantees": false
  },

  "capital_account": {
    "beginning": 37338,
    "contributed": null,
    "current_year_net_income": 3342,
    "other_increase_decrease": -6,
    "withdrawals_and_distributions": -3000,
    "ending": 37674,
    "ties": true
  },

  "part_iii": {
    "1_ordinary_business_income": null,
    "2_net_rental_real_estate": 3311,
    "3_other_net_rental": null,
    "4a_guaranteed_payments_services": null,
    "4b_guaranteed_payments_capital": null,
    "4c_total_guaranteed_payments": null,
    "5_interest_income": 31,
    "6a_ordinary_dividends": null,
    "6b_qualified_dividends": null,
    "6c_dividend_equivalents": null,
    "7_royalties": null,
    "8_net_short_term_capital_gain": null,
    "9a_net_long_term_capital_gain": null,
    "9b_collectibles_gain": null,
    "9c_unrecaptured_1250_gain": null,
    "10_net_section_1231": null,
    "11_other_income": [],
    "12_section_179": null,
    "13_other_deductions": [],
    "14_self_employment": [],
    "15_credits": [],
    "16_schedule_k3_attached": true,
    "17_amt_items": [],
    "18_tax_exempt_and_nondeductible": [{"code": "C", "amount": 6}],
    "19_distributions": [{"code": "A", "amount": 3000}],
    "20_other_information": [
      {"code": "A",  "amount": 31,    "note": null},
      {"code": "N",  "amount": 3127,  "note": "business interest expense, Sch K-1 line 2"},
      {"code": "Z",  "amount": null,  "note": "STMT — see qbi_statement_a"},
      {"code": "AJ", "amount": 11006, "note": "aggregate gross income; total deductions 7,703"}
    ],
    "21_foreign_taxes": null,
    "22_more_than_one_activity_at_risk": true,
    "23_more_than_one_activity_passive": true
  },

  "qbi_statement_a": {
    "ordinary_business_income": null,
    "rental_income": 3304,
    "royalty_income": null,
    "section_1231_gain": null,
    "other_income": null,
    "section_179_deduction": null,
    "other_deductions": null,
    "w2_wages": null,
    "ubia_qualified_property": 26941,
    "qualified_reit_dividends": null,
    "is_ptp": false,
    "is_sstb": false,
    "is_aggregated": false
  },

  "rental_activities": [
    {
      "property_type": "4 - COMMERCIAL",
      "description": "Georgia Industrial Portfolio, Stone Mountain, GA 30083",
      "gross_income": 11006,
      "net_expenses": 7702,
      "net_income": 3304,
      "passive_or_nonpassive": "PASSIVE"
    }
  ],

  "schedule_k3": {
    "attached": true,
    "parts_that_apply": ["II", "III"],
    "has_foreign_source_income": false,
    "has_foreign_taxes": false,
    "us_source_total": 11037,
    "foreign_source_total": 0
  },

  "notes": [
    "Box 2 total of 3,311 = 3,304 property net income + 7 rounding/special allocation adjustment.",
    "Item L ties: 37,338 + 3,342 - 6 - 3,000 = 37,674."
  ]
}
```

## Checks to run before you finish

These catch the great majority of transcription errors, and catching them here is far cheaper than catching them after twenty screens of data entry.

- **Item L rollforward.** beginning + contributed + current year income + other increase/(decrease) + withdrawals = ending. Set `capital_account.ties` accordingly and note any break in `notes`.
- **Supplemental detail matches the face of the form.** Where a box shows `STMT`, the statement's total should equal the box amount. Where box 2 shows a total, the rental activity schedule should sum to it (allowing for an explicit rounding line).
- **Schedule K-3, if present.** Determine whether any foreign-source column or foreign tax line carries an amount. This single fact decides whether the user faces a Form 1116 interview, so get it right rather than assuming from the box 16 checkbox alone.

## Report back

Return a short summary — under 200 words. Include: the partnership name and EIN, which Part III boxes carry amounts, whether item L ties, whether the K-3 has foreign activity, and anything ambiguous or unreadable. Do not paste the JSON into your reply; the orchestrator reads the file.
