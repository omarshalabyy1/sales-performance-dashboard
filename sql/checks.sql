-- The main totals of the report, computed again in SQL with DuckDB, apart from the pandas code.
-- The notebook (section 11) makes one view per input file (orders, items, reviews, customers) with the
-- standard column names from config/client.yaml, and passes the rules as parameters:
-- $sale_statuses, $late_after_days, $compare_year.
-- Same rules as the notebook: sale statuses only, dates without times, late = delivered more than
-- $late_after_days days after the estimated date, the latest review per order (then the higher score).

WITH sale_orders AS (
    SELECT
        order_id,
        customer_id,
        CAST(purchased_at AS DATE) AS order_date,
        CAST(delivered_at AS DATE) AS delivered_date,
        CAST(estimated_at AS DATE) AS estimated_date
    FROM orders
    WHERE list_contains($sale_statuses, status)
),
latest_review AS (
    SELECT order_id, score
    FROM reviews
    QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY answered_at DESC, score DESC) = 1
),
sales AS (
    SELECT i.order_id, i.price, o.order_date
    FROM items AS i
    JOIN sale_orders AS o USING (order_id)
),
order_facts AS (
    SELECT o.*, r.score, c.person_id
    FROM sale_orders AS o
    LEFT JOIN latest_review AS r USING (order_id)
    JOIN customers AS c USING (customer_id)
    WHERE o.order_id IN (SELECT order_id FROM sales)
),
window_end AS (
    SELECT least(max(order_date), make_date($compare_year, 12, 31)) AS d FROM sales
)
SELECT
    (SELECT sum(price) FROM sales)                         AS revenue,
    (SELECT count(DISTINCT order_id) FROM sales)           AS orders,
    (SELECT count(DISTINCT person_id) FROM order_facts)    AS customers,
    (SELECT avg(CASE WHEN delivered_date > estimated_date + $late_after_days THEN 100.0 ELSE 0 END)
       FROM order_facts WHERE delivered_date IS NOT NULL)  AS late_pct,
    (SELECT avg(score) FROM order_facts)                   AS avg_review,
    ((SELECT sum(price) FROM sales, window_end
       WHERE order_date BETWEEN make_date($compare_year, 1, 1) AND d)
     / (SELECT sum(price) FROM sales, window_end
         WHERE order_date BETWEEN make_date($compare_year - 1, 1, 1) AND CAST(d - INTERVAL 1 YEAR AS DATE))
     - 1) * 100                                            AS growth_pct;
