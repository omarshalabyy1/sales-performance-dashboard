# 1. Power Query

Seven queries: one parameter, two staging queries that stay out of the model, and four tables that load.
The rules match the notebook exactly (`analysis/analysis.ipynb`, section 3).

| Query | Loads to the model | What it is |
|---|---|---|
| `DataFolder` | No | The folder that holds the CSV files |
| `stg_orders` | No | Delivered orders with dates, delivery days and on time / late |
| `stg_reviews` | No | The latest review of each order |
| `fact_sales` | Yes | One row per order item, the fact table |
| `dim_product` | Yes | One row per product, with its category |
| `dim_seller` | Yes | One row per seller, with state and region |
| `dim_customer` | Yes | One row per customer address, with state and region |

## Before you start

1. Open Power BI Desktop, then **File → Options and settings → Options → Current file → Data load** and untick
   **Auto date/time**. The model has its own date table.
2. **Home → Transform data** opens Power Query.
3. For every query below: **Home → New source → Blank query**, rename it (right-click → Rename) to the name in the
   heading, then **Home → Advanced editor**, select all, paste the code block, **Done**.
4. For the two staging queries: right-click the query → untick **Enable load**. They turn italic.

Every file is read as UTF-8 (`Encoding = 65001`) so accented city names stay correct, and with
`QuoteStyle.Csv` so review texts that contain line breaks do not split rows. Types are set with the `en-US` culture
so `58.90` is read as fifty-eight point nine on any Windows language setting.

## DataFolder (parameter)

**Home → Manage parameters → New parameter**: name `DataFolder`, type **Text**, current value = the full path of
this repo's `data\raw\` folder, ending with a backslash. Or paste this in a blank query and change the path:

```m
"C:\Users\you\GitHub\sales-performance-dashboard\data\raw\" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

## stg_orders (staging, do not load)

Keeps delivered orders only. The order date is the purchase date without the time. `delivery_days` counts whole days
from purchase to delivery. An order is late when the delivery date is after the estimated date (dates only). Eight
delivered orders have no delivery date: they stay in the sales with `delivery_status = "No date"`.

```m
let
    Source = Csv.Document(
        File.Contents(DataFolder & "olist_orders_dataset.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Delivered = Table.SelectRows(PromotedHeaders, each [order_status] = "delivered"),
    ChangedType = Table.TransformColumnTypes(
        Delivered,
        {
            {"order_id", type text},
            {"customer_id", type text},
            {"order_purchase_timestamp", type datetime},
            {"order_delivered_customer_date", type datetime},
            {"order_estimated_delivery_date", type datetime}
        },
        "en-US"
    ),
    AddedOrderDate = Table.AddColumn(ChangedType, "order_date", each Date.From([order_purchase_timestamp]), type date),
    AddedDeliveryDays = Table.AddColumn(
        AddedOrderDate,
        "delivery_days",
        each if [order_delivered_customer_date] = null then null
            else Duration.Days(Date.From([order_delivered_customer_date]) - [order_date]),
        Int64.Type
    ),
    AddedDeliveryStatus = Table.AddColumn(
        AddedDeliveryDays,
        "delivery_status",
        each if [order_delivered_customer_date] = null then "No date"
            else if Date.From([order_delivered_customer_date]) > Date.From([order_estimated_delivery_date]) then "Late"
            else "On time",
        type text
    ),
    Kept = Table.SelectColumns(AddedDeliveryStatus, {"order_id", "customer_id", "order_date", "delivery_days", "delivery_status"})
in
    Kept
```

Expected: **96,478 rows**.

## stg_reviews (staging, do not load)

Some orders were reviewed twice. `Table.Max` keeps the row answered last, so each order has one score.

```m
let
    Source = Csv.Document(
        File.Contents(DataFolder & "olist_order_reviews_dataset.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Kept = Table.SelectColumns(PromotedHeaders, {"order_id", "review_score", "review_answer_timestamp"}),
    ChangedType = Table.TransformColumnTypes(
        Kept,
        {{"order_id", type text}, {"review_score", Int64.Type}, {"review_answer_timestamp", type datetime}},
        "en-US"
    ),
    LatestPerOrder = Table.Group(
        ChangedType,
        {"order_id"},
        {{"review_score", each Table.Max(_, "review_answer_timestamp")[review_score], Int64.Type}}
    )
in
    LatestPerOrder
```

Expected: **98,673 rows** (one per reviewed order, all statuses).

## fact_sales (load)

Grain: **one row per order item** (`order_id` + `order_item_id`). The inner join to `stg_orders` drops items of
orders that were not delivered. Order-level columns (`delivery_days`, `delivery_status`, `review_score`) repeat on
every item of the same order; the measures count them once per order.

```m
let
    Source = Csv.Document(
        File.Contents(DataFolder & "olist_order_items_dataset.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Kept = Table.SelectColumns(PromotedHeaders, {"order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"}),
    ChangedType = Table.TransformColumnTypes(
        Kept,
        {
            {"order_id", type text},
            {"order_item_id", Int64.Type},
            {"product_id", type text},
            {"seller_id", type text},
            {"price", Currency.Type},
            {"freight_value", Currency.Type}
        },
        "en-US"
    ),
    JoinedOrders = Table.NestedJoin(ChangedType, {"order_id"}, stg_orders, {"order_id"}, "order", JoinKind.Inner),
    ExpandedOrders = Table.ExpandTableColumn(JoinedOrders, "order", {"customer_id", "order_date", "delivery_days", "delivery_status"}),
    JoinedReviews = Table.NestedJoin(ExpandedOrders, {"order_id"}, stg_reviews, {"order_id"}, "review", JoinKind.LeftOuter),
    ExpandedReviews = Table.ExpandTableColumn(JoinedReviews, "review", {"review_score"}),
    Typed = Table.TransformColumnTypes(
        ExpandedReviews,
        {
            {"customer_id", type text},
            {"order_date", type date},
            {"delivery_days", Int64.Type},
            {"delivery_status", type text},
            {"review_score", Int64.Type}
        }
    )
in
    Typed
```

Expected: **110,197 rows**.

## dim_product (load)

Grain: one row per product. The category is the English name, with underscores turned into spaces. Two categories
have no English name, so they keep the Portuguese one; 610 products have no category and get `unknown`.

```m
let
    Source = Csv.Document(
        File.Contents(DataFolder & "olist_products_dataset.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Kept = Table.SelectColumns(PromotedHeaders, {"product_id", "product_category_name"}),
    Names = Table.PromoteHeaders(
        Csv.Document(
            File.Contents(DataFolder & "product_category_name_translation.csv"),
            [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
        ),
        [PromoteAllScalars = true]
    ),
    JoinedNames = Table.NestedJoin(Kept, {"product_category_name"}, Names, {"product_category_name"}, "names", JoinKind.LeftOuter),
    ExpandedNames = Table.ExpandTableColumn(JoinedNames, "names", {"product_category_name_english"}),
    AddedCategory = Table.AddColumn(
        ExpandedNames,
        "category",
        each Text.Replace(
            if [product_category_name_english] <> null then [product_category_name_english]
            else if [product_category_name] <> "" then [product_category_name]
            else "unknown",
            "_",
            " "
        ),
        type text
    ),
    Final = Table.TransformColumnTypes(Table.SelectColumns(AddedCategory, {"product_id", "category"}), {{"product_id", type text}})
in
    Final
```

Expected: **32,951 rows**.

## dim_seller (load)

Grain: one row per seller. The region follows Brazil's five official regions; it drives the row-level security.
`seller_short_id` is the first 8 characters of the id, unique for every seller, used as the label in tables.

```m
let
    Source = Csv.Document(
        File.Contents(DataFolder & "olist_sellers_dataset.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Kept = Table.SelectColumns(PromotedHeaders, {"seller_id", "seller_city", "seller_state"}),
    ChangedType = Table.TransformColumnTypes(Kept, {{"seller_id", type text}, {"seller_city", type text}, {"seller_state", type text}}),
    AddedRegion = Table.AddColumn(
        ChangedType,
        "seller_region",
        each if List.Contains({"AC", "AP", "AM", "PA", "RO", "RR", "TO"}, [seller_state]) then "North"
            else if List.Contains({"AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"}, [seller_state]) then "Northeast"
            else if List.Contains({"DF", "GO", "MT", "MS"}, [seller_state]) then "Center-West"
            else if List.Contains({"ES", "MG", "RJ", "SP"}, [seller_state]) then "Southeast"
            else if List.Contains({"PR", "RS", "SC"}, [seller_state]) then "South"
            else "Unknown",
        type text
    ),
    AddedShortId = Table.AddColumn(AddedRegion, "seller_short_id", each Text.Start([seller_id], 8), type text)
in
    AddedShortId
```

Expected: **3,095 rows**, no `Unknown` region.

## dim_customer (load)

Grain: one row per `customer_id`. In this data a `customer_id` is one order's delivery address; the same person
keeps one `customer_unique_id` across orders, so **Customers** counts `customer_unique_id`.

```m
let
    Source = Csv.Document(
        File.Contents(DataFolder & "olist_customers_dataset.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Kept = Table.SelectColumns(PromotedHeaders, {"customer_id", "customer_unique_id", "customer_city", "customer_state"}),
    ChangedType = Table.TransformColumnTypes(
        Kept,
        {{"customer_id", type text}, {"customer_unique_id", type text}, {"customer_city", type text}, {"customer_state", type text}}
    ),
    AddedRegion = Table.AddColumn(
        ChangedType,
        "customer_region",
        each if List.Contains({"AC", "AP", "AM", "PA", "RO", "RR", "TO"}, [customer_state]) then "North"
            else if List.Contains({"AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"}, [customer_state]) then "Northeast"
            else if List.Contains({"DF", "GO", "MT", "MS"}, [customer_state]) then "Center-West"
            else if List.Contains({"ES", "MG", "RJ", "SP"}, [customer_state]) then "Southeast"
            else if List.Contains({"PR", "RS", "SC"}, [customer_state]) then "South"
            else "Unknown",
        type text
    )
in
    AddedRegion
```

Expected: **99,441 rows**, no `Unknown` region.

## Columns that load

What each loaded table must contain after **Close & apply** (no renames anywhere: the names are the source names).

| Table | Column | Type |
|---|---|---|
| `fact_sales` | `order_id` | Text |
| | `order_item_id` | Whole number |
| | `product_id` | Text |
| | `seller_id` | Text |
| | `price` | Fixed decimal number |
| | `freight_value` | Fixed decimal number |
| | `customer_id` | Text |
| | `order_date` | Date |
| | `delivery_days` | Whole number |
| | `delivery_status` | Text (`On time`, `Late`, `No date`) |
| | `review_score` | Whole number (1 to 5, blank when no review) |
| `dim_product` | `product_id` | Text |
| | `category` | Text |
| `dim_seller` | `seller_id` | Text |
| | `seller_city` | Text |
| | `seller_state` | Text |
| | `seller_region` | Text |
| | `seller_short_id` | Text |
| `dim_customer` | `customer_id` | Text |
| | `customer_unique_id` | Text |
| | `customer_city` | Text |
| | `customer_state` | Text |
| | `customer_region` | Text |

## Finish

**Home → Close & apply.** Then check the row counts in the Data view (bottom left shows the row count of the
selected table). If any count differs from the ones above, stop and compare that query with this file.
