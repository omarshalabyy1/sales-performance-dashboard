# 1. Power Query

Power BI reads the model tables the notebook writes to `output/`. The rules (which orders are sales, when an order
is late, which review counts, the regions) are applied once, in the notebook, from `config/client.yaml`; Power
Query only reads the files and sets the types. Run the notebook first (`08-build-checklist.md`, steps 1 to 4).

Six queries: one parameter and five tables that load.

| Query | Loads to the model | What it is |
|---|---|---|
| `OutputFolder` | No | The folder that holds the notebook's output files |
| `fact_sales` | Yes | One row per order item, the fact table |
| `dim_product` | Yes | One row per product, with its category |
| `dim_seller` | Yes | One row per seller, with state and region |
| `dim_customer` | Yes | One row per customer address, with state and region |
| `report_settings` | Yes (hidden) | One row: `report.top_categories` and `report.top_sellers_percent` from the config, read by two measures |

## Before you start

1. Open Power BI Desktop, then **File → Options and settings → Options → Current file → Data load** and untick
   **Auto date/time**. The model has its own date table.
2. **Home → Transform data** opens Power Query.
3. For every query below: **Home → New source → Blank query**, rename it (right-click → Rename) to the name in the
   heading, then **Home → Advanced editor**, select all, paste the code block, **Done**.

Every file is read as UTF-8 (`Encoding = 65001`) so accented city names stay correct, and types are set with the
`en-US` culture because the notebook writes dates as `YYYY-MM-DD` and decimals with a dot.

## OutputFolder (parameter)

**Home → Manage parameters → New parameter**: name `OutputFolder`, type **Text**, current value = the full path of
this repo's `output\` folder, ending with a backslash. Or paste this in a blank query and change the path:

```m
"C:\Users\you\GitHub\sales-performance-dashboard\output\" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

## fact_sales (load)

Grain: **one row per order item** (`order_id` + `item_no`). Order-level columns (`delivery_days`,
`delivery_status`, `review_score`) repeat on every item of the same order; the measures count them once per order.

```m
let
    Source = Csv.Document(
        File.Contents(OutputFolder & "fact_sales.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"order_id", type text},
            {"item_no", Int64.Type},
            {"order_date", type date},
            {"product_id", type text},
            {"seller_id", type text},
            {"customer_id", type text},
            {"price", Currency.Type},
            {"freight", Currency.Type},
            {"delivery_days", Int64.Type},
            {"delivery_status", type text},
            {"review_score", Int64.Type}
        },
        "en-US"
    )
in
    ChangedType
```

## dim_product (load)

```m
let
    Source = Csv.Document(
        File.Contents(OutputFolder & "dim_product.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"product_id", type text}, {"category", type text}}, "en-US")
in
    ChangedType
```

## dim_seller (load)

```m
let
    Source = Csv.Document(
        File.Contents(OutputFolder & "dim_seller.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"seller_id", type text},
            {"seller_city", type text},
            {"seller_state", type text},
            {"seller_region", type text},
            {"seller_short_id", type text}
        },
        "en-US"
    )
in
    ChangedType
```

## dim_customer (load)

`customer_id` is one order's delivery address; `person_id` is the same person across orders, so **Customers**
counts `person_id`.

```m
let
    Source = Csv.Document(
        File.Contents(OutputFolder & "dim_customer.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"customer_id", type text},
            {"person_id", type text},
            {"customer_city", type text},
            {"customer_state", type text},
            {"customer_region", type text}
        },
        "en-US"
    )
in
    ChangedType
```

## report_settings (load, hidden)

One row with the two top-N values from `config/client.yaml`, so the DAX never holds a client number.

```m
let
    Source = Csv.Document(
        File.Contents(OutputFolder & "report_settings.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedType = Table.TransformColumnTypes(
        PromotedHeaders,
        {{"top_categories", Int64.Type}, {"top_sellers_percent", Int64.Type}},
        "en-US"
    )
in
    ChangedType
```

## Columns that load

| Table | Column | Type |
|---|---|---|
| `fact_sales` | `order_id` | Text |
| | `item_no` | Whole number |
| | `order_date` | Date |
| | `product_id` | Text |
| | `seller_id` | Text |
| | `customer_id` | Text |
| | `price` | Fixed decimal number |
| | `freight` | Fixed decimal number |
| | `delivery_days` | Whole number (blank when there is no delivery date) |
| | `delivery_status` | Text (`On time`, `Late`, `No date`) |
| | `review_score` | Whole number (blank when there is no review) |
| `dim_product` | `product_id` | Text |
| | `category` | Text |
| `dim_seller` | `seller_id` | Text |
| | `seller_city` | Text |
| | `seller_state` | Text |
| | `seller_region` | Text |
| | `seller_short_id` | Text |
| `dim_customer` | `customer_id` | Text |
| | `person_id` | Text |
| | `customer_city` | Text |
| | `customer_state` | Text |
| | `customer_region` | Text |
| `report_settings` | `top_categories` | Whole number |
| | `top_sellers_percent` | Whole number |

## Finish

**Home → Close & apply.** Then check the row counts in the Data view (bottom left shows the row count of the
selected table) against `06-checks.md` (C1, C3, C4, C5): they must equal the notebook's section 3.
