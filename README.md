# Tax Receipt Sorter

Drop receipts in one Google Drive folder. On a schedule, Claude reads the new ones, applies your household's own rules, and adds them to your Google Sheet. Where it is not sure, it leaves a question in the sheet instead of guessing. You approve or reject each row, and the sheet adds up what goes on each tax form line.

It is for people with a side gig and a US tax return (Schedule C, Form 8829, Form 2441). It works with Claude: you install a skill in your own Claude account and use your own Google connectors. There is no server, no API key and no account to create.

**This is not tax advice and not a filing tool.** It sorts receipts and suggests categories. You, or your tax preparer, decide what is deductible.

## How it works

1. You upload receipts (PDFs or photos) to a Drive folder, from your phone or computer. Optionally, you put a Gmail label on emailed receipts.
2. Once a week, a Claude scheduled task runs the skill. You can also run it any time by saying "sort my receipts".
3. Each new receipt becomes one row in the `Expenses` tab, with a suggested category, business purpose and business share, or a question.
4. You answer questions in the `Your answer` column and set `Status` to `Approved` or `Rejected`.
5. The next run re-checks the rows you answered. The `Categories` and `Filing summary` tabs update by themselves.
6. Optionally, the next run also files each approved receipt into a folder for its category or vendor, so the upload folder only holds what still needs you.

## Setup

You need a Claude plan that includes skills, connectors and scheduled tasks. Runs count toward your plan's usage limits.

1. **Add the skill.** Download this repository and run `tools/package_skill.sh`, which builds `dist/sort-tax-receipts.zip` from the [`skills/sort-tax-receipts`](skills/sort-tax-receipts) folder. In Claude, open Settings > Capabilities, turn on code execution and file creation, and upload the zip under Skills.
2. **Connect Google.** Turn on the Google Drive and Google Sheets connectors, and Gmail if you want emailed receipts. Drive reads and files the receipts; Sheets lets Claude write the rows.
3. **Create the sheet.** Say "set up my tax sheet". Claude creates a folder in your Drive holding the sheet and a `Receipts inbox` folder, and gives you both links. If Claude cannot upload the sheet, do it by hand: upload [`templates/tax-receipt-sorter-template.xlsx`](templates/tax-receipt-sorter-template.xlsx) to Google Drive, open it, choose File > Save as Google Sheets, and paste the link to a receipts folder into `My situation`.
4. **Fill in `My situation`.** Answer what you can. Blank answers are fine: Claude will ask. See [`templates/situation.example.md`](templates/situation.example.md) for a filled-in example.
5. **Try it.** Upload the files in [`sample-receipts/`](sample-receipts) to `Receipts inbox`, wait a minute or two, and say:
   > Sort my receipts into this sheet: (your sheet link)
6. **Schedule it.** Create a weekly scheduled task with the same sentence as the prompt. A scheduled run puts its questions in the sheet; answer them there, or approve the row, before the next run.

When you are done trying it, delete the sample rows and files.

## How it decides

For each receipt, in this order:

1. Your **vendor rules** ("Inkwell is always software, 100%").
2. Your **settings** (phone business share, when a meal counts, what is always personal).
3. How you treated the same vendor in earlier rows.
4. A built-in [category guide](skills/sort-tax-receipts/reference/categories.md).

If those do not settle it, the row gets `Needs answer` and a specific question. Claude also asks when a receipt:

- is dated outside your tax year,
- looks like a duplicate (same vendor, date and total),
- mixes business and personal items,
- could be personal or business, such as a laptop.

Some things it never does:

- **It never does sums.** Amounts are copied as printed on the receipt. `Total paid`, `Deductible amount` and everything in `Categories` and `Filing summary` are sheet formulas, including the 50% limit on meals.
- **It never approves.** Only you set `Approved` or `Rejected`, and it does not touch those rows again.
- **It never adds a receipt twice.** Each row stores the ID of its source file or email.
- **It never deletes or renames a file.** If you set a filed receipts folder, it moves a file there only after you approve or reject its row.

## The sheet

| Tab | What it is for |
|---|---|
| `Expenses` | One row per receipt: date, item, vendor, category, business purpose, amount, business use %, deductible amount, receipt link, notes. `Status` is `Needs answer`, `Suggested`, `Approved` or `Rejected`. |
| `Filing summary` | Your return, line by line: Schedule C income and expenses, Form 8829 home office (regular and simplified side by side), Form 2441 childcare. Yellow cells are yours to type in. |
| `Categories` | Total paid and deductible total per category, with its Schedule C line. |
| `My situation` | Your rules. Claude reads it on every run and never edits it. |

A row counts when its date is in your tax year and its `Status` is `Approved`. Rows you type in by hand, with no `Status`, count too. The form line numbers follow recent versions of the forms; check them against this year's forms before you file.

## If Claude cannot edit your sheet

The Google Sheets connector edits the sheet from a chat you start yourself. If a scheduled run reports that it could not write to the sheet, or you run Claude somewhere without that connector, install the optional bridge: in your sheet, open Extensions > Apps Script, paste in [`apps-script/Code.gs`](apps-script/Code.gs), save, choose `setup` and press Run (press it again if nothing shows in the log after you allow it). The script runs as you, inside your own Google account. Once an hour it copies the rows Claude left in a `_claude` folder into the sheet, and writes a text copy of the sheet there for Claude to read.

## How it differs

- **From a bookkeeping app:** the rules are yours, in plain words, in a sheet you own. Nothing is stored anywhere else.
- **From asking a chatbot each time:** your rules and past answers stay in the sheet, runs happen on a schedule, and nothing is counted until you approve it.
- **From auto-categorisers:** when it does not know, it asks.

## Privacy

Everything runs inside your own Claude account with your own connectors. This project has no server and never sees your files, your sheet or your credentials. The skill is told not to copy card, bank or tax ID numbers into the sheet.

## Repository

```
skills/sort-tax-receipts/   the skill, its reference files, and a copy of the template
templates/                  sheet template and an example of filled-in rules
sample-receipts/            ten invented receipts, each stamped SAMPLE
apps-script/                optional bridge for when Claude cannot edit the sheet
tools/                      scripts that build the template, the samples and the skill zip
```

To rebuild the template or the samples: `pip install openpyxl reportlab`, then run the scripts in `tools/`. After changing the template, run `tools/sync_skill_assets.sh` to copy it into the skill.

## Licence

MIT. See [LICENSE](LICENSE).

This is an independent project. It is not affiliated with or endorsed by Anthropic or Google.
