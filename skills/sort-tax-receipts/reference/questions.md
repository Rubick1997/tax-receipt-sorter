# When to ask, and how

A good question can be answered in a few words by someone looking at one row. Name the thing you are unsure about and, where it helps, offer the likely answers.

- Good: "Who was this lunch with, and was it for work?"
- Good: "This receipt has printer ink (38.99) next to groceries and socks. Is only the ink for the business?"
- Poor: "Please clarify this expense."

Ask one question per row. If several things are unclear, ask about the one that decides the category.

## Checks that always produce `Needs answer`

Still fill in everything you can read, and your best Category if you have one. A `Needs answer` row is not counted until the user approves it, so a blank Business use % is safe.

### Wrong year
The receipt date is outside the tax year in `My situation` B4. The sheet leaves such rows out of the totals by their date.
Question: "Dated 2025-12-28, outside tax year 2026. Was it paid in 2026? If not, set Status to Rejected."

### Likely duplicate
Another row has the same vendor, date and total but a different Source ID, or no Source ID because the user typed it by hand. Add the row anyway, so the file is not read again next time.
Question: "Looks like the same receipt as row 14 (same vendor, date and total). Is this a second purchase? If not, set Status to Rejected."

### Mixed business and personal
The receipt has both kinds of item. Write the receipt total as printed in Unit price and leave Business use % blank.
Question: name the items that look like business, with their printed prices, and ask which ones count.
When the user answers and exactly one line counts, set Business use % to a formula of two printed amounts, such as `=38.99/114.52`, and note that sales tax is not included. If more than one line counts, do not add them up: ask the user to type the business amount into Unit price.

### Equipment
A single item likely to last more than a year that costs more than $2,500, or any item the rules say to treat as equipment. How it is deducted is a decision for the user or their preparer. Items under that amount go to Supplies without a question, unless it is unclear that they are for the business.
Question: "This looks like equipment. Is it only for the business, and do you want it depreciated, expensed under Section 179, or treated as a supply?"

### Not clearly for the business
An item that could be personal or business (a laptop, a phone case, a desk) and no rule says which.
Question: "Is this laptop used only for the business? If it is shared, what share is business?"

### Missing share
The category needs a business share and the setting is blank: phone, internet, car costs.
Question: "What share of this phone plan is for the business? Adding it to My situation will stop this question."

### Rule does not cover it
The meals rule needs a client or travel and the receipt does not show it; a provider is not in the dependent care list; a vendor could be either business or personal.

### Cannot read it
The date, vendor or total is missing or illegible. Leave that cell blank.
Question: "I could not read the total on this receipt. What was it?"

## When not to ask

- A vendor rule or an "always personal" / "always business" entry covers it.
- It is plainly personal (groceries, clothing) and nothing in the rules says otherwise: `Personal (not deductible)`, `Suggested`.
- The same question about the same vendor was already answered in an earlier row. Follow that answer and say so in Notes.
- Earlier rows, including ones the user typed by hand, show how they treat this vendor or kind of item. Follow that pattern and say so in Notes.
