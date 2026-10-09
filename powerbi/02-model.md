# 2. Model

A star schema: one fact table in the middle, four dimensions around it, every relationship one-to-many with the
filter flowing one way, from the dimension to the fact.

```
                 dim_date
                    │ 1
                    │
   dim_product 1 ── * fact_sales * ── 1 dim_seller
                    │
                    │ *
                    │ 1
               dim_customer
```

## Tables

| Table | Grain | Key | Rows |
|---|---|---|---|
| `fact_sales` | One order item of a sale order (`rules.sale_statuses`) | `order_id` + `item_no` | `06-checks.md` C1 |
| `dim_date` | One day, `report.date_start` to `report.date_end` in `config/client.yaml` | `Date` | C2 |
| `dim_product` | One product | `product_id` | C3 |
| `dim_seller` | One seller | `seller_id` | C4 |
| `dim_customer` | One customer address (`customer_id`) | `customer_id` | C5 |
| `report_settings` | One row: the top-N values from `config/client.yaml` | | 1 |
| `_Measures` | Holds the measures, no data | | 1 |

`order_id`, `delivery_status` and `review_score` stay in `fact_sales` as degenerate attributes: they describe the
order, have no table of their own, and the delivery page uses them as chart axes.

## The date table

**Modeling → New table**, paste:

```dax
dim_date =
VAR FirstDay = DATE ( 2016, 1, 1 )
VAR LastDay = DATE ( 2018, 12, 31 )
VAR LastSaleDate = MAX ( fact_sales[order_date] )
RETURN
    ADDCOLUMNS (
        CALENDAR ( FirstDay, LastDay ),
        "Year", YEAR ( [Date] ),
        "Month Number", MONTH ( [Date] ),
        "Month", FORMAT ( [Date], "mmm" ),
        "Year Month", FORMAT ( [Date], "mmm yyyy" ),
        "Year Month Number", YEAR ( [Date] ) * 100 + MONTH ( [Date] ),
        "Date With Sales", [Date] <= LastSaleDate
    )
```

- `FirstDay` and `LastDay` are `report.date_start` and `report.date_end` in `config/client.yaml`, whole years, as
  time intelligence needs. `build_pbip.py` writes them in from the config; when you paste by hand, type the config's
  two dates. The range is never read from `fact_sales`, so the table is not built from the fact, and the notebook
  stops if an order date falls outside it.
- `Date With Sales` is TRUE up to the last order date. `Revenue LY` uses it, so when the data stops inside a year
  (the demo stops on 29 Aug 2018) that year is compared with the same days of the year before, not the whole year.
  `LastSaleDate` is the only read of `fact_sales`: it flags days for display, it never sets the range.
- **Table tools → Mark as date table → Date column: `Date`.**
- Set the data types: `Date` = Date, `Year`, `Month Number`, `Year Month Number` = Whole number,
  `Date With Sales` = True/False.

## The measures table

**Home → Enter data**, leave one empty column, name the table `_Measures`, **Load**. After you paste the first
measure into it (file `03-measures.dax`), hide the empty `Column1`; the table moves to the top of the field list.

## Relationships

**Modeling → Manage relationships → New**, four times. Delete any relationship Power BI created by itself first.

| From (many) | To (one) | Cardinality | Cross-filter direction | Active | Why |
|---|---|---|---|---|---|
| `fact_sales[order_date]` | `dim_date[Date]` | Many to one | Single | Yes | Every time filter and `Revenue LY` go through the date table |
| `fact_sales[product_id]` | `dim_product[product_id]` | Many to one | Single | Yes | Category charts and tables filter the sales |
| `fact_sales[seller_id]` | `dim_seller[seller_id]` | Many to one | Single | Yes | Carries the row-level security filter to every sale |
| `fact_sales[customer_id]` | `dim_customer[customer_id]` | Many to one | Single | Yes | Customer region and state filter the sales |

No both-direction filters and no inactive relationships: one path from each dimension to the fact keeps every
total unambiguous.

## Design choices

| Choice | Why |
|---|---|
| Fact table at order-item grain | Revenue, category and seller exist per item; an order can hold items from several sellers |
| Order-level columns repeated on each item | Avoids a second fact table; measures summarise to one row per order before averaging |
| Date table in DAX, whole years | Time intelligence (`DATEADD`) needs a continuous, complete calendar |
| `Date With Sales` flag | When the data ends inside a year, last year must stop on the same day |
| Separate `_Measures` table | All measures in one place, apart from the columns |
| Keys and raw amounts hidden | Report users use measures, so nobody sums `price` by hand or drags an id into a chart |
| Static roles per region | One filter per region in the regions file: simpler than a user-to-region mapping table |
| Rules applied once, in the notebook | Sales statuses, the late rule, the latest review and the regions come from `config/client.yaml`; Power Query only reads the result, so the report and the notebook cannot disagree |
| `report_settings` table | The top-N values reach DAX from the config, so no measure holds a client number |

## Hide these columns

Report users pick fields from the dimensions and use the measures, so the keys and raw amounts are hidden
(right-click → **Hide in report view**).

| Table | Hidden columns |
|---|---|
| `fact_sales` | `order_id`, `item_no`, `order_date`, `product_id`, `seller_id`, `customer_id`, `price`, `freight`, `delivery_days` |
| `dim_date` | `Month Number`, `Year Month Number`, `Date With Sales` |
| `dim_seller` | `seller_id` |
| `dim_customer` | `customer_id`, `person_id` |
| `report_settings` | the whole table (right-click the table → **Hide in report view**) |

Visible in `fact_sales`: `delivery_status` and `review_score` only.

## Sort-by columns

Select the column, then **Column tools → Sort by column**:

| Column | Sort by |
|---|---|
| `dim_date[Month]` | `dim_date[Month Number]` |
| `dim_date[Year Month]` | `dim_date[Year Month Number]` |

## Formats and summarisation

Select the column, then **Column tools**:

| Column | Format | Summarization | Why |
|---|---|---|---|
| `dim_date[Date]` | `dd mmm yyyy` | | Readable dates in tooltips |
| `dim_date[Year]` | Whole number, no thousands separator | Don't summarize | Shows 2018, not 2,018, and never adds years up |
| `fact_sales[review_score]` | Whole number | Don't summarize | A score is a label on the axis, not a number to add |
| `fact_sales[delivery_days]` | Whole number | Don't summarize | Hidden; only `Average Delivery Days` uses it |
| `fact_sales[price]`, `fact_sales[freight]` | Decimal, `client.decimals` places | Sum | Hidden; only the measures use them |
| All other columns | as loaded | Don't summarize | Text, ids and labels |

Data category stays **Uncategorized** for every column: the report has no maps.
Measures carry their own format strings (see `03-measures.dax`).

## Display folders

Select a measure → **Properties pane → Display folder**. The folders match the headings in `03-measures.dax`:
`Sales`, `Orders and customers`, `Delivery`, `Reviews`, `Categories`, `Sellers`.

## Row-level security

Each regional manager sees only the sellers in their region. **Modeling → Manage roles → New**, once for each
distinct `region` in the regions file (`inputs.regions`; the demo has five, listed in `06-checks.md`):

| Role | Table | DAX filter |
|---|---|---|
| `Seller region - <region>` | `dim_seller` | `[seller_region] = "<region>"` |

The filter flows from `dim_seller` to `fact_sales`, so every page shows only that region's sales. Test with
**Modeling → View as → (role)**; the expected totals are in `06-checks.md`. After publishing, people or groups are
added to each role in the Power BI service (dataset → Security).
