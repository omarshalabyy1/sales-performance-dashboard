-- The main totals of the report, computed straight from the raw files with DuckDB.
-- Same rules as the notebook and Power Query: delivered orders only, dates without times,
-- late = delivered after the estimated date, the latest review per order.
-- Run from the repo root: duckdb -c ".read sql/checks.sql"

WITH orders AS (
    SELECT
        order_id,
        customer_id,
        CAST(order_purchase_timestamp AS DATE)      AS order_date,
        CAST(order_delivered_customer_date AS DATE) AS delivered_date,
        CAST(order_estimated_delivery_date AS DATE) AS estimated_date
    FROM 'data/raw/olist_orders_dataset.csv'
    WHERE order_status = 'delivered'
),
latest_review AS (
    SELECT order_id, arg_max(review_score, review_answer_timestamp) AS review_score
    FROM 'data/raw/olist_order_reviews_dataset.csv'
    GROUP BY order_id
),
sales AS (
    SELECT i.order_id, i.price, o.order_date
    FROM 'data/raw/olist_order_items_dataset.csv' AS i
    JOIN orders AS o USING (order_id)
),
order_facts AS (
    SELECT o.*, r.review_score, c.customer_unique_id
    FROM orders AS o
    LEFT JOIN latest_review AS r USING (order_id)
    JOIN 'data/raw/olist_customers_dataset.csv' AS c USING (customer_id)
    WHERE o.order_id IN (SELECT order_id FROM sales)
),
last_day AS (
    SELECT max(order_date) AS d FROM sales
)
SELECT
    (SELECT sum(price) FROM sales)                         AS revenue,
    (SELECT count(DISTINCT order_id) FROM sales)           AS orders,
    (SELECT count(DISTINCT customer_unique_id) FROM order_facts) AS customers,
    (SELECT avg(CASE WHEN delivered_date > estimated_date THEN 100.0 ELSE 0 END)
       FROM order_facts WHERE delivered_date IS NOT NULL)  AS late_pct,
    (SELECT avg(review_score) FROM order_facts)            AS avg_review,
    ((SELECT sum(price) FROM sales WHERE year(order_date) = 2018)
     / (SELECT sum(price) FROM sales, last_day
         WHERE order_date BETWEEN DATE '2017-01-01' AND CAST(d - INTERVAL 1 YEAR AS DATE))
     - 1) * 100                                            AS growth_pct;
