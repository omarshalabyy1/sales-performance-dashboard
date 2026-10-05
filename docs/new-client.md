# New client

This repo is a GitHub template. A new client gets a **private** repo from it (Use this template > Create a new
repository > Private); client data never goes into this public repo. Everything that changes per client is in two
places: `config/client.yaml` and the files in `data/input/`. There is no secret, so there is no `.env`.

It is the Power BI version of offering 10, "Power BI sales and margin dashboard". **Which repo:** pick this one
when the client sends exports and wants the report without a database or Docker; pick
[retail-supplier-warehouse](https://github.com/omarshalabyy1/retail-supplier-warehouse) when they want a database
loaded and tested on a schedule (Airflow, dbt).

## Done in the template

What the client gets with no work. Hours are an estimate of building each part from scratch.

| # | Part | Estimate (hours) |
|---|---|---|
| A | Client settings: `config/client.yaml`, `config.py` (`load_config()` and the one-line input checks, `python config.py`), the Power BI theme written from the config (`theme.py`) | 2 |
| B | The model build: sale statuses, the late rule with its grace days, the latest review per order, regions and category names from input files, the health check, the star tables written to `output/` for Power BI (`analysis/analysis.ipynb`, sections 1 to 3) | 3 |
| C | Every number and the three charts: headline numbers, growth against the same days last year, delivery and reviews, category and seller concentration, revenue per region (sections 4 to 10, 12) | 3 |
| D | The SQL recount: DuckDB views from the config, the rules as parameters, the notebook stops if a total differs (`sql/checks.sql`, section 11) | 1.5 |
| E | Power BI build pack: 5 queries, the model with a DAX date table and one security role per region, 23 measures, 5 pages with 41 visuals, interactions, 43 checks, a 47-step checklist (`powerbi/`) | 8 |
| F | README with its diagrams, and the input file guide (`data/input/README.md`) | 2.5 |
| G | The finished report: `powerbi/build_pbip.py` writes `sales-performance.pbip` from the build pack and the config; every check verified against the model running in Power BI Desktop | 2 |
| | **Total** | **22** |

## Configure

Per client, file by file. Hours are an estimate.

| File | Key | Example (the drill below) | Estimate (hours) |
|---|---|---|---|
| `config/client.yaml` | `client.name`, `client.currency`, `client.decimals`, `report.title`, `report.colours` | `EGP`, `"#0F766E"` | 0.25 |
| `config/client.yaml` | `inputs` (eight file names) and `columns` (27 headers) | `orders: sales_orders.csv`, `price: Unit Price` | 1 |
| `config/client.yaml` | `rules.sale_statuses`, `rules.late_after_days`, `report.compare_year`, `report.top_categories`, `report.top_sellers_percent` | `[COMPLETE, PARTIAL]`, `1`, `2025`, `2`, `50` | 0.25 |
| `data/input/regions.csv` | the region of every state the client sells in | `CAI,Greater Cairo` | 0.5 |
| `data/input/` category names file | the name shown for each category code | `KIT,Kitchen` | 0.5 |
| Run `python config.py`, the notebook and `python theme.py`; go through the health check (section 2) with the client and fix the config | | | 1 |
| | **Subtotal without Power BI** | | **3.5** |
| `powerbi/` | `python powerbi/build_pbip.py`, open `sales-performance.pbip`, **Refresh now**; refill `06-checks.md` from the notebook's section 12 (same check numbers) and compare | | 1 |
| | **Total** | | **4.5** |

## Custom, for offering 10

Typical work per client that the template does not do. Hours are estimates.

| Work | Estimate (hours) |
|---|---|
| Margin: the client's cost per item (a product cost file or a cost column), the margin measures and a margin page (the demo data has no cost, so the demo has no margin) | 4 |
| Dates in another format, or Excel exports instead of CSV (the `read()` function in the notebook) | 1 |
| Publishing: the report in the Power BI service, people added to each region role, scheduled refresh through a gateway or OneDrive | 1.5 |
| A short walkthrough video of the report (the listing's deliverable) | 0.5 |
| **Total** | **7** |

Growth against last year and row-level security, custom work in the warehouse version, are already in this
template.

## Share already done (estimate)

Template hours ÷ (template + configure + custom) hours:

| Offering | Arithmetic | Share already done |
|---|---|---|
| 10. Power BI sales and margin dashboard | 22 ÷ (22 + 4.5 + 7) = 22 ÷ 33.5 | **66%** (65.7%) |
| 10, a client that needs no margin page | 22 ÷ (22 + 4.5 + 3) = 22 ÷ 29.5 | **75%** (74.6%) |

## Steps

1. Create the private repo from the template and clone it.
2. Put the client's files in `data/input/` ([columns and examples](../data/input/README.md)); CSV files there are
   ignored by git. Replace `data/input/regions.csv` with the client's states and regions.
3. Edit `config/client.yaml`.
4. `pip install -r requirements.txt`, then `python config.py`. It stops with one line if a key, a file or a column
   is wrong; fix and run again.
5. Run the notebook (`cd analysis`, `jupyter nbconvert --to notebook --execute --inplace analysis.ipynb`). Go
   through the health check (section 2) with the client.
6. `python theme.py`.
7. `python powerbi/build_pbip.py`, open `powerbi/sales-performance.pbip` in Power BI Desktop and click **Refresh now**.
   Refill `powerbi/06-checks.md` with the numbers from the notebook's section 12 and compare every page.

## Second-client drill (2026-10-05)

The acceptance test of the template: a copy of the repo as a fresh clone gets it (no demo files, no `output/`), a
made-up second client, a run from scratch.

**Client B (drill):** "Cedar Home Goods", currency `EGP`, title "Cedar Home sales", teal colours (`#0F766E` main,
`#B91C1C` danger, page `#F0FDFA`), `compare_year: 2025`, `top_categories: 2`, `top_sellers_percent: 50`.

- Its own file names (`sales_orders.csv`, `order_lines.csv`, `catalogue.csv`, `vendors.csv`, `shoppers.csv`,
  `feedback.csv`, `dept_names.csv`) and headers (`Order No`, `Customer Ref`, `State`, `Ordered On`, `Delivered On`,
  `Promised By`, `Line`, `SKU`, `Vendor`, `Unit Price`, `Delivery Fee`, `Dept`, `Town`, `Gov`, `Person`, `Stars`,
  `Answered`, `Display`), and an extra column in every file (`Channel`, `Discount`, `Weight`, `Phone`, `Comment`).
- Two sale statuses (`COMPLETE`, `PARTIAL`) and one that is not (`CANCELLED`); `late_after_days: 1`.
- Regions of another shape: `CAI` and `GIZ` in "Greater Cairo", `ALX` in "North Coast".
- One case for each rule: a cancelled order, an order 1 day after its promised date (on time with the grace day),
  one 2 days after and one 4 days after (late), a sale with no delivery date, an order reviewed twice (the later
  one counts), an order reviewed twice at the same moment (the higher score counts), a product with no category, a
  category code with no display name, one person with two addresses and two orders.

| What | Demo | Client B (drill) |
|---|---|---|
| Rows read: orders, items, reviews | 99,441, 112,650, 99,224 | 6, 8, 7 |
| Sale orders, items sold | 96,478, 110,197 | 5, 7 |
| Revenue, average order value | BRL 13,221,498.11, 137.04 | EGP 680.00, 136.00 |
| Customers, with 2+ orders | 93,358, 3.0% | 4, 25.0% |
| Late deliveries, late orders | 6.8%, 6,534 | 50.0%, 2 |
| Average review: all, on time, late | 4.16, 4.29, 2.27 | 3.75, 4.50, 3.00 |
| Growth against the same days last year | 2018: +145.1% | 2025: +120.0% |
| Top categories share | top 10 of 74: 62.4% | top 2 of 4: 67.6% |
| Top sellers share | top 10% (297 of 2,970): 67.1% | top 50% (2 of 3): 80.9% |
| Revenue per security role | five regions, 7,177.20 to 10,354,931.00 | Greater Cairo 390.00, North Coast 290.00 |
| SQL recount | 6 of 6 totals match | 6 of 6 totals match |
| Power BI theme | "Sales performance dashboard", `#2563EB` | "Cedar Home sales", `#0F766E`, danger `#B91C1C`, page `#F0FDFA` |
| Notebook | 0 errors | 0 errors; titles name Cedar Home Goods, amounts in EGP |

**By hand:** sale items 100 + 50 + 200 + 120 + 80 + 40 + 90 = 680.00 over orders O1, O2, O3, O4, O6 = 5, so the
average order is 136.00; freight 68.00 = 10.0%. Delivered on or before the promised date + 1 day: O1 and O3 (on
time); O2 (2 days after) and O4 (4 days after) late; O6 has no date: 2 ÷ 4 = 50.0%. Delivery days 4, 11, 7, 13:
average 8.75. Reviews counted: O1 5, O2 1 (the later of 2 and 1), O3 4, O4 5 (the higher of a tie, 3 and 5):
average 3.75, on time (5 + 4) ÷ 2 = 4.50, late (1 + 5) ÷ 2 = 3.00. Persons P1 (two orders), P2, P3, P5: 4
customers, 1 ÷ 4 = 25.0% repeat. 2025 to 2 Apr: 120 + 120 + 90 = 330.00 against 2024 to 2 Apr: 150.00, so +120.0%.
Categories Kitchen 260, DEC (no display name) 200, Bath 140, unknown 80: top 2 = 460 ÷ 680 = 67.6%. Sellers
V-GAMMA- 290, V-ALPHA- 260, V-BETA-0 130: top 50% of 3 = 2 sellers, 550 ÷ 680 = 80.9%. Every output number matched.

**Clear failures**, one line each, run on the Client B copy:

```
config/client.yaml is missing rules.late_after_days
config/client.yaml is not valid YAML near line 2 (quote a value with # or :)
missing data/input/feedback.csv (inputs.reviews in config/client.yaml)
data/input/feedback.csv: missing column(s): Stars
AssertionError: data/input/regions.csv: no region for state(s): ALX
AssertionError: rules.sale_statuses matches no order status
```

The first four come from `python config.py` (and the notebook's first cell); the last two from the notebook's
health check.

**The report for Client B:** `python powerbi/build_pbip.py` on the same copy wrote two security roles (Greater Cairo,
North Coast), the teal theme, a "Top 2 categories share" card, "Revenue, EGP" labels and 2025 preselected on the
Sales page. It was not opened in Power BI Desktop; the demo report was, and all 43 checks matched there.

**Nothing hard-coded:** this search over the notebook's code cells, `config.py`, `theme.py`, `sql/checks.sql`,
`powerbi/03-measures.dax`, `powerbi/build_pbip.py` and the M and DAX code in `powerbi/01-power-query.md` and
`powerbi/02-model.md` finds nothing:

```
olist|Olist|order_purchase_timestamp|order_delivered_customer_date|order_estimated_delivery_date|order_status|order_item_id|freight_value|product_category_name|customer_unique_id|review_answer_timestamp|["'\[]delivered["'\]]|\bBRL\b|Sample marketplace|\b2016\b|\b2017\b|\b2018\b|Southeast|Northeast|Center-West|\bSP\b|#[0-9A-Fa-f]{6}|TOPN \( 10|/ 10\b|\* 0\.1|regions\.csv|Sales performance
```

These keep the demo's values on purpose: the README and the diagrams in `docs/`, `powerbi/04-pages.md`,
`powerbi/06-checks.md` and `powerbi/08-build-checklist.md` (they name the demo values next to the config keys), and
`data/input/` (the demo's regions file and the input guide).

**Nothing broke:** after the change, the notebook on the demo files gives the same numbers as before, every one of
the 43 checks in `powerbi/06-checks.md` (13,221,498.11 revenue, 96,478 orders, 93,358 customers, 6.8% late,
+145.1% for 2018).

## Beyond the template standard

What this repo needed that `portfolio/docs/template-standard.md` does not say:

- **No database, so the notebook is the loader.** It applies the rules and writes the model tables to `output/`;
  Power BI reads those files. The input checks are `check_inputs()` in `config.py`, runnable on their own with
  `python config.py` before anything else.
- **Config values for DAX travel in a file.** With no database setting to read, the two top-N values reach the
  measures through `output/report_settings.csv`, a one-row table.
- **One header per column.** The inputs are system exports, so `columns` maps each standard name to one header,
  not a list of spellings as in excel-branch-report.
- **Model names that equal demo headers.** `order_id`, `customer_id`, `product_id`, `seller_id`, `review_score`,
  `customer_city`, `customer_state`, `seller_city` and `seller_state` are the template's own column names in
  `output/`, so the search above looks only for the demo headers that differ.
- **The report is generated, not hand-built.** `powerbi/build_pbip.py` reads the M code, the date table and the
  measures from the build pack itself, so the files a person follows and the report cannot drift apart.
- **Run the DAX before trusting it.** Opened in Power BI Desktop, the model rejected `Percent`, `TopPercent` and
  `TopCount` as variable names (reserved by the engine); checking every card over the local engine with ADOMD.NET
  caught it, and C1 to C43 then matched.
- **A tie in the data needs a rule, not a stop.** Two reviews answered at the same moment on one order would have
  stopped the demo version; the template keeps the higher score.

Not covered, custom work when a client needs it: dates in a format other than `YYYY-MM-DD`, Excel inputs, a
client without reviews or without delivery dates (the Delivery page), and seller ids whose first 8 characters are
not unique (the run stops).
