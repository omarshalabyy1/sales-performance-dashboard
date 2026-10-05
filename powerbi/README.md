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

Each regional manager can be limited to the sellers of their region (row-level security, one role per region).

## The fast way: open the generated report

`sales-performance.pbip` is the finished report as a Power BI project, written by `build_pbip.py` from the files
below and `config/client.yaml`. After the notebook has written `output/`:

1. `python powerbi/build_pbip.py` (only after a change to the config or to files 01 to 05).
2. Open `powerbi/sales-performance.pbip` in Power BI Desktop and click **Refresh now** on the yellow bar.
3. Compare the cards with `06-checks.md`. Every check was verified against the model running in Power BI Desktop
   on 2026-10-05, C1 to C43, and the five pages are in `screenshots/`.

## Or build it by hand, to learn it

`08-build-checklist.md` is the click-by-click order from opening Power BI Desktop to the last screenshot; it points
into the other files and says when to compare with each check in `06-checks.md`.

| File | Contents |
|---|---|
| `01-power-query.md` | The `OutputFolder` parameter and five queries that read the notebook's output tables, the columns and types that load |
| `02-model.md` | Tables and grain, the date table (DAX), relationships, design choices, hidden columns, sort orders, formats, display folders, one security role per region |
| `03-measures.dax` | 23 measures with format, display folder and meaning, and which page uses each |
| `04-pages.md` | The five pages, visual by visual: type, fields, position and size, sort, labels, conditional formatting, slicers and their sync |
| `05-theme.json` | The theme, written by `python theme.py` from `report.title` and `report.colours` (import: View → Themes → Browse for themes) |
| `06-checks.md` | The value every card and table must show for the demo, C1 to C43 |
| `07-interactions.md` | The edit-interactions matrix per page, filters, and why there is no drill-through or bookmark |
| `08-build-checklist.md` | The 47 steps, from the input files to the last screenshot, with the checks to make at each point |

Built by hand, the report is saved as `sales-performance.pbix`; the generated one is `sales-performance.pbip` with its
`.Report` and `.SemanticModel` folders. One screenshot per page is in `screenshots/`.

## Needs

- Power BI Desktop (free).
- The input files in `data/input/` and the notebook run once (steps 1 to 4 of `08-build-checklist.md`).
