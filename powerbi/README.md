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

| Step | File | You do |
|---|---|---|
| 1 | `01-power-query.md` | Paste seven queries into Power Query; check the row counts |
| 2 | `02-model.md` | Create the date table and the measures table, the four relationships, hidden columns, sort orders and the five security roles |
| 3 | `03-measures.dax` | Paste 23 measures, each with its format and display folder |
| 4 | `05-theme.json` | Load the theme (before you build the pages) |
| 5 | `04-pages.md` | Build the five pages, visual by visual |
| 6 | `06-checks.md` | Check every card against the expected numbers, and each security role |

Then save the report here as `sales-performance.pbix` and put one screenshot per page in `screenshots/`.

## Needs

- Power BI Desktop (free).
- The seven CSV files in `data/raw/` (see the main README, "Data").
