# Input files

What the client supplies, in this folder: eight CSV files (UTF-8, comma-separated, a header row). Each file's name
is set under `inputs` in `config/client.yaml`, and each header the code reads is set under `columns` (standard
name: the client's header). Extra columns are ignored; only the mapped ones are read.

`python config.py` (and the notebook's first cell) checks every file before anything is computed and stops with
one line naming the file and the problem. Dates are read as `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`; decimals use a
dot.

## Orders (`inputs.orders`)

One row per order.

| Standard column | Type | Demo header | Demo example |
|---|---|---|---|
| order_id | text, unique | order_id | 53cdb2fc8bc7dce0b6741e2150273451 |
| customer_id | text, in the customers file | customer_id | b0830fb4747a6c6d20dea0b8c802d7ef |
| status | text; the sale ones are listed in `rules.sale_statuses` | order_status | delivered |
| purchased_at | date and time | order_purchase_timestamp | 2018-07-24 20:41:37 |
| delivered_at | date and time, empty if not delivered | order_delivered_customer_date | 2018-08-07 15:27:45 |
| estimated_at | date and time promised to the customer | order_estimated_delivery_date | 2018-08-13 00:00:00 |

## Order items (`inputs.items`)

One row per item in an order.

| Standard column | Type | Demo header | Demo example |
|---|---|---|---|
| order_id | text, in the orders file | order_id | 00018f77f2f0320c557190d7a144bdd3 |
| item_no | whole number, unique within the order | order_item_id | 1 |
| product_id | text, in the products file | product_id | e5f2d52b802189ee658865ca93d83a8f |
| seller_id | text, in the sellers file | seller_id | dd7ddc04e1b6c2c614352b383efe2d36 |
| price | number, the item's sale price | price | 239.90 |
| freight | number, the freight charged for the item | freight_value | 19.93 |

## Products (`inputs.products`)

| Standard column | Type | Demo header | Demo example |
|---|---|---|---|
| product_id | text, unique | product_id | 3aa071139cb16b67ca9e5dea641aaa2f |
| category | text code, may be empty (shown as `unknown`) | product_category_name | artes |

## Sellers (`inputs.sellers`)

| Standard column | Type | Demo header | Demo example |
|---|---|---|---|
| seller_id | text, unique; its first 8 characters must also be unique (the label in tables) | seller_id | d1b65fc7debc3361ea86b5f14c68d2e2 |
| city | text | seller_city | mogi guacu |
| state | text, in the regions file | seller_state | SP |

## Customers (`inputs.customers`)

| Standard column | Type | Demo header | Demo example |
|---|---|---|---|
| customer_id | text, unique (one per order address) | customer_id | 18955e83d337fd6b2def6b18a428ac77 |
| person_id | text, the same for every order of one person | customer_unique_id | 290c77bc529b7ac935b93aa66c333dc3 |
| city | text | customer_city | sao bernardo do campo |
| state | text, in the regions file | customer_state | SP |

## Reviews (`inputs.reviews`)

Zero, one or more reviews per order; the latest answered one counts (on a tie, the higher score).

| Standard column | Type | Demo header | Demo example |
|---|---|---|---|
| order_id | text | order_id | a548910a1c6147796b98fdf73dbeba33 |
| score | whole number, 1 to 5 | review_score | 5 |
| answered_at | date and time | review_answer_timestamp | 2018-03-11 03:05:13 |

## Category names (`inputs.category_names`)

The name shown in the report for each category code. A code missing here is shown as the code itself.

| Standard column | Type | Demo header | Demo example |
|---|---|---|---|
| category | text, the code used in the products file | product_category_name | informatica_acessorios |
| name | text, the name to show (underscores become spaces) | product_category_name_english | computers_accessories |

## Regions (`inputs.regions`)

Written by us, not by the client's system: the region of every state that appears in the sellers or customers
file. The headers are fixed: `state`, `region`. One security role is made per region. The demo file
(`regions.csv`, committed) holds Brazil's 27 states in its five official regions.

| state | region |
|---|---|
| SP | Southeast |

## What stops the run

One line each, before anything is computed:

```
config/client.yaml is missing <key>
config/client.yaml is not valid YAML near line <n> (quote a value with # or :)
missing data/input/<file> (inputs.<name> in config/client.yaml)
data/input/<file>: missing column(s): <columns>
data/input/regions.csv: no region for state(s): <states>
rules.sale_statuses matches no order status
```

A broken key in the data (a duplicate order id, an item whose product is not in the products file) stops the
notebook's health check with one line naming the file and the column.

## The demo files

The demo uses seven files of the Brazilian E-Commerce Public Dataset by Olist (CC BY-NC-SA 4.0), which are not
committed: download them from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce into this folder (the
main README, "Data"). Only `regions.csv` is committed. CSV files here are ignored by git, so client data is never
committed.
