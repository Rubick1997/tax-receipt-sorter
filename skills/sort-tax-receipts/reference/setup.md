# First-time setup: creating the sheet

Use this when the user asks to set up the tax sheet, or asks to sort receipts and has no sheet yet. Only run it when the user is present; never in a scheduled run. Do not run it if the user already gave a sheet link.

The sheet ships with this skill as `assets/tax-receipt-sorter-template.xlsx`, with its four tabs, formulas and dropdowns.

## Steps

1. **Ask before creating anything.** Say that you will create one folder in their Google Drive with a sheet and a receipts folder in it, and wait for a yes. Ask which tax year it is for if they have not said.
2. **Create the folder.** In the top level of their Drive, create a folder named `Tax receipts <year>`. If a folder with that name already exists, ask whether to use it.
3. **Upload the sheet.** Upload `assets/tax-receipt-sorter-template.xlsx` into that folder with the Drive tool, as an Excel file that Drive converts to a Google Sheet (do not turn conversion off). Name it `Tax sheet <year>`. Upload the file's own bytes; never retype or rebuild the sheet from its contents.
4. **Check it.** Read the new file. It must be a Google Sheet with the tabs `Expenses`, `Filing summary`, `Categories` and `My situation`. If it is not, say so and go to "If the upload does not work".
5. **Create the receipts folder.** In the same folder, create a folder named `Receipts inbox`.
6. **Fill in two cells.** With the Google Sheets tools, write the tax year into `My situation` B4 and the link to `Receipts inbox` into B5. These are the only cells of `My situation` you write. If you have no Google Sheets tools, give the user the folder link and ask them to paste it into B5.
7. **Hand over.** Give the user the links to the sheet and to `Receipts inbox`, and these steps:
   1. Open the sheet. In `My situation`, answer what you can. Blank answers are fine: I will ask.
   2. Upload receipts to `Receipts inbox`, then say "sort my receipts".
   3. To have it run by itself, create a weekly scheduled task with the prompt "Sort my receipts into this sheet: (sheet link)".

Do not answer anything else in `My situation` yourself, and do not guess.

## If the upload does not work

If you cannot upload the template's bytes with the tools you have, do not try to recreate the sheet another way. Give the user the file from `assets/` and these steps instead:

1. Upload `tax-receipt-sorter-template.xlsx` to Google Drive, open it, and choose File > Save as Google Sheets.
2. Create a folder for receipts and paste its link into `My situation` B5.
3. Come back with the sheet link and say "sort my receipts".

Say plainly which parts you did and which parts are left to them.
