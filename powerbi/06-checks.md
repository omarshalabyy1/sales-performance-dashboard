# 6. Checks

The numbers each page must show for the demo run. For other data, refill the values from the notebook's section 12.
They come from the notebook (`analysis/analysis.ipynb`, section 12), and the main
totals are computed a second time in SQL straight from the input files (`sql/checks.sql`, notebook section 11). If a
card shows anything else, the build is wrong: see "If a number is off" at the end.

Slicers cleared ("All") unless the row says otherwise. Display units as set in `04-pages.md`.

## Row counts (Data view)

| # | Table | Rows |
|---|---|---|
| C1 | `fact_sales` | 110,197 |
| C2 | `dim_date` | 1,096 |
| C3 | `dim_product` | 32,951 |
| C4 | `dim_seller` | 3,095 |
| C5 | `dim_customer` | 99,441 |

## Overview

| # | Visual | Must show | Exact value |
|---|---|---|---|
| C6 | Revenue card | 13.22M | 13,221,498.11 |
| C7 | Orders card | 96,478 | |
| C8 | Customers card | 93,358 | |
| C9 | Repeat customers card | 3.0% | |
| C10 | Late deliveries card | 6.8% | 6.77% |
| C11 | Average review card | 4.16 | |
| C12 | Revenue by customer region, first bar | Southeast, 8.6M | 8,648,409.57 |
| C13 | Top 5 categories, first bar | health beauty, 1.23M | 1,233,131.72 |
| C14 | Average review, on time against late | 4.29 and 2.27 | |

## Sales (Year slicer = `report.compare_year`, demo 2018)

| # | Visual | Must show | Exact value |
|---|---|---|---|
| C15 | Revenue card | 7.22M | 7,218,125.12 |
| C16 | Revenue last year card | 2.94M | 2,944,431.50 (1 Jan to 29 Aug 2017) |
| C17 | Against last year card | +145.1% | |
| C18 | Orders card | 52,783 | |
| C19 | Average order value card | 136.75 | |
| C20 | Freight % of revenue card | 17.1% | |
| C21 | Month by month, Jan 2018 row | 7,069 orders, 924,645 revenue | 924,645.00 |
| C22 | Month by month, total row | 52,783 orders, 7,218,125 revenue | |

## Categories

| # | Visual | Must show | Exact value |
|---|---|---|---|
| C23 | Revenue card | 13.22M | |
| C24 | Items sold card | 110,197 | |
| C25 | Categories with sales card | 74 | |
| C26 | Top categories share card | 62.4% | |
| C27 | All categories table, first row | health beauty, 9.3% of revenue | 1,233,131.72 |

## Sellers

| # | Visual | Must show | Exact value |
|---|---|---|---|
| C28 | Active sellers card | 2,970 | |
| C29 | Top sellers share card | 67.1% | the 297 largest sellers |
| C30 | Late deliveries card | 6.8% | |
| C31 | Sellers table, first row | 4869f7a5 | 226,987.93 |

## Delivery

| # | Visual | Must show | Exact value |
|---|---|---|---|
| C32 | Average delivery days card | 12.5 | |
| C33 | Late deliveries card | 6.8% | |
| C34 | Late orders card | 6,534 | |
| C35 | Average review, on time card | 4.29 | |
| C36 | Average review, late card | 2.27 | |
| C37 | Review scores chart, 1 star | Late 54%, On time 7% | 53.8% and 6.6% |
| C38 | 10 states with the most late deliveries, first column | AL, 21.4% | |

## Row-level security (Modeling → View as)

The Revenue card on Overview, viewed as each role:

| # | Role | Revenue |
|---|---|---|
| C39 | Seller region - Southeast | 10,354,931.00 |
| C40 | Seller region - South | 2,219,100.72 |
| C41 | Seller region - Northeast | 455,082.78 |
| C42 | Seller region - Center-West | 185,206.41 |
| C43 | Seller region - North | 7,177.20 |

The five add up to 13,221,498.11, the total revenue.

## SQL check

The notebook's section 11 runs `sql/checks.sql` with DuckDB on the input files (the rules arrive as parameters
from `config/client.yaml`) and stops if any total differs from the pandas result. For the demo it returns revenue 13,221,498.11, orders 96,478, customers 93,358, late_pct 6.77, avg_review 4.16 and
growth_pct 145.14, the same as the cards above.

## If a number is off

| Symptom | Likely cause |
|---|---|
| Orders shows 99,441 | the notebook ran with every status as a sale (`rules.sale_statuses`), or `output/` is from another run: rerun the notebook, then **Refresh** |
| Customers shows 96,478 | the measure counts `customer_id` (one per order) instead of `person_id` |
| Average review is a little off | the review is averaged per item instead of per order |
| Categories look like `beleza_saude` or many show `unknown` | the category names file did not match: check `inputs.category_names` and `columns.category_names` in `config/client.yaml`, rerun the notebook |
| Revenue last year is blank | the Sales page Year slicer is not on one year, or `dim_date` is not marked as the date table |
| Revenue last year shows the whole of 2017 | `Date With Sales` is missing from `Revenue LY` |
| Amounts 100 times too big | the price column was typed without the `en-US` culture |
