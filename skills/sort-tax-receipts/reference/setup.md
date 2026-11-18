# First-time setup: creating the sheet

Use this when the user asks to set up the tax sheet, or asks to sort receipts and has no sheet yet. Only run it when the user is present; never in a scheduled run. Do not run it if the user already gave a sheet link.

Two files ship with this skill, in `assets/`:

- `tax-receipt-sorter-template.xlsx`: the sheet, with its four tabs, formulas and dropdowns.
- `sheet-bridge.txt`: the script the user pastes into the sheet once.

## Steps

1. **Ask before creating anything.** Say that you will create one folder in their Google Drive with a sheet and a text file in it, and wait for a yes. Ask which tax year it is for if they have not said.
2. **Create the folder.** In the top level of their Drive, create a folder named `Tax receipts <year>`. If a folder with that name already exists, ask whether to use it.
3. **Upload the sheet.** Upload `assets/tax-receipt-sorter-template.xlsx` into that folder with the Drive tool, as an Excel file that Drive converts to a Google Sheet (do not turn conversion off). Name it `Tax sheet <year>`. Upload the file's own bytes; never retype or rebuild the sheet from its contents.
4. **Check it.** Read the new file. It must be a Google Sheet with the tabs `Expenses`, `Filing summary`, `Categories` and `My situation`. If it is not, say so and go to "If the upload does not work".
5. **Upload the script text.** Upload `assets/sheet-bridge.txt` into the same folder as a plain text file (conversion off), named `Paste this into Apps Script.txt`.
6. **Hand over.** Give the user the link to the sheet and these steps, in this order:
   1. Open the sheet. In `My situation`, set the tax year and answer what you can. Blank answers are fine: I will ask.
   2. Open `Paste this into Apps Script.txt` and copy all of it.
   3. In the sheet, choose Extensions > Apps Script, replace what is there with the copied text, and save.
   4. Choose `setup` in the toolbar and press Run. Google asks you to allow the script to edit this sheet and use your Drive. It runs as you, inside your own account. After you allow it, press Run once more if the log under the code does not show that it started and finished.
   5. `setup` creates a folder called `Receipts inbox` next to the sheet and fills in its link. Upload receipts there, then say "sort my receipts" with the sheet link.

Do not fill in `My situation` yourself, and do not guess any answer in it.

## If the upload does not work

If you cannot upload the template's bytes with the tools you have, do not try to recreate the sheet another way. Give the user the two files from `assets/` and these steps instead:

1. Upload `tax-receipt-sorter-template.xlsx` to Google Drive, open it, and choose File > Save as Google Sheets.
2. Carry on from step 6.1 above, pasting the contents of `sheet-bridge.txt`.

Say plainly which parts you did and which parts are left to them.
