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
| `fact_sales` | One order item of a delivered order | `order_id` + `order_item_id` | 110,197 |
| `dim_date` | One day, 1 Jan 2016 to 31 Dec 2018 | `Date` | 1,096 |
| `dim_product` | One product | `product_id` | 32,951 |
| `dim_seller` | One seller | `seller_id` | 3,095 |
| `dim_customer` | One customer address (`customer_id`) | `customer_id` | 99,441 |
| `_Measures` | Holds the measures, no data | | 1 |

`order_id`, `delivery_status` and `review_score` stay in `fact_sales` as degenerate attributes: they describe the
order, have no table of their own, and the delivery page uses them as chart axes.

## The date table

**Modeling → New table**, paste:

```dax
dim_date =
VAR FirstYear = YEAR ( MIN ( fact_sales[order_date] ) )
VAR LastYear = YEAR ( MAX ( fact_sales[order_date] ) )
VAR LastSaleDate = MAX ( fact_sales[order_date] )
RETURN
    ADDCOLUMNS (
        CALENDAR ( DATE ( FirstYear, 1, 1 ), DATE ( LastYear, 12, 31 ) ),
        "Year", YEAR ( [Date] ),
        "Month Number", MONTH ( [Date] ),
        "Month", FORMAT ( [Date], "mmm" ),
        "Year Month", FORMAT ( [Date], "mmm yyyy" ),
        "Year Month Number", YEAR ( [Date] ) * 100 + MONTH ( [Date] ),
        "Date With Sales", [Date] <= LastSaleDate
    )
```

- Whole years (2016 to 2018), as time intelligence needs.
- `Date With Sales` is TRUE up to the last order date (29 Aug 2018). `Revenue LY` uses it so 2018 is compared with
  the same days of 2017, not with the whole of 2017.
- **Table tools → Mark as date table → Date column: `Date`.**
- Set the data types: `Date` = Date, `Year`, `Month Number`, `Year Month Number` = Whole number,
  `Date With Sales` = True/False.

## The measures table

**Home → Enter data**, leave one empty column, name the table `_Measures`, **Load**. After you paste the first
measure into it (file `03-measures.dax`), hide the empty `Column1`; the table moves to the top of the field list.

## Relationships

**Modeling → Manage relationships → New**, four times. Delete any relationship Power BI created by itself first.

| From (many) | To (one) | Cardinality | Cross-filter direction | Active |
|---|---|---|---|---|
| `fact_sales[order_date]` | `dim_date[Date]` | Many to one | Single | Yes |
| `fact_sales[product_id]` | `dim_product[product_id]` | Many to one | Single | Yes |
| `fact_sales[seller_id]` | `dim_seller[seller_id]` | Many to one | Single | Yes |
| `fact_sales[customer_id]` | `dim_customer[customer_id]` | Many to one | Single | Yes |

## Hide these columns

Report users pick fields from the dimensions and use the measures, so the keys and raw amounts are hidden
(right-click → **Hide in report view**).

| Table | Hidden columns |
|---|---|
| `fact_sales` | `order_id`, `order_item_id`, `order_date`, `product_id`, `seller_id`, `customer_id`, `price`, `freight_value`, `delivery_days` |
| `dim_date` | `Month Number`, `Year Month Number`, `Date With Sales` |
| `dim_seller` | `seller_id` |
| `dim_customer` | `customer_id`, `customer_unique_id` |

Visible in `fact_sales`: `delivery_status` and `review_score` only.

## Sort-by columns

Select the column, then **Column tools → Sort by column**:

| Column | Sort by |
|---|---|
| `dim_date[Month]` | `dim_date[Month Number]` |
| `dim_date[Year Month]` | `dim_date[Year Month Number]` |

## Formats and summarisation

- `fact_sales[review_score]`, `dim_date[Year]`: **Column tools → Summarization → Don't summarize**.
- `dim_date[Date]`: format `dd mmm yyyy`.
- Measures carry their own format strings (see `03-measures.dax`).

## Display folders

Select a measure → **Properties pane → Display folder**. The folders match the headings in `03-measures.dax`:
`Sales`, `Orders and customers`, `Delivery`, `Reviews`, `Categories`, `Sellers`.

## Row-level security

Each regional manager sees only the sellers in their region. **Modeling → Manage roles → New**, five times:

| Role | Table | DAX filter |
|---|---|---|
| `Seller region - North` | `dim_seller` | `[seller_region] = "North"` |
| `Seller region - Northeast` | `dim_seller` | `[seller_region] = "Northeast"` |
| `Seller region - Center-West` | `dim_seller` | `[seller_region] = "Center-West"` |
| `Seller region - Southeast` | `dim_seller` | `[seller_region] = "Southeast"` |
| `Seller region - South` | `dim_seller` | `[seller_region] = "South"` |

The filter flows from `dim_seller` to `fact_sales`, so every page shows only that region's sales. Test with
**Modeling → View as → (role)**; the expected totals are in `06-checks.md`. After publishing, people or groups are
added to each role in the Power BI service (dataset → Security).
