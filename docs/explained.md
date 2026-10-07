# The project explained, from zero

This page explains the whole project in plain words: what it does, what every word means, where every number comes from, and how to talk about it in an interview. You do not need to know Python or Power BI to read it.

[← Back to the README](../README.md)

## 1. The project in one minute

An online marketplace is like a big shopping centre: about three thousand independent sellers sell through it, and the marketplace delivers the orders and collects the reviews. Its systems export the data as separate files: one for orders, one for the items in each order, one for products, sellers, customers and reviews.

So the manager cannot answer simple questions on one page:

- Are we growing against last year?
- What sells, and who sells it?
- What do late deliveries cost us in customer reviews?

This project answers them. One Python notebook reads the files, checks them, applies the business rules once (what counts as a sale, when an order is late, which review counts) and writes clean tables. Power BI reads those tables and shows five report pages. A second calculation in SQL proves the main totals are right.

Think of it like a till receipt for every item sold. Each receipt line is one item, and it carries stamps: the day, the product, the seller, the customer, whether the order arrived late and the review it got. Every question in the report is the same move: sort the receipt lines by one stamp and add them up.

## 2. Words you will meet

| Word | What it means here |
|---|---|
| **BRL** | Brazilian real, the currency of the data. "7.22M" means 7.22 million reais. |
| **Order, item** | An order is one purchase. An item is one line in it: an order of two phone cases has two items. |
| **Sale** | An item of an order whose status is `delivered`. Orders that were cancelled, still shipping or never sent are left out. The rule is `rules.sale_statuses` in `config/client.yaml`. |
| **Revenue** | The item price. **Freight** (the delivery fee) is kept apart and shown on its own. The data has no product cost, so there is no profit or margin. |
| **Estimated date** | The delivery date the customer was promised when they ordered. |
| **Late** | Delivered on a later day than the estimated date. Only the dates count, not the time of day. The rule is `rules.late_after_days: 0`. |
| **Review score** | 1 to 5 stars the customer gave the order. When an order has more than one review, the latest answered one counts. |
| **Region** | Brazil's 26 states and the Federal District sit in five official regions (Southeast, South, Northeast, Center-West, North). `data/input/regions.csv` gives each state its region. |
| **Notebook** | `analysis/analysis.ipynb`, a file that mixes code, its output and notes. It is the source of truth for every number. |
| **Python, pandas** | Python is a programming language. pandas is its library for tables. The notebook uses it. |
| **CSV** | Comma-separated values: a plain text file of a table, one row per line. Every input and output file is a CSV. |
| **SQL** | Structured Query Language, the language used to ask a database questions. `sql/checks.sql` is SQL. |
| **DuckDB** | A small database that runs inside Python, with nothing to install or start. The project uses it only for the SQL check, reading the input files directly. That is why the README says "no database" and still shows a DuckDB badge. |
| **Table, row, column** | Like a spreadsheet sheet: each row is one thing (one item, one seller), each column is one fact about it (its price, its state). |
| **Fact table** | The big table of events you add up. Here `fact_sales`: one row per item sold, with its price and freight. |
| **Dimension table** | A lookup table that describes the facts: `dim_product` (the category), `dim_seller` (city, state, region), `dim_customer` (the person, city, state, region) and `dim_date` (day, month, year). You filter and group by them. |
| **Star schema** | One fact table in the middle with dimension tables around it, like a star. It is the standard shape for Power BI reports. See [data-model.svg](data-model.svg). |
| **Grain** | What one row of a table stands for. The grain of `fact_sales` is "one item of one delivered order". |
| **Primary key (PK)** | The column (or columns) that makes each row unique. For `fact_sales` it is the order id plus the item number. |
| **Foreign key (FK)** | A column that points to a row in another table: `fact_sales[seller_id]` points to one row in `dim_seller`. The notebook stops if one points to nothing. |
| **Degenerate attribute** | A fact about the order (its id, its delivery status, its review score) kept in the fact table because it has no table of its own. |
| **Date table** | A dimension with one row per day, so every day exists even if nothing sold on it. Here it is built in Power BI with DAX and covers whole years. |
| **YAML, `config/client.yaml`** | YAML is a simple text format for settings. `client.yaml` holds everything a client would change: names, file and column names, the rules, the top-N values, the colours. `config.py` reads it. |
| **Power BI** | Microsoft's tool for interactive reports and dashboards. |
| **Power Query** | The part of Power BI that loads data before the report uses it. Here it only reads the notebook's CSV files and sets the types. |
| **Import mode** | Power BI copies the data into the report file. After the notebook runs again, you click **Refresh** to see the new numbers. |
| **DAX** | Data Analysis Expressions, the formula language of Power BI, used to write **measures**: calculations like "Revenue" or "Late Deliveries %". This report has 23. |
| **Display folder** | A folder in Power BI's field list that groups measures. The 23 measures sit in 6: Sales, Orders and customers, Delivery, Reviews, Categories, Sellers. |
| **Same days last year** | The growth figure compares 2018 with 2017, but only from 1 Jan to 29 Aug in both years, because the data stops on 29 Aug 2018. |
| **Row-level security (RLS)** | A rule in Power BI that hides rows from some people. Here there is one role per seller region, so a regional manager sees only the sales of their own region's sellers. |
| **`.pbip`** | A Power BI project: the report saved as plain text files, so it can live in Git. `powerbi/sales-performance.pbip` opens in Power BI Desktop. |
| **Theme** | A Power BI file that sets the report's colours and fonts. `theme.py` writes `powerbi/05-theme.json` from `client.yaml`. |

## 3. How it works, file by file

Run in this order (the commands are in the README's "Run it" section):

| Step | File | What it does |
|---|---|---|
| 0 | `requirements.txt` | The Python libraries to install: PyYAML, pandas, matplotlib, DuckDB, Jupyter. |
| 0 | `config/client.yaml`, `config.py` | Hold every setting. `python config.py` checks that the 8 input files exist and have the needed columns, and stops with one line if not. |
| 1 | notebook sections 1 to 2 (cells 3, 5, 6) | Reads the 8 files, keeps only the mapped columns, then runs the health check: ids are unique, every item points to a real order, product and seller, every state has a region. It also counts what it will leave out (non-sale orders, extra reviews). |
| 2 | notebook section 3 (cell 8) | Applies the rules once and writes the model tables to `output/`: `fact_sales`, `dim_product`, `dim_seller`, `dim_customer` and `report_settings` (the top-N values for DAX). |
| 3 | notebook sections 4 to 10 (cells 10 to 26) | Computes every number in the README and draws the three charts in `docs/`. |
| 4 | notebook section 11 (cell 28) + `sql/checks.sql` | Computes revenue, orders, customers, late %, average review and growth again in SQL with DuckDB, straight from the input files. The notebook stops if any value differs. |
| 5 | notebook section 12 (cell 30) | Prints the value every Power BI card must show; they are copied into `powerbi/06-checks.md`. |
| 6 | `theme.py` | Writes the Power BI theme file from the colours in `client.yaml`. |
| 7 | `powerbi/build_pbip.py` | Writes the Power BI project from the build pack in `powerbi/` (queries, model, measures, pages). You open the `.pbip` and click **Refresh now**. |
| 8 | `powerbi/01` to `08` | The same report, step by step by hand: queries, model, measures, pages, theme, the 43 checks (`06-checks.md`), interactions, and a 47-step checklist. |

The 8 input files: 7 come from the marketplace (orders, order items, products, sellers, customers, reviews, category names; you download them, see Data in the README) and 1 is ours, committed in `data/input/` (`regions.csv`, the region of every state). The "How it works" diagram lists six of the seven by name; the seventh is the category names file, which turns a category code into a readable name.

### The rules, with an example

One real order from the data (order `66e4624a…`), traced through every rule:

| Fact | Value in the input files |
|---|---|
| Status | delivered |
| Ordered | 9 Mar 2018, 14:50 |
| Estimated delivery | 2 Apr 2018 |
| Delivered | 3 Apr 2018, 13:28 |
| Items | 2, the same product, 22.99 each, freight 22.85 each |
| Product category | code `telefonia`, shown as "telephony" |
| Seller | São Paulo, state SP |
| Customer | Aracaju, state SE |
| Reviews | one, 1 star, answered 4 Apr 2018 |

1. **Sale.** The status is `delivered`, so the order counts. 2,963 orders with another status are left out (cell 5).
2. **Grain.** Two items become two rows in `fact_sales`, keyed (`66e4624a…`, 1) and (`66e4624a…`, 2). Revenue is 22.99 + 22.99 = 45.98. Freight, 22.85 + 22.85 = 45.70, stays apart and is not in revenue.
3. **Late.** Times are dropped and only dates compared. Delivered 3 Apr is later than the estimated 2 Apr, so the order is **Late**, by one day. Delivery days = 3 Apr − 9 Mar = 25 days.
4. **Review.** The order has one review, so it keeps that one: 1 star. Had it two, the one answered last would count.
5. **Count once per order.** The delivery status (Late), the 25 days and the 1-star review repeat on both rows. The measures and the notebook first reduce to one row per order, so this order adds 1 to Late Orders and one 1-star score to Average Review, not 2. It adds 2 to Items Sold and 1 to Orders.
6. **Regions.** SP is in the Southeast and SE in the Northeast. On the Overview chart "Revenue by customer region", the 45.98 sits in **Northeast**. In row-level security, the role **Seller region - Southeast** sees this sale and the Northeast role does not. The two region views split the same total in different ways.

You can see the two rows in `output/fact_sales.csv` after a run: `66e4624a…, 1, 2018-03-09, …, 22.99, 22.85, 25, Late, 1` and the same with item 2.

## 4. Every number, explained

All of these are printed by the notebook ([`analysis/analysis.ipynb`](../analysis/analysis.ipynb)) unless the row says otherwise. The cell numbers below count from 0, the first cell. Where a number is not printed by the notebook, the row says so and gives how it was counted from the same files.

### The headline and the results table

| Number | What it means | How it is worked out | Where |
|---|---|---|---|
| **96,478 orders** | Delivered orders, the ones that count as sales. | Count of distinct order ids in `fact_sales`. The orders file has 99,441; 96,478 of them are `delivered`. | notebook cells 6, 10; SQL check cell 28 |
| **13,221,498** (exact 13,221,498.11) | Revenue: the price of every item sold. Freight is not in it. | Sum of `price` over the 110,197 rows of `fact_sales`. The README drops the 11 cents. | notebook cell 10; SQL check cell 28 |
| **Sep 2016 to Aug 2018** | The order dates in the data. | The first sale is on 15 Sep 2016 and the last on 29 Aug 2018. The notebook prints the last day (29 Aug, cell 12) but not the first; the first was read from `output/fact_sales.csv`. | notebook cell 12 |
| **93,358 customers** | People who bought, not addresses. | Count of distinct `person_id` among the 96,478 orders. The customers file has one row per order (99,441), so one person with three orders has three rows but counts once. | notebook cell 10; SQL check cell 28 |
| **+145.1%** (header, typing line), **+145%** (mental-model.svg) | Growth: 2018 revenue against the same days of 2017. | 7,218,125.12 / 2,944,431.50 − 1 = 145.1%. Both cover 1 Jan to 29 Aug, the last day with sales in 2018. | notebook cell 12 |
| **7.22M against 2.94M** | 2018 revenue and 2017 revenue on the same days. | Sums of `price` for orders placed 1 Jan to 29 Aug 2018 (7,218,125.12) and 1 Jan to 29 Aug 2017 (2,944,431.50). | notebook cell 12 |
| **6.8% late** | Share of orders delivered after the estimated date. | 6,534 late orders / 96,470 orders with a delivery date = 6.77%. 8 delivered orders have no delivery date and are left out of this one number (cell 5). The notebook prints 6,534 and 6.77; the 96,470 base (6,534 late + 89,936 on time) is in cell 15. | notebook cells 10, 15 |
| **2.27 stars late, 4.29 on time** | Average review of late and of on-time orders. | Average `review_score`, once per order, of reviewed orders in each group. | notebook cell 15 |
| **54% of late orders get 1 star, against 7% on time** | How often a late order ends in the worst review. | 3,431 one-star / 6,381 reviewed late orders = 53.8%. On time: 5,920 / 89,443 = 6.6%. The notebook prints 53.8% and 6.6%; the counts behind them were recomputed from `output/fact_sales.csv`. | notebook cell 30 ("1 star, late") |
| **Top 10% of sellers (297 of 2,970) bring 67.1%** | A small group of sellers carries most of the revenue. | 2,970 sellers sold something. 10% of 2,970 = 297 (rounded up). Their revenue / all revenue = 67.1%. The setting is `report.top_sellers_percent: 10`. The notebook prints 297, 2,970 and 67.1%; their sum, 8,873,076.37, was recomputed. | notebook cell 20 |
| **Top 10 of 74 categories bring 62.4%** | The same for product categories. | Add the revenue of the ten rows in cell 18 (8,254,334.23) / 13,221,498.11 = 62.4%. Setting: `report.top_categories: 10`. | notebook cell 18 |
| **3.0% repeat buyers** | Customers who ordered a second time. | 2,801 people with 2 or more orders / 93,358 people = 3.0%. The notebook prints 3.00%; the 2,801 was recomputed. | notebook cell 12 |
| **AL: 21.4%** | The customer state with the highest late share: Alagoas. | 85 late / 397 dated orders to AL customers = 21.4%. The notebook prints 397 and 21.41; the 85 was recomputed. | notebook cell 16 |
| **6.8% of orders, more than half 1 star** | The README's first action. | 6.8% as above; "more than half" is the 53.8% of reviewed late orders with 1 star. | notebook cells 10, 30 |
| **Two thirds of revenue** | The README's second action. | The 67.1% of the top 297 sellers. | notebook cell 20 |
| **23 DAX measures** | The calculations in the Power BI report. | Counted in `powerbi/03-measures.dax`, which lists them by page; 2 of them are helpers used inside other measures. | `powerbi/03-measures.dax` |
| **Five pages, five security roles** | Overview, Sales, Categories, Sellers, Delivery; one role per seller region. | One role per distinct region in `regions.csv`, which has 5. | `powerbi/04-pages.md`, `powerbi/02-model.md` |
| **All 43 checks** | Values each card must show (C1 to C43). | Every Power BI card was compared with the notebook in Power BI Desktop on 2026-10-05. | `powerbi/06-checks.md` |

### The charts in the README

| Number | Where you see it | What it means |
|---|---|---|
| **Nov 2017: 988k** | revenue-by-month.png | The best month: 987,765.37 of revenue from orders placed in November 2017. The chart starts in Jan 2017, the year before the compare year. The data does not say why November is high. Notebook cell 13. |
| **7%, 3%, 8%, 20%, 62%** (on time) and **54%, 9%, 11%, 10%, 17%** (late) | reviews-on-time-vs-late.png | For each group, the share of reviewed orders at 1, 2, 3, 4 and 5 stars. Each group adds up to 100%. Drawn by cell 25; the notebook prints only the 1-star pair (cell 30); the others were read from the chart and recomputed. |
| **Top 10% of sellers: 67% of revenue** | seller-concentration.png | The same 67.1%, rounded to a whole number. The line adds sellers from largest to smallest; the dot is at 10% of sellers. Cell 26. |

Things that can look wrong but are not:

- **6.8% of orders are late, but 54% of late orders get 1 star.** Different bases. 6.8% is a share of all dated orders; 54% is a share of late orders that got a review.
- **The late base is 96,470, not 96,478.** 8 delivered orders have no delivery date, so they cannot be late or on time (status "No date").
- **2018 revenue (7.22M) is bigger than all of 2017 (5,962,902.01) by only 21%, not 145%.** The 145.1% compares 1 Jan to 29 Aug in both years, because 2018 stops on 29 Aug. The full 2017 figure is not printed by the notebook; it was recomputed. Adding Jan to Aug 2017 from the month table (cell 13) gives 2,993,456.13, more than 2,944,431.50, because the month table holds all of August and the comparison stops on 29 Aug: 30 and 31 Aug 2017 are 49,024.63 (recomputed).
- **Row counts shrink and grow between tables.** The items file has 112,650 rows but `fact_sales` 110,197: the 2,453 items of non-delivered orders are left out. `dim_customer` keeps all 99,441 customer rows, while only 96,478 bought and they are 93,358 people. `dim_product` keeps all 32,951 products and `dim_seller` all 3,095 sellers, though only 2,970 sellers sold something. Extra rows in a dimension do no harm: they just never match a sale.
- **99,224 reviews but fewer reviewed orders.** 551 reviews are extra reviews on an order that already has one; only the latest counts (cell 5). 646 delivered orders have no review at all, so the average review is over 95,832 orders (recomputed).
- **74 categories include "unknown".** 610 products have no category; they are shown as "unknown", which ranks 21st by revenue (recomputed), so it is not in the top 10. 2 category codes have no readable name and keep their code (cell 5).
- **Revenue by customer region and by seller region differ.** Southeast customers bought 8,648,409.57, Southeast sellers sold 10,354,931.00. Each view splits the same 13,221,498.11 in its own way, and each adds up to it (cell 22).
- **Rounding.** 67.1% shows as 67% on the chart and in the header, 145.1% as +145%, 62.4% as 62%. The exact values are in cell 30.
- **2016 is almost empty.** Only Sep, Oct and Dec 2016 have sales, 40,470.98 in all (recomputed), which is why the charts start in 2017.

### The diagrams

| Number | Where you see it | What it means |
|---|---|---|
| **8 CSV files: 7 store exports + regions.csv** | data-flow.svg | The input files, as in section 3. |
| **99,441 orders, 112,650 items, 99,224 reviews, 32,951 products, 3,095 sellers, 99,441 customers** | data-flow.svg | Rows read from each input file. Notebook cell 3. |
| **71 category names** | data-flow.svg | Rows in the category names file. The notebook does not print this count; it was counted from the file. |
| **27 regions** | data-flow.svg | Brazil's 26 states plus the Federal District, in `regions.csv`. Counted from the file, not printed by the notebook. |
| **96,478 sale_orders** | data-flow.svg | Orders with status `delivered`. Cell 6. |
| **110,197 fact_sales** | data-flow.svg, data-model.svg | One row per item of a delivered order. Cell 8. |
| **32,951, 3,095, 99,441** | data-flow.svg, data-model.svg | Rows in `dim_product`, `dim_seller`, `dim_customer`: every product, seller and customer row, sold or not. Cell 8. |
| **1 report_settings row** | data-flow.svg, data-model.svg | One row holding the two top-N values (10 and 10) from `client.yaml`. Hidden in the report and joined to nothing. |
| **1,096 days** | data-model.svg | Rows in `dim_date`: 1 Jan 2016 to 31 Dec 2018, whole years (366 + 365 + 365). Built in DAX (`powerbi/02-model.md`), checked as C2 in `06-checks.md`; not printed by the notebook. |
| **23 measures, in 6 display folders** | data-model.svg, how-it-works.svg | See section 2. |
| **1 to \*** | data-model.svg | One dimension row links to many fact rows: one seller has many items sold. |
| **3 charts** | data-flow.svg | The three PNG files in `docs/` the notebook draws. |
| **1 to 6** | how-it-works.svg | The six steps: load, clean, model, measure, report, secure. |
| **+145%, 62%, 67%, 93,358, 3%, 2.27, 4.29, 5 roles** | mental-model.svg | The same numbers as the results table above, rounded. |
| **96,478, +145.1%, 6.8%, 2.27, 4.29** | header.svg | The same numbers as the results table above. |

## 5. What the results mean for the business

- **The business is growing fast.** 2018 revenue was up 145.1% on the same days of 2017. The month chart shows the climb through 2017 and a flatter line in 2018.
- **Late delivery is the clearest problem.** Only 6.8% of orders arrive late, but more than half of the reviewed late orders get 1 star, against 7% of on-time orders. Average review falls from 4.29 to 2.27. Each late order is a likely bad review.
- **Some states are hit much harder.** 21.4% of orders to AL arrive late, more than three times the average. The Delivery page shows the ten worst states.
- **Revenue depends on a few sellers.** 297 sellers bring two thirds of revenue. Losing even a few of them would show in the total.
- **Customers rarely come back.** Only 3.0% of customers ordered twice, so almost all growth is paid for by winning new customers.
- **These are patterns, not proven causes.** The data shows that late orders review badly; it does not prove that lateness alone caused each bad review.

## 6. Interview questions you can expect

**Explain the project in 30 seconds.**
A marketplace had its orders, items, sellers, customers and reviews in separate exports, so nobody could see growth, what sells, or what late delivery costs on one page. I wrote one Python notebook that checks the files, applies the rules once and writes a star schema, and built a five-page Power BI report with 23 DAX measures and row-level security by region. A SQL check proves the main totals. Result: 2018 up 145.1% on the same days of 2017, late orders average 2.27 stars against 4.29, and the top 10% of sellers bring 67% of revenue.

**Why one row per item and not per order?**
Revenue, product and seller exist per item, and one order can hold items from several sellers. At order grain I could not say which seller or category sold what. The cost is that order facts (late, review) repeat on each item, so those measures reduce to one row per order before they average.

**How do you know the numbers are right?**
Three ways. The notebook's health check stops on a duplicate id or a key that points to nothing. `sql/checks.sql` computes revenue, orders, customers, late %, average review and growth again with DuckDB, straight from the input files, and the notebook stops if any value differs. And `powerbi/06-checks.md` lists 43 values the report must show; all were compared in Power BI Desktop.

**Why is there no database?**
The data is about 110 thousand sale rows, which fits in memory, and the client sends files. A notebook and CSV files are the simplest thing that works. DuckDB runs inside Python only for the SQL cross-check. With a live source and daily loads, I would put it in a warehouse.

**Why are the rules in the notebook and not in Power Query or DAX?**
So they are written once. Which orders are sales, when an order is late, which review counts and the regions are all decided in one place from `client.yaml`. Power Query only reads the result, so the notebook and the report cannot disagree.

**Why compare with the same days last year?**
The data stops on 29 Aug 2018. Comparing eight months of 2018 with all twelve of 2017 would show about +21% instead of +145.1%. The `Date With Sales` flag in the date table stops last year on the same day.

**Why customer `person_id` and not `customer_id`?**
In this data `customer_id` is one per order, so counting it gives 96,478 "customers". `person_id` is the same for every order of one person, which gives 93,358 people and makes the 3.0% repeat rate possible to measure.

**Why does each order keep only its latest review?**
Some orders have more than one review (551 extra). Averaging all of them would count those orders twice. The latest answered one is the customer's final opinion; on a tie the higher score wins, so the rule is fixed and repeatable.

**Why static security roles per seller region?**
There are only five regions, so five roles with one filter each are simple to read and test. With many managers or changing assignments, I would use one role with a table that maps each user to a region.

**How would you set it up for a real client?**
Change `config/client.yaml` (names, file names, column headers, the sale statuses, the late threshold, the top-N values, colours), put their files in `data/input/`, run `python config.py`, the notebook, `theme.py` and `build_pbip.py`. No code changes.

## 7. Limits, in plain words

- There is no product cost in the data, so the report shows revenue and freight but no profit or margin.
- Only delivered orders count. Revenue here is delivered revenue, not everything customers ordered.
- "Late" compares the delivery date with the promised date, days only. An order delivered in the evening of its promised day counts as on time.
- 2018 stops on 29 Aug and 2016 has only three months, so whole-year comparisons are not possible.
- Some state figures rest on few orders: AL's 21.4% is 85 of 397 orders.
- Late delivery and bad reviews go together in the data, but the data cannot prove one causes the other.
- The report reads files exported once. New data needs the notebook to run again and the report to refresh.
