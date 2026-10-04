# Power BI build

How to build the report in Power BI Desktop from nothing, by copying and pasting. Every number it shows must match
the notebook; `06-checks.md` lists them.

## What the report answers

| Page | Question |
|---|---|
| Overview | How is the business doing overall? |
| Sales | Are we growing against last year, and where? |
| Categories | What sells? |
| Sellers | Who sells, and which sellers hurt the customer experience? |
| Delivery | How much does late delivery cost us in reviews? |

Each regional manager can be limited to the sellers of their region (row-level security, five roles).

## Follow the files in order

`08-build-checklist.md` is the click-by-click order from opening Power BI Desktop to the last screenshot; it points
into the other files and says when to compare with each check in `06-checks.md`.

| File | Contents |
|---|---|
| `01-power-query.md` | The parameter and six queries (M code), which ones load, the columns and types that load |
| `02-model.md` | Tables and grain, the date table (DAX), relationships, design choices, hidden columns, sort orders, formats, display folders, the five security roles |
| `03-measures.dax` | 23 measures with format, display folder and meaning, and which page uses each |
| `04-pages.md` | The five pages, visual by visual: type, fields, position and size, sort, labels, conditional formatting, slicers and their sync |
| `05-theme.json` | The theme, in the portfolio site's colours (import: View → Themes → Browse for themes) |
| `06-checks.md` | The value every card and table must show, C1 to C43 |
| `07-interactions.md` | The edit-interactions matrix per page, filters, and why there is no drill-through or bookmark |
| `08-build-checklist.md` | The 45 steps, with the checks to make at each point |

The report is saved here as `sales-performance.pbix`, with one screenshot per page in `screenshots/`.

## Needs

- Power BI Desktop (free).
- The seven CSV files in `data/raw/` (see the main README, "Data").
