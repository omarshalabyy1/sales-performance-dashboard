# Sales performance dashboard

**96,478 orders: orders that arrived late scored 2.27 stars against 4.29 on time, and the top 10% of sellers brought 67% of revenue.**

A Power BI report built end to end: raw files cleaned in Power Query, a star schema, 23 DAX measures, five pages
and row-level security by region. A Python notebook computes every number first, so the report can be checked
against it.

## The problem

An online marketplace sells through about three thousand independent sellers. Orders, items, sellers, customers and
reviews come out as separate exports, so nobody can answer on one page:

- Are we growing against last year?
- What sells, and who sells it?
- What do late deliveries cost us in customer reviews?

Every report starts with a day of cleaning, and the totals never agree.

## The solution

![How it works](docs/how-it-works.svg)

One model answers five questions: when, what sold, who sold it, who bought it, and how the order went. Each
dimension answers one of them; the fact table in the middle answers the last.

![Five questions, one star](docs/mental-model.svg)

## What the numbers say

| | |
|---|---|
| Revenue (delivered orders, Sep 2016 to Aug 2018) | 13,221,498 from 96,478 orders and 93,358 customers |
| Growth | 2018 revenue up **145.1%** on the same days of 2017 (7.22M against 2.94M) |
| Late deliveries | **6.8%** of orders arrived after the estimated date |
| What late costs | late orders average **2.27** stars against **4.29** on time; **54%** of late orders get 1 star, against 7% on time |
| Seller concentration | the top 10% of sellers (297 of 2,970) bring **67.1%** of revenue |
| Category concentration | the top 10 of 74 categories bring **62.4%** of revenue |
| Repeat buyers | only **3.0%** of customers ordered a second time |

![Revenue by month](docs/revenue-by-month.png)

![Review scores, on time against late](docs/reviews-on-time-vs-late.png)

![Seller concentration](docs/seller-concentration.png)

What a manager does with it:

1. **Fix late deliveries first.** They are 6.8% of orders but more than half of them end in a 1-star review.
   The Sellers page shows which sellers deliver late most often; the Delivery page shows the states where orders
   arrive late most (AL: 21.4%).
2. **Look after the top 297 sellers.** Two thirds of revenue depends on them.
3. **Win the second order.** With 3% of customers coming back, almost all growth is paid for with new customers.

These are patterns in the data, not proven causes: the report shows where to look.

## The report

| Page | Question it answers |
|---|---|
| Overview | How is the business doing overall? |
| Sales | Are we growing against last year, and where? |
| Categories | What sells? |
| Sellers | Who sells, and which sellers hurt the customer experience? |
| Delivery | How much does late delivery cost us in reviews? |

Five security roles (one per region) limit each regional manager to their own sellers.

Everything needed to build the report is in [`powerbi/`](powerbi/README.md), ready to copy and paste: every Power
Query step, the model, every measure, every visual with its position and fields, the theme, and the numbers each
page must show.

## How the numbers are checked

- [`analysis/analysis.ipynb`](analysis/analysis.ipynb) is the source of truth. It applies the same rules as Power
  Query, stops on broken keys or missing lookups, and computes every number above.
- [`sql/checks.sql`](sql/checks.sql) computes the main totals again in SQL, straight from the raw files; the
  notebook asserts that both agree.
- [`powerbi/06-checks.md`](powerbi/06-checks.md) lists the value every card must show, and the revenue each
  security role must see.

Rules used everywhere: a sale is an item of a delivered order; revenue is the item price, with freight shown on its
own; an order is late when it arrives after the estimated date (dates only); each order keeps its latest review.

## Run it

```bash
pip install -r requirements.txt
```

Put the data files in `data/raw/` (see "Data" below), then:

```bash
cd analysis
jupyter nbconvert --to notebook --execute --inplace analysis.ipynb
```

Then build the report with [`powerbi/README.md`](powerbi/README.md).

```
data/raw/      the seven CSV files (not in the repo)
analysis/      the notebook: health check, model tables, every number, the charts
sql/           the SQL cross-check
docs/          the diagrams and charts used here
powerbi/       the step-by-step build, the theme, the checks, and the report once built
```

## Data

The [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
on Kaggle: about 100,000 orders placed on the Olist marketplace from 2016 to 2018, licensed CC BY-NC-SA 4.0.
Amounts are in Brazilian reais. Seven of its files are used (orders, order items, products, sellers, customers,
reviews, category names); the data has no product cost, so the report shows revenue and freight but no margin.

Download it from that page and unzip it into `data/raw/`, or with the Kaggle command-line tool:

```bash
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
```
