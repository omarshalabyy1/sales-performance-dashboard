# 8. Build checklist

Follow it top to bottom. **Check** means: compare with that row of `06-checks.md`; if it differs, stop and use
"If a number is off" there before going on. Save (Ctrl+S) after every block.

## Data and settings

1. Put the seven CSV files in `data/raw/` (main README, "Data"). Check that the folder holds `olist_orders_dataset.csv`,
   `olist_order_items_dataset.csv`, `olist_order_reviews_dataset.csv`, `olist_products_dataset.csv`,
   `olist_sellers_dataset.csv`, `olist_customers_dataset.csv` and `product_category_name_translation.csv`.
2. Open Power BI Desktop → **Blank report**.
3. **File → Options and settings → Options → Current file → Data load**: untick **Auto date/time**.
4. Same window, **Current file → Report settings**: tick **Change default visual interaction from cross
   highlighting to cross filtering** (`07-interactions.md`). **OK**.
5. **File → Save as** → `powerbi/sales-performance.pbix` in this repo.

## Power Query (`01-power-query.md`)

6. **Home → Transform data**.
7. Create the `DataFolder` parameter with the full path of your `data\raw\` folder, ending with a backslash.
8. Create `stg_orders` and `stg_reviews` (blank query → rename → Advanced editor → paste). Right-click each →
   untick **Enable load**.
9. Create `fact_sales`, `dim_product`, `dim_seller`, `dim_customer` the same way (load stays on).
10. Compare each loaded table's columns and types with "Columns that load" in `01-power-query.md`.
11. **Home → Close & apply**. Wait for the load to finish.
12. **Check C1, C3, C4, C5** (Data view, select each table, row count bottom left).

## Model (`02-model.md`)

13. **Modeling → New table** → paste `dim_date`. Set the column data types listed there.
14. Select `dim_date` → **Table tools → Mark as date table** → `Date`. **Check C2**.
15. **Home → Enter data** → name `_Measures` → **Load**.
16. **Modeling → Manage relationships**: delete any relationship Power BI made by itself, then create the four in
    the table, each Many to one, Single, Active. Open **Model view**: the five tables form a star around
    `fact_sales`.
17. Hide the columns in "Hide these columns".
18. Set the two sort-by columns.
19. Set the column formats and summarization in "Formats and summarisation".

## Measures (`03-measures.dax`)

20. Select `_Measures` → **Home → New measure** → paste one measure (from its name down) → Enter. Repeat for all 23,
    in file order.
21. For each measure set the format string from its comment and the display folder from its heading.
22. Hide `_Measures[Column1]`.

## Theme and canvas (`04-pages.md`, `05-theme.json`)

23. **View → Themes → Browse for themes** → select `powerbi/05-theme.json`.
24. **Format page (paintbrush with no visual selected) → Canvas settings → Type: 16:9**.
25. Rename the page to `Overview`; add `Sales`, `Categories`, `Sellers`, `Delivery`. Set 16:9 on each.

## Overview

26. Title text box, Year slicer, Customer region slicer (positions in "Shared layout").
27. Six cards. **Check C6, C7, C8, C9, C10, C11**.
28. The four charts. **Check C12, C13, C14**.
29. Set the Overview interactions marked **None** (`07-interactions.md`).
30. **View → Sync slicers**: set the Year and Customer region slicers as in the slicer sync table in `04-pages.md`.
    The two slicers appear on the other pages.

## Sales

31. Title text box. Add the page's own Year slicer (single select, **2018**); check in Sync slicers that it is not
    synced.
32. Six cards. **Check C15, C16, C17, C18, C19, C20**.
33. The three charts. **Check C21, C22**.

## Categories

34. Title text box, four cards. **Check C23, C24, C25, C26**.
35. The bar chart and the table with its conditional formatting. **Check C27**.

## Sellers

36. Title text box, four cards. **Check C28, C29, C30**.
37. The bar chart, the scatter chart (with its `Orders` >= 30 filter) and the table. **Check C31**.

## Delivery

38. Title text box, five cards. **Check C32, C33, C34, C35, C36**.
39. The four charts. **Check C37, C38**.
40. Set the Delivery interactions marked **None** (`07-interactions.md`).

## Security (`02-model.md`, "Row-level security")

41. **Modeling → Manage roles**: create the five roles with their DAX filter. **Save**.
42. **Modeling → View as** → one role at a time → read the Revenue card on Overview. **Check C39, C40, C41, C42,
    C43**. Then **Stop viewing**.

## Finish

43. Clear the Year and Customer region slicers on every page (Sales page Year stays on **2018**). Open Overview.
    **Ctrl+S**.
44. For each page: select the tab, **View → Page view → Fit to page**, take a screenshot of the canvas only
    (Windows: Win+Shift+S), save as `powerbi/screenshots/01-overview.png`, `02-sales.png`, `03-categories.png`,
    `04-sellers.png`, `05-delivery.png`.
45. Commit and push the report and the screenshots from the repo root:

```bash
git add powerbi/sales-performance.pbix powerbi/screenshots
```

```bash
git commit -m "Power BI report and page screenshots"
```

```bash
git push
```
