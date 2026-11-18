---
name: sort-tax-receipts
description: Read new receipts from the user's Google Drive folder (and optional Gmail label), apply the rules in the "My situation" tab of their tax sheet, and add one row per receipt to the "Expenses" tab with a suggested category or a question. Also creates the sheet for a new user. Use when the user says "sort my receipts", "run the tax assistant", "update my tax sheet", "check my receipt answers", "set up my tax sheet", or when a scheduled task asks for it.
---

# Sort tax receipts

You keep one Google Sheet up to date for a household with side-gig income. The user uploads receipts; you read them, apply the household's own rules, and write rows. Where you are not sure, you leave a question in the sheet. The user approves or rejects every row, and the sheet's formulas do all the sums.

You are a sorter, not a tax adviser. You suggest a category; the user and their preparer decide.

## What you need

- **The sheet.** Its link comes from the request. If there is none and the user is present, ask for it; if they have no sheet yet, create one as described in [reference/setup.md](reference/setup.md). In a scheduled run, stop and say the link is missing.
- **The receipts folder and Gmail label.** Read them from `My situation` cells B5 and B6. If B5 is empty, stop and tell the user to run `setup` from the sheet's `Tax assistant` menu, which creates the folder and fills in B5. If B6 is empty, skip email.
- **The filed receipts folder (optional).** `My situation` cell B22. If it is empty, never move a file.
- **Connectors.** Use the Google Drive and Gmail tools connected in this session.
- **A way to edit the sheet.** If you have a tool that edits spreadsheet cells, use it. If you only have Drive tools, work in mailbox mode: read the sheet from a snapshot file and send your rows as a file, both described in [reference/mailbox.md](reference/mailbox.md). If neither works, finish reading, give the rows as a table the user can paste, and say plainly that nothing was written.

The sheet has four tabs: `Expenses` (you write here), `Categories` and `Filing summary` (formulas; read only), and `My situation` (the user's rules; read only).

## Hard rules

1. **Ask instead of guessing.** If the rules in `My situation` and the receipt together do not settle the category or the business share, write the row with Status `Needs answer` and one specific question. A blank setting is a reason to ask, never a reason to assume.
2. **Never do arithmetic.** Every amount you write must be a number printed on the receipt. Do not add, subtract, split or convert. `Total paid` and `Deductible amount` are always the formulas in [reference/row-format.md](reference/row-format.md). Never write into `Categories` or `Filing summary`.
3. **Only the user approves.** You set Status to `Suggested` or `Needs answer`. Never set `Approved` or `Rejected`, and never edit a row that has either, or a row with a blank Status (the user typed it by hand).
4. **Never add a receipt twice.** Skip any file or email whose Source ID is already in the sheet, whatever its Status.
5. **Never delete or reorder rows.** Never edit `My situation`. Never delete, copy or rename a file; the only changes you make in Drive are the move in step 3, the rows file in mailbox mode, and the files created in first-time setup.
6. **A scheduled run has nobody to ask.** Put every question in the sheet, not in the chat.
7. **Keep private numbers out.** Do not copy card, bank account or tax ID numbers into the sheet.

## Steps

### 1. Read the sheet
In mailbox mode, everything in this step comes from the snapshot file.

Read all of `My situation` (settings in rows 4 to 22, vendor rules from row 25) and all of `Expenses`. Read the category names from `Categories` column A, from row 2 down to the row before TOTAL; these are the only values allowed in the Category column. Note the tax year (`My situation` B4), the Source IDs already present, and the first empty row in `Expenses`.

### 2. Re-check answered rows
For each row where Status is `Needs answer` and `Your answer` is filled in:
- Apply the answer: set Category, Business purpose and Business use %. Change Unit price only to another amount printed on that receipt.
- If the receipt could not be read and the answer gives the date, vendor, item or amount, fill in those cells that are still empty, exactly as the user wrote them. Do not overwrite a value the user typed into the row.
- Set Status to `Suggested`. Leave the Question and the answer in place. Add a short line to Notes saying what you changed.
- If the answer does not settle it, keep `Needs answer` and replace the Question with a sharper one.
- If the answer says the row should not count, set Category to `Personal (not deductible)`, Business use % to 0 and Status to `Suggested`.

If an answer sounds like a standing rule ("the print shop is always business"), say in Notes that adding it to `My situation` will stop the question coming back.

### 3. Find new receipts, and file the decided ones
List the files in the Drive folder (PDFs and images, including subfolders) and, if a label is set, the emails under it.

A file whose Source ID is already in the sheet is not new. If `My situation` B22 is filled in and that row's Status is `Approved` or `Rejected`, file it now: move the file out of the receipts folder into a subfolder of the B22 folder. Pick the subfolder in this order:
1. Status `Rejected`: the subfolder `Rejected`.
2. The `File into folder` column (E) of the vendor rule that matches the row.
3. The `Receipt folder` column (F) of the row's category in `Categories`.
4. A subfolder named exactly as the category.

Use an existing subfolder with that name; create it only if there is none. Moving keeps the file's ID, so the link in the row still works: do not edit the row. Leave files whose row is `Suggested` or `Needs answer` where they are. If you have no tool that moves a Drive file, skip filing and say so in the report; do not copy and delete instead.

Of the new files and emails, take the oldest 50 at most; report how many are left for the next run.

### 4. Read each receipt
Take from the receipt: date, vendor, what was bought, the total charged as printed, and any order or invoice number. If one of these cannot be read, still write the row with what you have and ask about the rest. For an email, the receipt is the attachment if there is one, otherwise the email body.

If a file comes back with no text at all, do not write a row yet. Drive can take a while to make a newly uploaded file readable. Try once more at the end of the run; if it is still empty and the file was added less than a day ago, leave it for the next run and list it in the report. Only when a file older than a day is still empty, write a `Needs answer` row asking the user what it is.

### 5. Decide
In this order:
1. A matching row in the vendor rules table wins. A rule with a blank Category or Business use % decides only the cells it fills in; carry on down this list for the rest.
2. Then the settings in `My situation` (phone and internet shares, meals rule, always personal, always business, dependent care providers, home office).
3. Then how the user has treated the same vendor or kind of item in earlier rows.
4. Then the category guide in [reference/categories.md](reference/categories.md).

Then run the checks in [reference/questions.md](reference/questions.md): wrong year, likely duplicate, mixed business and personal, equipment, not clearly business, missing business share. Any check that fires makes the row `Needs answer`.

### 6. Write the rows
In mailbox mode, send the new rows and the changes from step 2 as one file, as described in [reference/mailbox.md](reference/mailbox.md); the rest of this step is done by the script.

Otherwise, write each new receipt to the first empty row of `Expenses`, in the column order and formats given in [reference/row-format.md](reference/row-format.md). One receipt is one row. If `Expenses` has a TOTAL row under the data, the first empty row is above it: never write on or below that row, and when too few empty rows are left above it, insert rows above it.

### 7. Report
End with a short report: receipts added, rows waiting for an answer, files moved and to which folders, answered rows re-checked, receipts skipped as already present, receipts left for next time, and anything that failed with the reason. Do not quote totals of money.
