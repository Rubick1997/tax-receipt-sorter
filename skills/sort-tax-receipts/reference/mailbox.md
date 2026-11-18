# Mailbox mode: reading and writing the sheet through Drive

Use this when you have Google Drive tools but no tool that edits spreadsheet cells. A small Apps Script inside the user's sheet does the cell edits. You and the script exchange plain-text files in a folder called `_claude` inside the receipts folder.

| File in `_claude` | Written by | What it is |
|---|---|---|
| `sheet-snapshot.txt` | the script, every hour | The whole sheet as text: settings, vendor rules, categories, every Expenses row, the rows waiting for an answer, and the result of the last import. |
| `rows-YYYYMMDD-HHMM.txt` | you | The rows to add and the rows to change. The script applies it on its next run and moves it to `_claude/done`. |

## Reading

1. Get the receipts folder link from `My situation` B5. Reading the sheet file directly is enough for this, but do not rely on that read for anything else: it may show only the first rows of each tab.
2. Find the `_claude` folder inside the receipts folder and read `sheet-snapshot.txt`. If the folder or the file is missing, stop and tell the user to add the bridge script to the sheet and run `setup` once (after allowing it, Run may need a second press).
3. Check the `written:` line. If the snapshot is more than a day old, say so in the report: the script's timer may be off.
4. Read every `rows-*.txt` still sitting in `_claude` (not in `done`). Those rows are on their way into the sheet. Treat their Source IDs as already present and do not send them again.
5. Your Drive tool may show the text with backslashes added before characters such as `_`, `[` and `=`. They are not part of the file: read `drive:1B\_wAq` as `drive:1B_wAq`.
6. Read the `Last import` section. Report any line that says `failed` or `could not be read`.

Never treat `_claude` or anything in it as a receipt.

## Writing

Create one file per run in `_claude`, named `rows-YYYYMMDD-HHMM.txt`, as plain text (`text/plain`, not converted to a Google Doc). Its content is JSON:

```json
{"version": 1, "rows": [
  {"action": "add",
   "sourceId": "drive:1AbC...",
   "date": "2026-03-21",
   "item": "Printer ink, groceries, kids socks",
   "vendor": "BigMart Superstore",
   "category": "Office expenses",
   "purpose": "",
   "unitPrice": 114.52,
   "businessUse": null,
   "receiptUrl": "https://drive.google.com/file/d/1AbC.../view",
   "receiptName": "05-bigmart.pdf",
   "notes": "Receipt 5501; mixed items",
   "status": "Needs answer",
   "question": "This receipt has printer ink (38.99) next to groceries and socks. Is only the ink for the business?"},
  {"action": "update",
   "sourceId": "drive:1AbC...",
   "businessUse": {"num": 38.99, "den": 114.52},
   "status": "Suggested",
   "notesAppend": "Applied your answer: ink only; sales tax not included"}
]}
```

Fields for `add`:

| Field | Value |
|---|---|
| `sourceId` | Required. `drive:<file id>` or `gmail:<message id>`. |
| `date` | `YYYY-MM-DD`, as printed on the receipt. Leave out if unreadable. |
| `item`, `vendor`, `purpose`, `notes`, `question` | Text. Leave out what you do not have. |
| `category` | Exactly as in the snapshot's Categories list. |
| `qty` | A number. Left out means 1. |
| `unitPrice` | A number printed on the receipt, with a decimal point. Never a sum you worked out. |
| `businessUse` | A share from 0 to 1 (0.4 for 40%); or `{"num": a, "den": b}` where both are amounts printed on the receipt, and the sheet does the division; or `null` for blank. |
| `receiptUrl`, `receiptName` | The file's link and name. |
| `status` | `Suggested` or `Needs answer`. Anything else becomes `Needs answer`. |

Fields for `update`: `sourceId` (required), and only the fields you are changing among `date`, `item`, `vendor`, `qty`, `category`, `purpose`, `unitPrice`, `businessUse`, `question`, `status`, `notesAppend`. The script refuses to change a row whose Status is Approved, Rejected or blank.

The script writes the `Total paid` and `Deductible amount` formulas itself, so there are none in the file.

## What to tell the user

Rows you send appear in the sheet after the script's next run, which is up to an hour later. Say that in the report, and say how many rows you sent. In the sheet, `Tax assistant > Sync now` applies them at once.
