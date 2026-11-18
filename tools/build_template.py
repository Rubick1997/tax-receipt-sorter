"""Build templates/tax-receipt-sorter-template.xlsx.

Upload the result to Google Drive and open it with Google Sheets to get the
sheet template. Needs: pip install openpyxl

Usage: python tools/build_template.py [output.xlsx]
"""

import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

OUT = Path(__file__).resolve().parent.parent / "templates" / "tax-receipt-sorter-template.xlsx"

BOLD = Font(bold=True)
TITLE = Font(bold=True, size=14)
MUTED = Font(color="666666", italic=True)
HEADER_FILL = PatternFill("solid", fgColor="E8EEF7")
INPUT_FILL = PatternFill("solid", fgColor="FFF8E1")
WRAP = Alignment(wrap_text=True, vertical="top")
MONEY = '"$"#,##0.00'

STATUSES = ["Needs answer", "Suggested", "Approved", "Rejected"]
LAST_ROW = 2000

# ---------------------------------------------------------------- Categories
# (category, schedule C line, note). Rows 2-19 make up the Schedule C total.
CATEGORIES = [
    ("Advertising & marketing", "Line 8", "Domains, ads, business cards, portfolio site hosting"),
    ("Car & truck", "Line 9", "Business miles x IRS standard mileage rate, or actual costs. Commuting is not deductible"),
    ("Contract labor", "Line 11", "Freelancers you paid (1099-NEC if $600+)"),
    ("Equipment (depreciation / Sec. 179)", "Line 13", "Computers, monitors, phones over $2,500 per item"),
    ("Insurance", "Line 15", "Business liability insurance (self-employed health insurance goes on Schedule 1 instead)"),
    ("Legal & professional fees", "Line 17", "Accountant, tax prep, lawyer"),
    ("Office expenses", "Line 18", "Postage, printer ink, small office items"),
    ("Rent / lease", "Line 20", "Coworking space, rented equipment"),
    ("Supplies", "Line 22", "Items up to $2,500 each (de minimis safe harbor): keyboard, cables, webcam"),
    ("Taxes & licenses", "Line 23", "Business licenses, permits"),
    ("Travel", "Line 24a", "Flights, hotels, transport on overnight business trips"),
    ("Meals (50%)", "Line 24b", "Business meals; the sheet applies the 50% limit automatically"),
    ("Utilities", "Line 25", "Utilities for a separate business location"),
    ("Phone & internet", "Line 27a", "Enter the business-use % in the Expenses tab"),
    ("Software & subscriptions", "Line 27a", "SaaS, AI tools, cloud hosting, side-project domains"),
    ("Education & training", "Line 27a", "Courses, technical books, conference tickets"),
    ("Home office", "Form 8829 / Line 30", "Items bought for the office room itself. Not counted if you use the simplified method"),
    ("Other", "Line 27a", "Describe in Notes; the IRS wants these itemized"),
]
# Tracked in Expenses, but not part of the Schedule C total.
TRACKED = [
    ("Home shared costs", "Form 8829", "Rent, household utilities, renter's or homeowner's insurance. Filing summary applies the office share"),
    ("Dependent care", "Form 2441", "Daycare, after-school care, day camp. Filing summary shows what you paid"),
    ("Personal (not deductible)", "Not counted", "Kept so the receipt is not read again"),
]
CAT_FIRST = 2
CAT_LAST = CAT_FIRST + len(CATEGORIES) - 1          # 19
TRK_FIRST = CAT_LAST + 1                             # 20
TRK_LAST = TRK_FIRST + len(TRACKED) - 1              # 22
TOTAL_ROW = TRK_LAST + 1                             # 23
CATEGORY_RANGE = f"Categories!$A${CAT_FIRST}:$A${TRK_LAST}"


def cat_row(name):
    names = [c[0] for c in CATEGORIES + TRACKED]
    return CAT_FIRST + names.index(name)


def counted(column, row):
    """Sum an Expenses column for one category: this tax year, approved or hand-entered rows."""
    year = "'My situation'!$B$4"
    base = (
        f"Expenses!${column}:${column},Expenses!$D:$D,$A{row},"
        f'Expenses!$A:$A,">="&DATE({year},1,1),Expenses!$A:$A,"<="&DATE({year},12,31),'
    )
    return f'=SUMIFS({base}Expenses!$M:$M,"Approved")+SUMIFS({base}Expenses!$M:$M,"")'


def build_categories(ws):
    for i, (text, width) in enumerate(
        [("Category", 34), ("Schedule C line", 20), ("Total paid", 14), ("Deductible total", 16), ("Notes", 90),
         ("Receipt folder (optional)", 30)], start=1
    ):
        c = ws.cell(row=1, column=i, value=text)
        c.font, c.fill = BOLD, HEADER_FILL
        ws.column_dimensions[c.column_letter].width = width
    for offset, (name, line, note) in enumerate(CATEGORIES + TRACKED):
        r = CAT_FIRST + offset
        ws[f"A{r}"], ws[f"B{r}"], ws[f"E{r}"] = name, line, note
        ws[f"C{r}"], ws[f"D{r}"] = counted("H", r), counted("J", r)
        ws[f"C{r}"].number_format = ws[f"D{r}"].number_format = MONEY
        ws[f"F{r}"].fill = INPUT_FILL
        if r >= TRK_FIRST:
            for col in "ABCDE":
                ws[f"{col}{r}"].font = MUTED
    ws[f"A{TOTAL_ROW}"] = "TOTAL (Schedule C and home office)"
    ws[f"C{TOTAL_ROW}"] = f"=SUM(C{CAT_FIRST}:C{CAT_LAST})"
    ws[f"D{TOTAL_ROW}"] = f"=SUM(D{CAT_FIRST}:D{CAT_LAST})"
    for col in "ACD":
        ws[f"{col}{TOTAL_ROW}"].font = BOLD
    ws[f"C{TOTAL_ROW}"].number_format = ws[f"D{TOTAL_ROW}"].number_format = MONEY
    ws[f"A{TOTAL_ROW + 2}"] = (
        "Counts rows dated in the tax year whose Status is Approved or blank. "
        "The three grey rows are tracked but stay out of the total. "
        "Receipt folder: where approved receipts of that category are filed; blank means a folder named after the category."
    )
    ws[f"A{TOTAL_ROW + 2}"].font = MUTED
    ws.freeze_panes = "A2"


# ------------------------------------------------------------------ Expenses
EXPENSE_COLUMNS = [
    ("Date", 12),
    ("Item / description", 30),
    ("Vendor", 22),
    ("Category", 26),
    ("Business purpose", 36),
    ("Qty", 6),
    ("Unit price", 12),
    ("Total paid", 12),
    ("Business use %", 14),
    ("Deductible amount", 17),
    ("Receipt (link or image)", 30),
    ("Notes", 40),
    ("Status", 14),
    ("Question", 44),
    ("Your answer", 34),
    ("Source ID", 26),
]


def build_expenses(ws):
    ws.title = "Expenses"
    for i, (name, width) in enumerate(EXPENSE_COLUMNS, start=1):
        c = ws.cell(row=1, column=i, value=name)
        c.font, c.fill = BOLD, HEADER_FILL
        ws.column_dimensions[c.column_letter].width = width
    ws.freeze_panes = "A2"

    for col, fmt in (("A", "yyyy-mm-dd"), ("G", MONEY), ("H", MONEY), ("I", "0.00%"), ("J", MONEY)):
        for row in range(2, 302):
            ws[f"{col}{row}"].number_format = fmt

    status = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=True)
    cat = DataValidation(type="list", formula1=CATEGORY_RANGE, allow_blank=True)
    ws.add_data_validation(status)
    ws.add_data_validation(cat)
    status.add(f"M2:M{LAST_ROW}")
    cat.add(f"D2:D{LAST_ROW}")

    rng = f"A2:P{LAST_ROW}"
    ws.conditional_formatting.add(
        rng, FormulaRule(formula=['$M2="Needs answer"'], fill=PatternFill("solid", bgColor="FFE599"))
    )
    ws.conditional_formatting.add(
        rng, FormulaRule(formula=['$M2="Rejected"'], font=Font(color="999999", strike=True))
    )
    ws.conditional_formatting.add(
        f"M2:M{LAST_ROW}", FormulaRule(formula=['$M2="Approved"'], fill=PatternFill("solid", bgColor="B7E1CD"))
    )


# ------------------------------------------------------------ Filing summary
def build_filing(ws):
    rows = []  # (form/line, item, amount, records, style)

    def add(a="", b="", c=None, d="", style=None):
        rows.append((a, b, c, d, style))
        return len(rows) + 1  # sheet row (row 1 is the title)

    add("Form / line", "Item", "Amount", "Records to keep / how to enter", "header")
    add("SCHEDULE C - INCOME", style="section")
    income = add("Sch C line 1", "Gross receipts (1099-NEC and other business income)", None,
                 "ENTER: update to the 1099 totals when they arrive", "input")
    add("SCHEDULE C - EXPENSES (Part II)", style="section")
    first_exp = None
    for name, line, _ in CATEGORIES:
        if name == "Home office":
            continue
        label = f"{line} (list in Part V)" if line == "Line 27a" else line
        r = add(label, name, f"=Categories!D{cat_row(name)}", "Receipts in Expenses tab")
        first_exp = first_exp or r
    last_exp = r
    line28 = add("Line 28", "Total expenses before home office", f"=SUM(C{first_exp}:C{last_exp})", "", "bold")
    line29 = add("Line 29", "Tentative profit", f"=C{income}-C{line28}", "", "bold")

    add("FORM 8829 - HOME OFFICE", style="section")
    sqft = add("Form 8829", "Office square feet", "='My situation'!B13", "Used regularly and only for business")
    home = add("Form 8829", "Total home square feet", "='My situation'!B14")
    pct = add("Form 8829", "Business-use %", f"=IF(AND(N(C{sqft})>0,N(C{home})>0),C{sqft}/C{home},0)", "", "pct")
    shared = add("Form 8829", "Shared home costs (rent, utilities, insurance)",
                 f"=Categories!C{cat_row('Home shared costs')}", "Home shared costs rows in Expenses tab")
    indirect = add("Form 8829", "Shared home costs x business %", f"=C{shared}*C{pct}")
    direct = add("Form 8829", "Direct office expenses (Home office rows)",
                 f"=Categories!D{cat_row('Home office')}", "Receipts in Expenses tab")
    regular = add("Line 30", "Home office - regular method",
                  f"=MAX(0,MIN(C{indirect}+C{direct},C{line29}))", "Capped at tentative profit", "bold")
    simplified = add("Line 30", "Home office - simplified method (compare)",
                     f"=MAX(0,MIN(MIN(N(C{sqft}),300)*5,C{line29}))",
                     "$5 per sq ft, up to 300 sq ft. If used, direct office expenses are not deducted separately")
    add("Line 31", "Net profit (regular method)", f"=C{line29}-C{regular}", "Goes to Schedule 1 and Schedule SE", "bold")
    add("Line 31", "Net profit (simplified method)", f"=C{line29}-C{simplified}", "Use one method, not both")

    add("FORM 2441 - CHILDCARE", style="section")
    add("Form 2441", "Dependent care paid this year", f"=Categories!C{cat_row('Dependent care')}",
        "Provider name, address, EIN and year-end statement")
    add("Form 2441", "Dependent care FSA (W-2 box 10)", None, "ENTER: from your W-2", "input")
    add("Form 2441", "Spouse earned income", None,
        "ENTER: if 0, the FSA amount is added back to income and there is no credit", "input")

    add("ESTIMATED TAX", style="section")
    add("Form 1040-ES", "Q4 estimated payment", None, "ENTER: due January 15 of the following year", "input")

    ws["A1"] = '="Filing summary - "&\'My situation\'!B4&" return"'
    ws["A1"].font = TITLE
    for i, (a, b, c, d, style) in enumerate(rows, start=2):
        ws[f"A{i}"], ws[f"B{i}"], ws[f"D{i}"] = a, b, d
        if c is not None:
            ws[f"C{i}"] = c
        ws[f"C{i}"].number_format = "0.00%" if style == "pct" else MONEY
        if style in ("header", "section", "bold"):
            for col in "ABCD":
                ws[f"{col}{i}"].font = BOLD
        if style == "header":
            for col in "ABCD":
                ws[f"{col}{i}"].fill = HEADER_FILL
        if style == "input":
            ws[f"C{i}"].fill = INPUT_FILL
    ws[f"C{sqft}"].number_format = ws[f"C{home}"].number_format = "#,##0"

    end = len(rows) + 3
    for i, text in enumerate([
        "Yellow cells are for you to type in. Everything else is calculated from the Expenses tab.",
        "Line numbers follow recent versions of the forms. Check them against this year's forms before you file.",
        "This is a sorting aid, not tax advice.",
    ]):
        ws[f"A{end + i}"] = text
        ws[f"A{end + i}"].font = MUTED

    for col, width in zip("ABCD", [28, 52, 16, 80]):
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "A3"


# -------------------------------------------------------------- My situation
SITUATION_ROWS = [
    # (row, label, default, help)
    (4, "Tax year", 2026, "Receipts dated in another year are flagged and left out of the totals."),
    (5, "Receipts folder (Google Drive link)", None, "The folder you upload receipts to."),
    (6, "Gmail label (optional)", None, "Example: tax-receipts. Leave blank to skip email."),
    (7, "What the side gig is", None, "Example: freelance illustration, sold through my own site and two agencies."),
    (8, "When it started", None, "Example: March 2024."),
    (9, "Phone: business use %", None, "Example: 40%. Leave blank and phone bills get a question."),
    (10, "Internet: business use %", None, "Example: 25%."),
    (11, "Home office: do you have one?", None, "Yes or No. It must be used regularly and only for the business."),
    (12, "Home office: method", None, "Simplified (no receipts needed) or Actual expenses."),
    (13, "Home office: office square feet", None, "Example: 120."),
    (14, "Home office: whole home square feet", None, "Example: 1,400."),
    (15, "Home office: business share", '=IF(AND(N(B13)>0,N(B14)>0),B13/B14,"")', "Calculated. Filing summary uses it for shared home costs."),
    (16, "Car: how you track business driving", None, "Standard mileage, Actual expenses, or No business driving."),
    (17, "Meals: when is a meal a business meal?", None, "Example: only with a client or while travelling overnight for work."),
    (18, "Dependent care: who and which providers", None, "Example: Mia (age 4), Little Oaks Daycare."),
    (19, "Always personal (never deductible)", None, "Example: groceries, streaming, gym."),
    (20, "Always business", None, "Example: anything from the print shop."),
    (21, "Anything else Claude should know", None, "Free text."),
    (22, "Filed receipts folder (Google Drive link, optional)", None,
     "After you approve or reject a row, Claude moves its file from the receipts folder into a subfolder here. Leave blank and files stay where they are."),
]


def build_situation(ws):
    ws["A1"] = "My situation"
    ws["A1"].font = TITLE
    ws["A2"] = (
        "Fill in the yellow cells. Claude reads this tab on every run and applies it to your receipts. "
        "A blank answer means Claude asks you instead of guessing."
    )
    ws["A2"].font = MUTED
    ws.merge_cells("A2:C2")
    ws["A2"].alignment = WRAP
    ws.row_dimensions[2].height = 32

    for col, text in zip("ABC", ["Setting", "Your answer", "What this means"]):
        c = ws[f"{col}3"]
        c.value, c.font, c.fill = text, BOLD, HEADER_FILL

    for row, label, default, help_text in SITUATION_ROWS:
        ws[f"A{row}"] = label
        ws[f"A{row}"].alignment = WRAP
        b = ws[f"B{row}"]
        b.value = default
        b.alignment = WRAP
        if row != 15:
            b.fill = INPUT_FILL
        ws[f"C{row}"] = help_text
        ws[f"C{row}"].font = MUTED
        ws[f"C{row}"].alignment = WRAP

    for cell in ("B9", "B10", "B15"):
        ws[cell].number_format = "0%"

    ws["A23"] = "Vendor rules"
    ws["A23"].font = TITLE
    for col, text in zip(
        "ABCDE", ["When the vendor or item contains", "Category", "Business use %", "Note", "File into folder (optional)"]
    ):
        c = ws[f"{col}24"]
        c.value, c.font, c.fill = text, BOLD, HEADER_FILL
    for row in range(25, 55):
        for col in "ABCDE":
            ws[f"{col}{row}"].fill = INPUT_FILL
        ws[f"C{row}"].number_format = "0%"

    yes_no = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    method = DataValidation(type="list", formula1='"Simplified,Actual expenses"', allow_blank=True)
    car = DataValidation(type="list", formula1='"Standard mileage,Actual expenses,No business driving"', allow_blank=True)
    cat = DataValidation(type="list", formula1=CATEGORY_RANGE, allow_blank=True)
    for dv, ref in ((yes_no, "B11"), (method, "B12"), (car, "B16"), (cat, "B25:B54")):
        ws.add_data_validation(dv)
        dv.add(ref)

    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 42
    ws.column_dimensions["C"].width = 70
    ws.column_dimensions["D"].width = 40
    ws.column_dimensions["E"].width = 30
    ws.freeze_panes = "A4"


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    wb = Workbook()
    build_expenses(wb.active)
    build_filing(wb.create_sheet("Filing summary"))
    build_categories(wb.create_sheet("Categories"))
    build_situation(wb.create_sheet("My situation"))
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
