<p align="center">
  <img width="100%" src="docs/header.svg" alt="Sales performance dashboard: 96,478 orders. Orders that arrived late scored 2.27 stars against 4.29 on time, and the top 10% of sellers brought 67% of revenue.">
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1200&color=2DD4BF&center=true&vCenter=true&width=760&lines=96%2C478+orders%2C+five+Power+BI+pages;Late+orders%3A+2.27+stars%2C+on+time%3A+4.29;Top+10%25+of+sellers%3A+67%25+of+revenue" alt="96,478 orders, five Power BI pages">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Power_BI-DAX_%26_Power_Query-F2C811?style=for-the-badge&logo=powerbi&logoColor=black" alt="Power BI, DAX and Power Query">
  <img src="https://img.shields.io/badge/Python-pandas-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python and pandas">
  <img src="https://img.shields.io/badge/DuckDB-Star_schema-FFF000?style=for-the-badge&logo=duckdb&logoColor=black" alt="DuckDB star schema">
</p>

> 📖 **New to data?** [The project explained, from zero](docs/explained.md): every word, every number and the interview questions, in plain words.

<h3 align="center">96,478 orders: orders that arrived late scored 2.27 stars against 4.29 on time,<br>and the top 10% of sellers brought 67% of revenue.</h3>

A Power BI report built end to end, with no database: one Python notebook checks and cleans the input files and
writes a star schema, and Power BI adds 23 DAX measures, five pages and row-level security by region. The notebook
computes every number first, so the report can be checked against it.

Every client value (names, file and column names, rules, colours) lives in `config/client.yaml` and the input files
in `data/input/`.

## The problem

An online marketplace sells through about three thousand independent sellers. Orders, items, sellers, customers and
reviews come out as separate exports, so nobody can answer on one page:

- Are we growing against last year?
- What sells, and who sells it?
- What do late deliveries cost us in customer reviews?

Every report starts with a day of cleaning, and the totals never agree.

## 🛠️ The solution

![How it works, in six layers: Bronze, the input files as received; Silver, mapped, typed and checked; Gold, the rules; Semantic, the star schema; Analytical, 23 DAX measures; Reporting, five pages](docs/how-it-works.svg)

One model answers five questions: when, what sold, who sold it, who bought it, and how the order went. Each
dimension answers one of them; the fact table in the middle answers the last.

![Five questions, one star](docs/mental-model.svg)

## 📈 What the numbers say

<p align="center">
  <img src="https://user-images.githubusercontent.com/74038190/221352987-68da234d-4d62-4e9d-9d7f-098dc657c2dc.gif" width="100" alt="Moving chart">
</p>

| | |
|---|---|
| Revenue (delivered orders, Sep 2016 to Aug 2018) | 13,221,498 from 96,478 orders and 93,358 customers |
| Growth | 2018 revenue up **145.1%** on the same days of 2017 (7.22M against 2.94M) |
| Late deliveries | **6.8%** of orders arrived after the estimated date |
| What late costs | late orders average **2.27** stars against **4.29** on time; **54%** of reviewed late orders get 1 star, against 7% of reviewed on-time orders |
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

## 📊 The report

| Page | Question it answers |
|---|---|
| Overview | How is the business doing overall? |
| Sales | Are we growing against last year, and where? |
| Categories | What sells? |
| Sellers | Who sells, and which sellers hurt the customer experience? |
| Delivery | How much does late delivery cost us in reviews? |

Five security roles (one per region) limit each regional manager to their own sellers.

The report is [`powerbi/sales-performance.pbip`](powerbi/README.md): open it in Power BI Desktop and click
**Refresh now**. It is written by `powerbi/build_pbip.py` from the build pack in [`powerbi/`](powerbi/README.md), which
also lets you build it by hand: every Power Query step, the model, every measure, every visual with its position and
fields, the theme, and the numbers each page must show. All 43 checks were run against the model in Power BI Desktop.

### 📸 Screenshots

**Overview:** revenue, orders, customers, late deliveries and reviews at a glance.

![Overview page](powerbi/screenshots/01-overview.png)

**Sales:** 2018 against the same days of 2017, month by month and by state.

![Sales page](powerbi/screenshots/02-sales.png)

**Categories:** what sells, and which categories review badly or arrive late.

![Categories page](powerbi/screenshots/03-categories.png)

**Sellers:** the sellers behind the revenue, and those who deliver late and review badly.

![Sellers page](powerbi/screenshots/04-sellers.png)

**Delivery:** how late delivery drags reviews down, and where it happens.

![Delivery page](powerbi/screenshots/05-delivery.png)

## 🔍 How the numbers are checked

- [`analysis/analysis.ipynb`](analysis/analysis.ipynb) is the source of truth. It applies the rules once, from
  `config/client.yaml`, stops on broken keys or missing lookups, writes the tables Power BI reads, and computes
  every number above.
- [`sql/checks.sql`](sql/checks.sql) computes the main totals again in SQL, straight from the input files; the
  notebook asserts that both agree.
- [`powerbi/06-checks.md`](powerbi/06-checks.md) lists the value every card must show, and the revenue each
  security role must see.

Rules for the demo (keys in `config/client.yaml`): a sale is an item of a delivered order; revenue is the item
price, with freight shown on its own; an order is late when it arrives after the estimated date (dates only); each
order keeps its latest review.

## ▶️ Run it

<p align="center">
  <img src="https://user-images.githubusercontent.com/74038190/212284087-bbe7e430-757e-4901-90bf-4cd2ce3e1852.gif" width="100" alt="Code">
</p>

```bash
pip install -r requirements.txt
```

Put the data files in `data/input/` (see "Data" below), check them, then run the notebook and write the theme:

```bash
python config.py
```

```bash
cd analysis
jupyter nbconvert --to notebook --execute --inplace analysis.ipynb
```

```bash
python theme.py
```

Then build the report with [`powerbi/README.md`](powerbi/README.md).

```
config/client.yaml   every client value: names, file and column names, rules, top-N, colours
config.py            load_config() and the input checks (python config.py)
theme.py             writes powerbi/05-theme.json from the config
data/input/          the input files (only regions.csv is in the repo) and their guide
analysis/            the notebook: health check, model tables, every number, the charts
output/              the Semantic layer: the tables the notebook writes for Power BI (not in the repo)
sql/                 the SQL cross-check
docs/                the diagrams and charts used here
powerbi/             the report (.pbip) and build_pbip.py, the step-by-step build, the theme, the checks, the screenshots
```

## 🏗️ For engineers

The steps are named after the six layers. There is no database: each layer is a file, a notebook section or a part of the Power BI report.

| Layer | In this repo |
|---|---|
| Bronze layer | The input files in `data/input/`, as received; the notebook only reads them |
| Silver layer | Notebook sections 1 and 2: the mapped columns, typed, with every id and link checked; no row is dropped |
| Gold layer | The rules, applied once: delivered orders, the late rule, each order's latest review, each state's region (sections 2 and 3) |
| Semantic layer | `fact_sales` and the three dimensions in `output/`, written in section 3; Power BI adds `dim_date` and the five region roles |
| Analytical layer | The 23 DAX measures (`powerbi/03-measures.dax`) and the numbers in notebook sections 4 to 9 |
| Reporting layer | The five Power BI pages and the three README charts (section 10) |

Every table, the tables it is built from, and its row count after one run:

![Data flow, table by table](docs/data-flow.svg)

The star schema Power BI builds from the files in `output/`:

![The star schema](docs/data-model.svg)

## 🗂️ Data

The [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
on Kaggle: about 100,000 orders placed on the Olist marketplace from 2016 to 2018, licensed CC BY-NC-SA 4.0.
Amounts are in Brazilian reais. Seven of its files are used (orders, order items, products, sellers, customers,
reviews, category names); the data has no product cost, so the report shows revenue and freight but no margin.

Download it from that page and unzip it into `data/input/`, or with the Kaggle command-line tool:

```bash
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/input --unzip
```

`data/input/regions.csv` (Brazil's 26 states and the Federal District, in their five official regions) is ours and is in the repo.

<p align="center">
  <img width="100%" src="docs/footer.svg" alt="Know what sells, who sells it, and what late costs.">
</p>
