# 8. Build checklist

Follow it top to bottom. **Check** means: compare with that row of `06-checks.md`; if it differs, stop and use
"If a number is off" there before going on. Save (Ctrl+S) after every block.

## Data, notebook and settings

1. Put the client's input files in `data/input/` (`data/input/README.md`; for the demo, the main README's "Data").
   Their names must match `inputs` in `config/client.yaml`.
2. From the repo root: `pip install -r requirements.txt`, then `python config.py`. It prints "config and input
   files OK" or stops with one line naming the key, file or column to fix.
3. Run the notebook from `analysis/` (`jupyter nbconvert --to notebook --execute --inplace analysis.ipynb`). It
   writes the model tables to `output/` and every number `06-checks.md` lists.
4. `python theme.py` writes `powerbi/05-theme.json` from `report.title` and `report.colours`.
5. Open Power BI Desktop → **Blank report**.
6. **File → Options and settings → Options → Current file → Data load**: untick **Auto date/time**.
7. Same window, **Current file → Report settings**: tick **Change default visual interaction from cross
   highlighting to cross filtering** (`07-interactions.md`). **OK**.
8. **File → Save as** → `powerbi/sales-performance.pbix` in this repo.

## Power Query (`01-power-query.md`)

9. **Home → Transform data**.
10. Create the `OutputFolder` parameter with the full path of your `output\` folder, ending with a backslash.
11. Create `fact_sales`, `dim_product`, `dim_seller`, `dim_customer` and `report_settings` (blank query → rename →
    Advanced editor → paste).
12. Compare each table's columns and types with "Columns that load" in `01-power-query.md`.
13. **Home → Close & apply**. Wait for the load to finish.
14. **Check C1, C3, C4, C5** (Data view, select each table, row count bottom left).

## Model (`02-model.md`)

15. **Modeling → New table** → paste `dim_date`. Set the column data types listed there.
16. Select `dim_date` → **Table tools → Mark as date table** → `Date`. **Check C2**.
17. **Home → Enter data** → name `_Measures` → **Load**.
18. **Modeling → Manage relationships**: delete any relationship Power BI made by itself, then create the four in
    the table, each Many to one, Single, Active. Open **Model view**: the five tables form a star around
    `fact_sales`.
19. Hide the columns in "Hide these columns", and the whole `report_settings` table.
20. Set the two sort-by columns.
21. Set the column formats and summarization in "Formats and summarisation".

## Measures (`03-measures.dax`)

22. Select `_Measures` → **Home → New measure** → paste one measure (from its name down) → Enter. Repeat for all 23,
    in file order.
23. For each measure set the format string from its comment and the display folder from its heading.
24. Hide `_Measures[Column1]`.

## Theme and canvas (`04-pages.md`, `05-theme.json`)

25. **View → Themes → Browse for themes** → select `powerbi/05-theme.json`.
26. **Format page (paintbrush with no visual selected) → Canvas settings → Type: 16:9**.
27. Rename the page to `Overview`; add `Sales`, `Categories`, `Sellers`, `Delivery`. Set 16:9 on each.

## Overview

28. Title text box, Year slicer, Customer region slicer (positions in "Shared layout").
29. Six cards. **Check C6, C7, C8, C9, C10, C11**.
30. The four charts. **Check C12, C13, C14**.
31. Set the Overview interactions marked **None** (`07-interactions.md`).
32. **View → Sync slicers**: set the Year and Customer region slicers as in the slicer sync table in `04-pages.md`.
    The two slicers appear on the other pages.

## Sales

33. Title text box. Add the page's own Year slicer (single select, `report.compare_year`, demo **2018**); check in Sync slicers that it is not
    synced.
34. Six cards. **Check C15, C16, C17, C18, C19, C20**.
35. The three charts. **Check C21, C22**.

## Categories

36. Title text box, four cards. **Check C23, C24, C25, C26**.
37. The bar chart and the table with its conditional formatting. **Check C27**.

## Sellers

38. Title text box, four cards. **Check C28, C29, C30**.
39. The bar chart, the scatter chart (with its `Orders` >= 30 filter) and the table. **Check C31**.

## Delivery

40. Title text box, five cards. **Check C32, C33, C34, C35, C36**.
41. The four charts. **Check C37, C38**.
42. Set the Delivery interactions marked **None** (`07-interactions.md`).

## Security (`02-model.md`, "Row-level security")

43. **Modeling → Manage roles**: create one role per region in the regions file, with its DAX filter (demo: five). **Save**.
44. **Modeling → View as** → one role at a time → read the Revenue card on Overview. **Check C39, C40, C41, C42,
    C43**. Then **Stop viewing**.

## Finish

45. Clear the Year and Customer region slicers on every page (Sales page Year stays on `report.compare_year`). Open Overview.
    **Ctrl+S**.
46. For each page: select the tab, **View → Page view → Fit to page**, take a screenshot of the canvas only
    (Windows: Win+Shift+S), save as `powerbi/screenshots/01-overview.png`, `02-sales.png`, `03-categories.png`,
    `04-sellers.png`, `05-delivery.png`.
47. Commit and push the report and the screenshots from the repo root:

```bash
git add powerbi/sales-performance.pbix powerbi/screenshots
```

```bash
git commit -m "Power BI report and page screenshots"
```

```bash
git push
```
