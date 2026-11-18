# Example: a filled-in "My situation" tab

An invented household, to show what useful answers look like. Copy the style, not the facts.

| Setting | Answer |
|---|---|
| Tax year | 2026 |
| Receipts folder (Google Drive link) | (link to a folder called "Receipts 2026") |
| Gmail label (optional) | tax-receipts |
| What the side gig is | Sam does freelance illustration: book covers and posters, sold through two agencies and Sam's own site. Jo has a salaried job with no business expenses. |
| When it started | March 2024 |
| Phone: business use % | 40% |
| Internet: business use % | 25% |
| Home office: do you have one? | Yes |
| Home office: method | Simplified |
| Home office: office square feet | 120 |
| Home office: whole home square feet | 1,400 |
| Car: how you track business driving | Standard mileage |
| Meals: when is a meal a business meal? | Only with a client or an agency contact, or while away overnight for work. Coffee alone while working is personal. |
| Dependent care: who and which providers | Mia (age 4). Little Oaks Daycare. |
| Always personal (never deductible) | Groceries, clothing, streaming, gym, anything for Mia other than daycare. |
| Always business | Anything from Paper & Pine Stationers. Parking at the agency offices. |
| Anything else Claude should know | Sam sometimes buys art supplies and household items on one receipt at BigMart. Always ask which lines are for work. |
| Filed receipts folder (Google Drive link, optional) | (link to a folder called "Taxes 2026") |

## Vendor rules

| When the vendor or item contains | Category | Business use % | Note | File into folder (optional) |
|---|---|---|---|---|
| Inkwell | Software & subscriptions | 100% | Design software | |
| Paper & Pine | Supplies | 100% | | |
| Northline | Phone & internet | 40% | Sam's mobile plan | Phone bills |
| Brookline | Phone & internet | 25% | Home internet | Internet bills |
| Little Oaks | Dependent care | 100% | | Daycare |

With the filed receipts folder set, an approved Northline bill moves from the receipts folder to "Taxes 2026 / Phone bills". An approved Inkwell invoice, with no folder in its rule or its category, moves to "Taxes 2026 / Software & subscriptions". A rejected receipt moves to "Taxes 2026 / Rejected".

## What to expect with the sample receipts

With these rules and the ten files in `sample-receipts/`, a first run should give roughly:

| Receipt | Expected result |
|---|---|
| 01 Inkwell Cloud | Suggested: Software & subscriptions |
| 02 Paper & Pine | Suggested: Supplies |
| 03 The Copper Kettle | Needs answer: who was the lunch with? |
| 04 Northline Mobile | Suggested: Phone & internet, 40% |
| 05 BigMart | Needs answer: which lines are for work? |
| 06 Little Oaks Daycare | Suggested: Dependent care |
| 07 Paper & Pine (second copy) | Needs answer: likely duplicate of 02 |
| 08 Frameworks, December 2025 | Needs answer: wrong year |
| 09 Voltbyte laptop | Needs answer: is it only for the business? |
| 10 Brookline Fibre | Suggested: Phone & internet, 25% |
