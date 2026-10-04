# 4. Pages

Five pages, each answering one question. Build them in this order. Positions and sizes are in pixels on a
**16:9 canvas (1280 × 720)**: select a visual, **Format → General → Properties → Size and position**, type the numbers.

| Page | Question it answers |
|---|---|
| Overview | How is the business doing overall? |
| Sales | Are we growing against last year, and where? |
| Categories | What sells? |
| Sellers | Who sells, and which sellers hurt the customer experience? |
| Delivery | How much does late delivery cost us in reviews? |

## Before the first page

1. **View → Themes → Browse for themes** → `05-theme.json`.
2. **Format page → Canvas settings → Type: 16:9**.
3. Rename the first page `Overview` (double-click the tab). Add four more pages: `Sales`, `Categories`, `Sellers`,
   `Delivery`.

## Colours

Refer to colours by their theme slot, as the colour picker shows them after the theme is loaded:

| Name used below | Where to pick it |
|---|---|
| **theme colour 1** (blue) | Colour picker, first theme colour |
| **theme colour 2** (navy) | Colour picker, second theme colour |
| **theme colour 4** (muted grey) | Colour picker, fourth theme colour |
| **danger** | The theme's `bad` colour; the picker does not list it, so choose **More colours** and type `C2410C` |

## Shared layout (every page)

| Element | x | y | w | h | Content |
|---|---|---|---|---|---|
| Title | 24 | 16 | 760 | 48 | Text box: page title in Segoe UI Semibold 20, **theme colour 2**; the subtitle under it in Segoe UI 11, **theme colour 4** |
| Year slicer | 816 | 16 | 210 | 56 | `dim_date[Year]`, style **Dropdown**, title "Year"; **Selection**: single select off, multi-select with Ctrl on, "Select all" option on |
| Region slicer | 1046 | 16 | 210 | 56 | `dim_customer[customer_region]`, style **Dropdown**, title "Customer region"; **Selection**: single select off, multi-select with Ctrl on, "Select all" option on |
| Cards row | 24 | 80 | (per page) | 96 | One **Card** per measure, the measure's name as the label; callout value in the measure's own format |
| Charts | 24 to 1256 | 192 to 704 | | | Per page, below |

**Every chart:** the title is the quoted name in its row, title on; legend off unless the row names two series;
value axis display units **Auto**; data labels only where the row says so; tooltips are the default ones (the
fields on the chart) unless the row lists extra tooltip fields.

**Slicer sync** (build both slicers on Overview, then **View → Sync slicers**):

| Slicer | Overview | Sales | Categories | Sellers | Delivery |
|---|---|---|---|---|---|
| Year (`dim_date[Year]`) | sync + visible | **not synced, not visible** | sync + visible | sync + visible | sync + visible |
| Customer region | sync + visible | sync + visible | sync + visible | sync + visible | sync + visible |

The Sales page has its own single-select Year slicer, because "against last year" needs exactly one year.

**Interactions, filters, drill-through and bookmarks:** see `07-interactions.md`. Leave the slicers cleared
("All") when you save, except the Sales page Year slicer, which stays on **2018**.

---

## Page 1: Overview

Title "Sales overview", subtitle "Delivered orders, Sep 2016 to Aug 2018".

**Cards** (w 196, h 96, y 80):

| x | Label | Measure | Display units |
|---|---|---|---|
| 24 | Revenue | `Revenue` | Millions, 2 decimals |
| 230 | Orders | `Orders` | None |
| 436 | Customers | `Customers` | None |
| 642 | Repeat customers | `Repeat Customers %` | |
| 848 | Late deliveries | `Late Deliveries %` | |
| 1054 | Average review | `Average Review` | |

**Charts:**

| Visual | x | y | w | h | Fields | Settings |
|---|---|---|---|---|---|---|
| Line chart, "Revenue by month" | 24 | 192 | 808 | 248 | X-axis `dim_date[Year Month]`, Y-axis `Revenue` | X-axis type **Categorical**; sort axis by `Year Month`, ascending; no markers, no data labels |
| Clustered bar chart, "Revenue by customer region" | 848 | 192 | 402 | 248 | Y-axis `dim_customer[customer_region]`, X-axis `Revenue` | Sort by `Revenue`, descending; data labels on, Millions, 1 decimal |
| Clustered bar chart, "Top 10 categories by revenue" | 24 | 456 | 808 | 248 | Y-axis `dim_product[category]`, X-axis `Revenue` | Filter on this visual: `category` → **Top N**, Top 10 by `Revenue`; sort by `Revenue`, descending; data labels on, Millions, 2 decimals |
| Clustered column chart, "Average review, on time against late" | 848 | 456 | 402 | 248 | Y-axis `Average Review On Time`, `Average Review Late` (no X-axis field) | Y-axis 0 to 5; data labels on, 2 decimals; colours: On time **theme colour 1**, Late **danger** |

---

## Page 2: Sales

Title "Sales against last year", subtitle "Last year = the same days one year earlier".

**Year slicer** (this page only, not synced): x 816, y 16, w 210, h 56, field `dim_date[Year]`, style
**Dropdown**, **Selection → Single select on**, select **2018**.

**Cards** (w 196, h 96, y 80):

| x | Label | Measure | Display units |
|---|---|---|---|
| 24 | Revenue | `Revenue` | Millions, 2 decimals |
| 230 | Revenue last year | `Revenue LY` | Millions, 2 decimals |
| 436 | Against last year | `Revenue vs LY %` | |
| 642 | Orders | `Orders` | None |
| 848 | Average order value | `Average Order Value` | None, 2 decimals |
| 1054 | Freight % of revenue | `Freight % of Revenue` | |

**Charts:**

| Visual | x | y | w | h | Fields | Settings |
|---|---|---|---|---|---|---|
| Line chart, "Revenue by month, this year and last year" | 24 | 192 | 808 | 300 | X-axis `dim_date[Month]`, Y-axis `Revenue`, `Revenue LY` | Sort axis by `Month`, ascending; colours: Revenue **theme colour 1**, Revenue LY **theme colour 4** with line style **Dashed**; legend top left |
| Clustered bar chart, "Revenue by customer state" | 848 | 192 | 402 | 512 | Y-axis `dim_customer[customer_state]`, X-axis `Revenue` | Sort by `Revenue`, descending; no data labels |
| Matrix, "Month by month" | 24 | 508 | 808 | 196 | Rows `dim_date[Year Month]`; Values `Orders`, `Revenue`, `Average Order Value`, `Revenue vs LY %` | Conditional formatting on `Revenue`: **Data bars**, positive bar **theme colour 1**; row totals on |

---

## Page 3: Categories

Title "What sells", subtitle "Revenue by product category".

**Cards** (w 300, h 96, y 80):

| x | Label | Measure | Display units |
|---|---|---|---|
| 24 | Revenue | `Revenue` | Millions, 2 decimals |
| 334 | Items sold | `Items Sold` | None |
| 644 | Categories with sales | `Categories With Sales` | None |
| 954 | Top 10 categories share | `Top 10 Categories Share` | |

**Charts:**

| Visual | x | y | w | h | Fields | Settings |
|---|---|---|---|---|---|---|
| Clustered bar chart, "Top 15 categories by revenue" | 24 | 192 | 500 | 512 | Y-axis `dim_product[category]`, X-axis `Revenue` | Filter on this visual: `category` → **Top N**, Top 15 by `Revenue`; sort descending; data labels on, Millions, 2 decimals |
| Table, "All categories" | 540 | 192 | 716 | 512 | `dim_product[category]` (rename to "Category" in the visual), `Revenue`, `Share of Revenue %`, `Items Sold`, `Average Review`, `Late Deliveries %` | Sort by `Revenue`, descending; totals on; conditional formatting: `Revenue` → **Data bars** in **theme colour 1**; `Average Review` → **Font colour → Rules**: if value < 4 then **danger**; `Late Deliveries %` → **Font colour → Rules**: if value >= 0.10 (number) then **danger** |

---

## Page 4: Sellers

Title "Who sells", subtitle "Sellers as suppliers: revenue, delivery and reviews".

**Cards** (w 300, h 96, y 80):

| x | Label | Measure | Display units |
|---|---|---|---|
| 24 | Active sellers | `Active Sellers` | None |
| 334 | Top 10% sellers share | `Top 10% Sellers Share` | |
| 644 | Revenue | `Revenue` | Millions, 2 decimals |
| 954 | Late deliveries | `Late Deliveries %` | |

**Charts:**

| Visual | x | y | w | h | Fields | Settings |
|---|---|---|---|---|---|---|
| Clustered bar chart, "Revenue by seller state" | 24 | 192 | 400 | 512 | Y-axis `dim_seller[seller_state]`, X-axis `Revenue` | Sort by `Revenue`, descending; no data labels |
| Scatter chart, "Late deliveries against reviews, sellers with 30+ orders" | 440 | 192 | 816 | 248 | Values `dim_seller[seller_short_id]`; X-axis `Late Deliveries %`; Y-axis `Average Review`; Size `Revenue`; Tooltips `dim_seller[seller_state]`, `Orders` | Filter on this visual: `Orders` is greater than or equal to 30; marker colour **theme colour 1** |
| Table, "Sellers" | 440 | 456 | 816 | 248 | `dim_seller[seller_short_id]` ("Seller"), `dim_seller[seller_state]` ("State"), `Revenue`, `Orders`, `Late Deliveries %`, `Average Review` | Sort by `Revenue`, descending; the same conditional formatting as the categories table (data bars on `Revenue`, orange font for `Average Review` < 4 and `Late Deliveries %` >= 0.10) |

---

## Page 5: Delivery

Title "How delivery drives reviews", subtitle "Orders that arrive late get far lower reviews".

**Cards** (w 238, h 96, y 80):

| x | Label | Measure | Display units |
|---|---|---|---|
| 24 | Average delivery days | `Average Delivery Days` | None, 1 decimal |
| 272 | Late deliveries | `Late Deliveries %` | |
| 520 | Late orders | `Late Orders` | None |
| 768 | Average review, on time | `Average Review On Time` | |
| 1016 | Average review, late | `Average Review Late` | |

**Charts:**

| Visual | x | y | w | h | Fields | Settings |
|---|---|---|---|---|---|---|
| Clustered column chart, "Review scores, on time against late" | 24 | 192 | 616 | 248 | X-axis `fact_sales[review_score]`, Legend `fact_sales[delivery_status]`, Y-axis `Review Share %` | X-axis type **Categorical**; filters on this visual: `review_score` **is not blank**, `delivery_status` = On time and Late (untick No date); colours: On time **theme colour 1**, Late **danger**; data labels on |
| Line chart, "Late deliveries % by month" | 656 | 192 | 600 | 248 | X-axis `dim_date[Year Month]`, Y-axis `Late Deliveries %` | X-axis type **Categorical**, sorted by `Year Month` ascending; line colour **danger** |
| Clustered bar chart, "10 states with the most late deliveries" | 24 | 456 | 616 | 248 | Y-axis `dim_customer[customer_state]`, X-axis `Late Deliveries %` | Filter on this visual: `customer_state` → **Top N**, Top 10 by `Late Deliveries %`; sort descending; data labels on, 1 decimal; bar colour **danger** |
| Clustered bar chart, "Average delivery days by customer region" | 656 | 456 | 600 | 248 | Y-axis `dim_customer[customer_region]`, X-axis `Average Delivery Days` | Sort descending; data labels on, 1 decimal |

---

## Finish

1. Check every page against `06-checks.md` (the order is in `08-build-checklist.md`).
2. Save as `powerbi/sales-performance.pbix`.
3. Export one screenshot per page into `powerbi/screenshots/` (`01-overview.png` to `05-delivery.png`): full page,
   slicers as saved.
