# 7. Interactions, filters, drill-through and bookmarks

## Report setting (once, before the first visual)

**File → Options and settings → Options → Current file → Report settings** → tick **Change default visual
interaction from cross highlighting to cross filtering**.

Why: clicking a bar then filters every other visual on the page, so cards and percentages recalculate for that
selection instead of showing a faded highlight. Every cell below marked **Filter** is then already set; you only
click the cells marked **None**.

## How to set one interaction

Select the source visual → **Format → Edit interactions** → on each target visual click the **filter** icon
(Filter) or the **circle with a line** icon (None). Click **Edit interactions** again to finish.

Rows are the visual you click; columns are the visuals it affects. "Cards" means every card on that page.
Slicers filter every visual on their page (default, nothing to set) and are left as targets at their default.

## Overview

| Click on ↓ / affects → | Revenue by month | Revenue by customer region | Top 5 categories | Average review, on time against late | Cards |
|---|---|---|---|---|---|
| Revenue by month | | Filter | Filter | Filter | Filter |
| Revenue by customer region | Filter | | Filter | Filter | Filter |
| Top 5 categories by revenue | Filter | Filter | | Filter | Filter |
| Average review, on time against late | **None** | **None** | **None** | | **None** |

Why None: that chart shows two measures, not a category, so a click on it has nothing to filter by.

## Sales

| Click on ↓ / affects → | Revenue by month, this year and last year | Top 15 customer states | Month by month | Cards |
|---|---|---|---|---|
| Revenue by month, this year and last year | | Filter | Filter | Filter |
| Top 15 customer states by revenue | Filter | | Filter | Filter |
| Month by month | Filter | Filter | | Filter |

## Categories

| Click on ↓ / affects → | Top 15 categories by revenue | All categories | Cards |
|---|---|---|---|
| Top 15 categories by revenue | | Filter | Filter |
| All categories | Filter | | Filter |

## Sellers

| Click on ↓ / affects → | Top 15 seller states | Late deliveries against reviews | Sellers | Cards |
|---|---|---|---|---|
| Top 15 seller states by revenue | | Filter | Filter | Filter |
| Late deliveries against reviews | Filter | | Filter | Filter |
| Sellers | Filter | Filter | | Filter |

## Delivery

| Click on ↓ / affects → | Review scores, on time against late | Late deliveries % by month | 10 states with the most late deliveries | Average delivery days by customer region | Cards |
|---|---|---|---|---|---|
| Review scores, on time against late | | **None** | **None** | **None** | **None** |
| Late deliveries % by month | Filter | | Filter | Filter | Filter |
| 10 states with the most late deliveries | Filter | Filter | | Filter | Filter |
| Average delivery days by customer region | Filter | Filter | Filter | | Filter |

Why None: that chart is split by delivery status, so a click on a "Late" bar would filter the page to late orders
only and every late-delivery percentage would read 100%.

## Filters

| Level | Filter |
|---|---|
| Report (all pages) | None |
| Page | None. The Sales page uses its own single-select Year slicer instead of a page filter, so the reader can change the year |
| Visual | Only the ones listed in `04-pages.md`: Top N on the category and state charts, `Orders` >= 30 on the scatter chart, `review_score` is not blank and `delivery_status` is On time or Late on the review chart |

## Drill-through, bookmarks, buttons, tooltip pages

None of them. The tables on Categories and Sellers already show the detail rows, the five page tabs are the
navigation, and the default tooltips show the fields of each chart (plus state and orders on the scatter chart).
