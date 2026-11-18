# Row format for the `Expenses` tab

Row 1 holds the headers. Write one row per receipt, starting at the first empty row. Find columns by their header text, not by letter, in case the user has moved one.

| Col | Header | What to write |
|---|---|---|
| A | Date | Date on the receipt, as a date. |
| B | Item / description | What was bought, in a few words. |
| C | Vendor | Vendor name as printed, without store numbers. |
| D | Category | Exactly one name from `Categories` column A. |
| E | Business purpose | Why this is a business cost, in one plain sentence, based on `My situation`. Blank when that is the question, and for personal rows. |
| F | Qty | `1`. |
| G | Unit price | The total charged, as printed, as a plain number: `48.17`. |
| H | Total paid | Always the formula below. |
| I | Business use % | Blank means 100%. Otherwise a share: `0.4` for 40%, `0` for personal, or a formula of two printed amounts (see below). |
| J | Deductible amount | Always the formula below. |
| K | Receipt (link or image) | The Drive file as a link (file name as the text), or the email subject. |
| L | Notes | Order or invoice number, which rule you used, anything the preparer should know. No card or account numbers. |
| M | Status | `Suggested` or `Needs answer`. |
| N | Question | One specific question when Status is `Needs answer`. Otherwise blank. |
| O | Your answer | Leave blank. The user writes here. |
| P | Source ID | `drive:<file id>` or `gmail:<message id>`. |

If the sheet has no Status, Question, Your answer or Source ID column yet, add those four headers after the last used column before writing anything.

Rows the user typed by hand have a blank Status. They count as approved. Leave them alone.

## Formulas

For a row written at row `n` (here row 12):

Total paid:
```
=IF(G12="","",IF(F12="",1,F12)*G12)
```

Deductible amount (the 50% meals limit is applied here):
```
=IF(H12="","",H12*IF(I12="",1,I12)*IF(D12="Meals (50%)",1/2,1))
```

Write formulas as user-entered input so the sheet treats them as formulas. Match the sheet's locale: if the formulas already in the sheet use `;` between arguments and `,` for decimals, write yours the same way. If the sheet already has a formula in these columns on earlier rows, copy its pattern.

## Business use % as a formula

When only part of a receipt is for the business and the receipt prints both amounts, let the sheet do the division. For printer ink at 38.99 on a receipt totalling 114.52:

```
=38.99/114.52
```

Both numbers must be printed on the receipt. Never type a share you worked out yourself.

## Example rows

| Date | Item / description | Vendor | Category | Business purpose | Qty | Unit price | Business use % | Status | Question | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-03-02 | Pro plan, monthly | Inkwell Cloud | Software & subscriptions | Design software for illustration work | 1 | 22.99 | | Suggested | | Invoice INV-20418. Vendor rule: Inkwell. |
| 2026-03-18 | Unlimited plan, March | Northline Mobile | Phone & internet | Mobile plan used partly for client calls | 1 | 85.00 | 0.4 | Suggested | | Vendor rule: Northline, 40%. |
| 2026-03-14 | Lunch for 2, coffee | The Copper Kettle | Meals (50%) | | 1 | 64.30 | | Needs answer | Who was this lunch with, and was it for work? | Meals rule needs a client or overnight travel; the receipt does not say. |
