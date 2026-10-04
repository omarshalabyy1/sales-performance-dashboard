# 6. Checks

The numbers each page must show. They come from the notebook (`analysis/analysis.ipynb`, section 12), and the main
totals are computed a second time in SQL straight from the raw files (`sql/checks.sql`, notebook section 11). If a
card shows anything else, the build is wrong: see "If a number is off" at the end.

Slicers cleared ("All") unless the row says otherwise. Display units as set in `04-pages.md`.

## Row counts (Data view)

| Table | Rows |
|---|---|
| `fact_sales` | 110,197 |
| `dim_date` | 1,096 |
| `dim_product` | 32,951 |
| `dim_seller` | 3,095 |
| `dim_customer` | 99,441 |

## Overview

| Visual | Must show | Exact value |
|---|---|---|
| Revenue card | 13.22M | 13,221,498.11 |
| Orders card | 96,478 | |
| Customers card | 93,358 | |
| Repeat customers card | 3.0% | |
| Late deliveries card | 6.8% | 6.77% |
| Average review card | 4.16 | |
| Revenue by customer region, first bar | Southeast, 8.6M | 8,648,409.57 |
| Top 10 categories, first bar | health beauty, 1.23M | 1,233,131.72 |
| Average review, on time against late | 4.29 and 2.27 | |

## Sales (Year slicer = 2018)

| Visual | Must show | Exact value |
|---|---|---|
| Revenue card | 7.22M | 7,218,125.12 |
| Revenue last year card | 2.94M | 2,944,431.50 (1 Jan to 29 Aug 2017) |
| Against last year card | +145.1% | |
| Orders card | 52,783 | |
| Average order value card | 136.75 | |
| Freight % of revenue card | 17.1% | |
| Month by month, Jan 2018 row | 7,069 orders, 924,645 revenue | 924,645.00 |
| Month by month, total row | 52,783 orders, 7,218,125 revenue | |

## Categories

| Visual | Must show | Exact value |
|---|---|---|
| Revenue card | 13.22M | |
| Items sold card | 110,197 | |
| Categories with sales card | 74 | |
| Top 10 categories share card | 62.4% | |
| All categories table, first row | health beauty, 9.3% of revenue | 1,233,131.72 |

## Sellers

| Visual | Must show | Exact value |
|---|---|---|
| Active sellers card | 2,970 | |
| Top 10% sellers share card | 67.1% | the 297 largest sellers |
| Late deliveries card | 6.8% | |
| Sellers table, first row | 4869f7a5 | 226,987.93 |

## Delivery

| Visual | Must show | Exact value |
|---|---|---|
| Average delivery days card | 12.5 | |
| Late deliveries card | 6.8% | |
| Late orders card | 6,534 | |
| Average review, on time card | 4.29 | |
| Average review, late card | 2.27 | |
| Review scores chart, 1 star | Late 54%, On time 7% | 53.8% and 6.6% |
| 10 states with the most late deliveries, first bar | AL, 21.4% | |

## Row-level security (Modeling → View as)

The Revenue card on Overview, viewed as each role:

| Role | Revenue |
|---|---|
| Seller region - Southeast | 10,354,931.00 |
| Seller region - South | 2,219,100.72 |
| Seller region - Northeast | 455,082.78 |
| Seller region - Center-West | 185,206.41 |
| Seller region - North | 7,177.20 |

The five add up to 13,221,498.11, the total revenue.

## SQL check

Run from the repo root (needs the DuckDB command-line tool, or run notebook section 11):

```
duckdb -c ".read sql/checks.sql"
```

It returns revenue 13,221,498.11, orders 96,478, customers 93,358, late_pct 6.77, avg_review 4.16 and
growth_pct 145.14, the same as the cards above.

## If a number is off

| Symptom | Likely cause |
|---|---|
| Orders shows 99,441 | `stg_orders` is missing the `Delivered` step |
| Customers shows 96,478 | the measure counts `customer_id` (one per order) instead of `customer_unique_id` |
| Average review is a little off | the review is averaged per item instead of per order, or `stg_reviews` is not grouped to the latest review |
| Categories look like `beleza saude` or many show `unknown` | the translation join failed; in `dim_product`, check that the `Names` step shows a column called exactly `product_category_name` |
| Revenue last year is blank | the Sales page Year slicer is not on one year, or `dim_date` is not marked as the date table |
| Revenue last year shows the whole of 2017 | `Date With Sales` is missing from `Revenue LY` |
| Amounts 100 times too big | the price column was typed without the `en-US` culture |
