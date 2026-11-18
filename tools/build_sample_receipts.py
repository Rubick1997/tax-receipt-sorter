"""Build the fake receipts in sample-receipts/.

Every vendor, person and number here is invented. Each page is stamped SAMPLE.
Needs: pip install reportlab

Usage: python tools/build_sample_receipts.py [output_dir]
"""

import sys
from pathlib import Path

from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent.parent / "sample-receipts"

# (file name, vendor, address line, date, lines [(item, amount)], tax, footer)
RECEIPTS = [
    ("01-inkwell-cloud.pdf", "Inkwell Cloud", "inkwellcloud.example", "2026-03-02",
     [("Pro plan, monthly", 22.99)], 0.00, "Invoice INV-20418  Paid by card ending 0000"),
    ("02-paper-and-pine.pdf", "Paper & Pine Stationers", "14 Alder Row, Fernhollow", "2026-03-09",
     [("Marker set, 24 colours", 31.50), ("Sketch pad A3 x2", 12.80)], 3.87, "Receipt 77102"),
    ("03-copper-kettle.pdf", "The Copper Kettle", "3 Quay Lane, Fernhollow", "2026-03-14",
     [("Lunch for 2", 52.00), ("Coffee x2", 7.00)], 5.30, "Table 6  Thank you!"),
    ("04-northline-mobile.pdf", "Northline Mobile", "northline.example", "2026-03-18",
     [("Unlimited plan, March", 85.00)], 0.00, "Account 000-111-222"),
    ("05-bigmart.pdf", "BigMart Superstore", "Ring Road Retail Park", "2026-03-21",
     [("Printer ink, black XL", 38.99), ("Groceries", 61.42), ("Kids socks 5pk", 9.99)], 4.12, "Till 12  Receipt 550193"),
    ("06-little-oaks.pdf", "Little Oaks Daycare", "22 Mill Street, Fernhollow", "2026-03-31",
     [("Childcare, March: Mia Rivera", 1150.00)], 0.00, "Provider tax ID 00-0000000"),
    ("07-paper-and-pine-photo.pdf", "Paper & Pine Stationers", "14 Alder Row, Fernhollow", "2026-03-09",
     [("Marker set, 24 colours", 31.50), ("Sketch pad A3 x2", 12.80)], 3.87, "Receipt 77102  (customer copy)"),
    ("08-frameworks-december.pdf", "Frameworks Framing", "9 Gallery Arcade, Fernhollow", "2025-12-28",
     [("Frame, oak, 50x70", 74.00)], 6.11, "Receipt 1203"),
    ("09-voltbyte.pdf", "Voltbyte Computers", "voltbyte.example", "2026-04-04",
     [("Laptop 14in, 32GB", 1499.00)], 123.67, "Order VB-88213"),
    ("10-brookline-fibre.pdf", "Brookline Fibre", "brooklinefibre.example", "2026-04-06",
     [("Home internet, April", 70.00)], 0.00, "Account 4400-000"),
]


def draw(path, vendor, address, date, lines, tax, footer):
    w, h = A6
    c = canvas.Canvas(str(path), pagesize=A6)
    c.setTitle(f"SAMPLE receipt: {vendor}")

    c.saveState()
    c.setFillGray(0.88)
    c.setFont("Helvetica-Bold", 44)
    c.translate(w / 2, h / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, "SAMPLE")
    c.restoreState()

    y = h - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w / 2, y, vendor)
    c.setFont("Helvetica", 8)
    c.drawCentredString(w / 2, y - 13, address)
    c.drawCentredString(w / 2, y - 25, f"Date: {date}")

    y -= 52
    c.line(20, y + 8, w - 20, y + 8)
    c.setFont("Helvetica", 9)
    subtotal = 0.0
    for item, amount in lines:
        c.drawString(22, y - 6, item)
        c.drawRightString(w - 22, y - 6, f"{amount:,.2f}")
        subtotal += amount
        y -= 15
    y -= 4
    c.line(20, y + 6, w - 20, y + 6)
    for label, amount, font in (
        ("Subtotal", subtotal, "Helvetica"),
        ("Tax", tax, "Helvetica"),
        ("TOTAL (USD)", subtotal + tax, "Helvetica-Bold"),
    ):
        c.setFont(font, 9 if font == "Helvetica" else 11)
        c.drawString(22, y - 8, label)
        c.drawRightString(w - 22, y - 8, f"{amount:,.2f}")
        y -= 15

    c.setFont("Helvetica", 7)
    c.drawCentredString(w / 2, 34, footer)
    c.drawCentredString(w / 2, 22, "Sample document for testing. Not a real receipt.")
    c.showPage()
    c.save()


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    out.mkdir(parents=True, exist_ok=True)
    for name, *rest in RECEIPTS:
        draw(out / name, *rest)
    print(f"wrote {len(RECEIPTS)} receipts to {out}")


if __name__ == "__main__":
    main()
