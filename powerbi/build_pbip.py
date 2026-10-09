"""Write the Power BI project (sales-performance.pbip) from this folder's build pack and config/client.yaml.

The M code comes from 01-power-query.md, the date table from 02-model.md and the measures from 03-measures.dax, so
the report and the build pack cannot drift apart. Client values come only through load_config().
Run from the repo root after the notebook and theme.py: python powerbi/build_pbip.py
"""
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from config import load_config  # noqa: E402

cfg = load_config()
NAME = "sales-performance"
REP, SEM = HERE / f"{NAME}.Report", HERE / f"{NAME}.SemanticModel"
BASE_THEME = "CY26SU09"
CUSTOM_THEME = "SalesPerformanceTheme.json"
S = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"

COL = cfg["report"]["colours"]
T1, T2, T4, T6, MUTED, DANGER = COL["data"][0], COL["data"][1], COL["data"][3], COL["data"][5], COL["muted"], COL["danger"]
CURRENCY = cfg["client"]["currency"]
TOP_N, TOP_PCT, YEAR = cfg["report"]["top_categories"], cfg["report"]["top_sellers_percent"], cfg["report"]["compare_year"]


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(obj if isinstance(obj, str) else json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------- read the build pack

def m_blocks():
    text = (HERE / "01-power-query.md").read_text(encoding="utf-8")
    blocks = {}
    for heading, body in re.findall(r"^## (\w+) \(.*?\)\n.*?```m\n(.*?)```", text, re.S | re.M):
        blocks[heading] = body.rstrip("\n")
    return blocks


def date_dax():
    text = (HERE / "02-model.md").read_text(encoding="utf-8")
    block = re.search(r"```dax\ndim_date =\n(.*?)```", text, re.S).group(1)
    for var, day in (("FirstDay", cfg["report"]["date_start"]), ("LastDay", cfg["report"]["date_end"])):
        block, found = re.subn(rf"VAR {var} = DATE \(.*?\)\n", f"VAR {var} = DATE ( {day.year}, {day.month}, {day.day} )\n", block)
        assert found == 1, f"02-model.md: dim_date needs one line 'VAR {var} = DATE ( ... )'"
    return block.rstrip("\n")


def measures():
    """Each measure: its comment block (with 'Format: ...'), the line 'Name =', the expression up to a blank line."""
    found, folder, comment, current = [], None, [], None
    for line in (HERE / "03-measures.dax").read_text(encoding="utf-8").splitlines():
        if current is not None:
            if line.strip():
                current["lines"].append(line)
                continue
            current = None
        if line.startswith("// Display folder: "):
            folder = line.removeprefix("// Display folder: ").strip()
        elif line.startswith("//"):
            comment.append(line)
        elif m := re.match(r"^(\w[^=]*?) =$", line):
            fmt = re.search(r"Format: (\S+)", " ".join(comment)).group(1)
            current = {"name": m.group(1), "expression": None, "formatString": fmt, "displayFolder": folder, "lines": []}
            found.append(current)
            comment = []
        else:
            comment = []
    return [{"name": m["name"], "expression": "\n".join(m["lines"]), "formatString": m["formatString"],
             "displayFolder": m["displayFolder"]} for m in found]


M = m_blocks()
MEASURES = measures()
assert len(MEASURES) == 23, f"expected 23 measures in 03-measures.dax, found {len(MEASURES)}"
assert set(M) >= {"OutputFolder", "fact_sales", "dim_product", "dim_seller", "dim_customer", "report_settings"}
OUTPUT = str(cfg["output_dir"].resolve()) + "\\"
PARAMETER = re.sub(r'^".*?"', lambda _: f'"{OUTPUT}"', M["OutputFolder"])

# ---------------------------------------------------------------- semantic model (model.bim)


def col(name, dtype, fmt=None, hidden=False, summarize="none", **extra):
    c = {"name": name, "dataType": dtype, "sourceColumn": name, "summarizeBy": summarize}
    if fmt:
        c["formatString"] = fmt
    if hidden:
        c["isHidden"] = True
    c.update(extra)
    return c


def calc_col(name, dtype, fmt=None, hidden=False, **extra):
    c = {"type": "calculatedTableColumn", "name": name, "dataType": dtype, "isNameInferred": True,
         "isDataTypeInferred": True, "sourceColumn": f"[{name}]", "summarizeBy": "none"}
    if fmt:
        c["formatString"] = fmt
    if hidden:
        c["isHidden"] = True
    c.update(extra)
    return c


def m_table(name, columns, hidden=False):
    t = {"name": name, "columns": columns,
         "partitions": [{"name": name, "mode": "import", "source": {"type": "m", "expression": M[name].split("\n")}}]}
    if hidden:
        t["isHidden"] = True
    return t


regions = sorted(set(l.split(",")[1].strip() for l in
                     (cfg["input_dir"] / cfg["inputs"]["regions"]).read_text(encoding="utf-8-sig").splitlines()[1:] if l.strip()))
DEC = "#,0." + "0" * cfg["client"]["decimals"]

model = {
    "compatibilityLevel": 1567,
    "model": {
        "culture": "en-US",
        "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "sourceQueryCulture": "en-US",
        "expressions": [{"name": "OutputFolder", "kind": "m", "expression": PARAMETER,
                         "annotations": [{"name": "PBI_ResultType", "value": "Text"}]}],
        "tables": [
            m_table("fact_sales", [
                col("order_id", "string", hidden=True), col("item_no", "int64", "0", hidden=True),
                col("order_date", "dateTime", "dd mmm yyyy", hidden=True), col("product_id", "string", hidden=True),
                col("seller_id", "string", hidden=True), col("customer_id", "string", hidden=True),
                col("price", "decimal", DEC, hidden=True, summarize="sum"),
                col("freight", "decimal", DEC, hidden=True, summarize="sum"),
                col("delivery_days", "int64", "0", hidden=True), col("delivery_status", "string"),
                col("review_score", "int64", "0")]),
            m_table("dim_product", [col("product_id", "string", hidden=True), col("category", "string")]),
            m_table("dim_seller", [col("seller_id", "string", hidden=True), col("seller_city", "string"),
                                   col("seller_state", "string"), col("seller_region", "string"),
                                   col("seller_short_id", "string")]),
            m_table("dim_customer", [col("customer_id", "string", hidden=True), col("person_id", "string", hidden=True),
                                     col("customer_city", "string"), col("customer_state", "string"),
                                     col("customer_region", "string")]),
            m_table("report_settings", [col("top_categories", "int64", "0"), col("top_sellers_percent", "int64", "0")],
                    hidden=True),
            {"name": "dim_date", "dataCategory": "Time",
             "columns": [calc_col("Date", "dateTime", "dd mmm yyyy", isKey=True),
                         calc_col("Year", "int64", "0"),
                         calc_col("Month Number", "int64", "0", hidden=True),
                         calc_col("Month", "string", sortByColumn="Month Number"),
                         calc_col("Year Month", "string", sortByColumn="Year Month Number"),
                         calc_col("Year Month Number", "int64", "0", hidden=True),
                         calc_col("Date With Sales", "boolean", hidden=True)],
             "partitions": [{"name": "dim_date", "mode": "import",
                             "source": {"type": "calculated", "expression": date_dax().split("\n")}}]},
            {"name": "_Measures",
             "columns": [col("Column1", "string", hidden=True)],
             "partitions": [{"name": "_Measures", "mode": "import", "source": {"type": "m", "expression": [
                 "let", "    Source = #table(type table [Column1 = text], {})", "in", "    Source"]}}],
             "measures": MEASURES},
        ],
        "relationships": [
            {"name": str(uuid.uuid4()), "fromTable": "fact_sales", "fromColumn": f, "toTable": t, "toColumn": c}
            for f, t, c in [("order_date", "dim_date", "Date"), ("product_id", "dim_product", "product_id"),
                            ("seller_id", "dim_seller", "seller_id"), ("customer_id", "dim_customer", "customer_id")]],
        "roles": [{"name": f"Seller region - {r}", "modelPermission": "read",
                   "tablePermissions": [{"name": "dim_seller", "filterExpression": f'[seller_region] = "{r}"'}]}
                  for r in regions],
        "annotations": [
            {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
            {"name": "PBI_QueryOrder", "value": json.dumps(["OutputFolder", "fact_sales", "dim_product", "dim_seller",
                                                            "dim_customer", "report_settings", "_Measures"])},
        ],
    },
}

# ---------------------------------------------------------------- report (PBIR) helpers


def lit(v): return {"expr": {"Literal": {"Value": v}}}
def colour(hexv): return {"solid": {"color": lit(f"'{hexv}'")}}
def s(text): return lit("'" + text.replace("'", "''") + "'")
def column(entity, prop): return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}
def measure(prop): return {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": prop}}
def src(kind, source, prop): return {kind: {"Expression": {"SourceRef": {"Source": source}}, "Property": prop}}


def proj(field, display=None):
    kind = "Column" if "Column" in field else "Measure"
    p = {"field": field, "queryRef": f"{field[kind]['Expression']['SourceRef']['Entity']}.{field[kind]['Property']}",
         "nativeQueryRef": field[kind]["Property"]}
    if display:
        p["displayName"] = display
    return p


def title(text, size=None):
    props = {"show": lit("true"), "text": s(text)}
    if size:
        props["fontSize"] = lit(f"{size}D")
    return {"title": [{"properties": props}]}


def container(name, x, y, w, h, z, visual, filters=None):
    v = {"$schema": f"{S}/visualContainer/2.0.0/schema.json", "name": name,
         "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z}, "visual": visual}
    if filters:
        v["filterConfig"] = {"filters": filters}
    return v


def textbox(heading, subtitle):
    return {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": [
        {"textRuns": [{"value": heading, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": T2}}]},
        {"textRuns": [{"value": subtitle, "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": MUTED}}]}]}}]},
        "drillFilterOtherVisuals": True}


def slicer(entity, prop, header, single=False, pick=None, sync=None):
    objects = {"data": [{"properties": {"mode": s("Dropdown")}}],
               "header": [{"properties": {"show": lit("true"), "text": s(header), "textSize": lit("10D")}}],
               "selection": [{"properties": {"singleSelect": lit("true" if single else "false"),
                                             "selectAllCheckboxEnabled": lit("false" if single else "true")}}]}
    if pick:
        objects["general"] = [{"properties": {"filter": {"filter": pick}}}]
    v = {"visualType": "slicer", "query": {"queryState": {"Values": {"projections": [proj(column(entity, prop))]}}},
         "objects": objects, "drillFilterOtherVisuals": True}
    if sync:
        v["syncGroup"] = {"groupName": sync, "fieldChanges": True, "filterChanges": True}
    return v


def in_filter(entity, prop, literals):
    return {"Version": 2, "From": [{"Name": "x", "Entity": entity, "Type": 0}],
            "Where": [{"Condition": {"In": {"Expressions": [src("Column", "x", prop)],
                                            "Values": [[{"Literal": {"Value": v}}] for v in literals]}}}]}


UNITS = {"M": "1000000D", "none": "1D"}


def card(m, label, units="none", decimals=None):
    labels = {"labelDisplayUnits": lit(UNITS[units])}
    if decimals is not None:
        labels["labelPrecision"] = lit(f"{decimals}L")
    return {"visualType": "card", "query": {"queryState": {"Values": {"projections": [proj(measure(m))]}}},
            "objects": {"labels": [{"properties": labels}], "categoryLabels": [{"properties": {"show": lit("false")}}]},
            "visualContainerObjects": title(label, 11), "drillFilterOtherVisuals": True}


def axes(categorical=False):
    cat = {"showAxisTitle": lit("false")}
    if categorical:
        cat["axisType"] = s("Categorical")
    return {"categoryAxis": [{"properties": cat}], "valueAxis": [{"properties": {"showAxisTitle": lit("false")}}]}


def data_labels(units=None, decimals=None):
    if units is None:
        return [{"properties": {"show": lit("false")}}]
    p = {"show": lit("true"), "labelDisplayUnits": lit(UNITS[units])}
    if decimals is not None:
        p["labelPrecision"] = lit(f"{decimals}L")
    return [{"properties": p}]


def bar(category, value, text, sort_by=None, labels=(None, None), fill=None):
    objects = {**axes(), "labels": data_labels(*labels)}
    if fill:
        objects["dataPoint"] = [{"properties": {"fill": colour(fill)}}]
    return {"visualType": "clusteredBarChart",
            "query": {"queryState": {"Category": {"projections": [proj(category)]},
                                     "Y": {"projections": [proj(measure(value))]}},
                      "sortDefinition": {"sort": [{"field": sort_by or measure(value), "direction": "Descending"}],
                                         "isDefaultSort": False}},
            "objects": objects, "visualContainerObjects": title(text), "drillFilterOtherVisuals": True}


def line(category, values, text, colours, dashed=()):
    objects = {**axes(categorical=True), "labels": data_labels(),
               "legend": [{"properties": {"show": lit("true" if len(values) > 1 else "false"), "position": s("Top")}}],
               "dataPoint": [{"properties": {"fill": colour(c)}, "selector": {"metadata": f"_Measures.{m}"}}
                             for m, c in zip(values, colours)],
               "lineStyles": [{"properties": {"strokeWidth": lit("2D"),
                                              **({"lineStyle": s("dashed")} if m in dashed else {})},
                               "selector": {"metadata": f"_Measures.{m}"}} for m in values]}
    return {"visualType": "lineChart",
            "query": {"queryState": {"Category": {"projections": [proj(category)]},
                                     "Y": {"projections": [proj(measure(m)) for m in values]}},
                      "sortDefinition": {"sort": [{"field": category, "direction": "Ascending"}], "isDefaultSort": False}},
            "objects": objects, "visualContainerObjects": title(text), "drillFilterOtherVisuals": True}


def top_n(name, entity, prop, n, by):
    sub = {"Version": 2, "From": [{"Name": "e", "Entity": entity, "Type": 0}, {"Name": "m", "Entity": "_Measures", "Type": 0}],
           "Select": [{**src("Column", "e", prop), "Name": "field"}],
           "OrderBy": [{"Direction": 2, "Expression": src("Measure", "m", by)}], "Top": n}
    return {"name": name, "field": column(entity, prop), "type": "TopN",
            "filter": {"Version": 2, "From": [{"Name": "subquery", "Expression": {"Subquery": {"Query": sub}}, "Type": 2},
                                              {"Name": "e", "Entity": entity, "Type": 0}],
                       "Where": [{"Condition": {"In": {"Expressions": [src("Column", "e", prop)],
                                                       "Table": {"SourceRef": {"Source": "subquery"}}}}}]}}


def measure_at_least(name, m, value):
    return {"name": name, "field": measure(m), "type": "Advanced",
            "filter": {"Version": 2, "From": [{"Name": "m", "Entity": "_Measures", "Type": 0}],
                       "Where": [{"Condition": {"Comparison": {"ComparisonKind": 2, "Left": src("Measure", "m", m),
                                                               "Right": {"Literal": {"Value": f"{value}L"}}}}}]}}


def basic_in(name, entity, prop, literals):
    return {"name": name, "field": column(entity, prop), "type": "Categorical", "filter": in_filter(entity, prop, literals)}


def not_blank(name, entity, prop):
    return {"name": name, "field": column(entity, prop), "type": "Advanced",
            "filter": {"Version": 2, "From": [{"Name": "x", "Entity": entity, "Type": 0}],
                       "Where": [{"Condition": {"Not": {"Expression": {"Comparison": {
                           "ComparisonKind": 0, "Left": src("Column", "x", prop), "Right": {"Literal": {"Value": "null"}}}}}}}]}}


def font_rule(m, kind, value):
    return {"properties": {"fontColor": {"solid": {"color": {"expr": {"Conditional": {"Cases": [{
        "Condition": {"Comparison": {"ComparisonKind": kind, "Left": measure(m), "Right": {"Literal": {"Value": value}}}},
        "Value": {"Literal": {"Value": f"'{DANGER}'"}}}]}}}}}},
        "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": f"_Measures.{m}"}}


def data_bar(m):
    return {"properties": {"dataBars": {"positiveColor": colour(T6), "negativeColor": colour(DANGER),
                                        "axisColor": colour(T4), "reverseDirection": lit("false"), "hideText": lit("false")}},
            "selector": {"metadata": f"_Measures.{m}"}}


def table(fields, text, sort_by):
    return {"visualType": "tableEx",
            "query": {"queryState": {"Values": {"projections": fields}},
                      "sortDefinition": {"sort": [{"field": measure(sort_by), "direction": "Descending"}], "isDefaultSort": False}},
            "objects": {"total": [{"properties": {"totals": lit("true")}}],
                        "columnHeaders": [{"properties": {"bold": lit("true")}}],
                        "values": [font_rule("Average Review", 3, "4D"), font_rule("Late Deliveries %", 2, "0.1D")],
                        "columnFormatting": [data_bar("Revenue")]},
            "visualContainerObjects": title(text), "drillFilterOtherVisuals": True}


def cards_row(specs, width):
    return [container(f"v1{i}Card{re.sub(r'[^A-Za-z]', '', m)}"[:50], 24 + i * (width + 10), 80, width, 96, 100 + i,
                      card(m, label, *rest)) for i, (m, label, *rest) in enumerate(specs)]


def header(heading, subtitle, year_slicer=True):
    v = [container("v01Title", 24, 8, 760, 68, 1, textbox(heading, subtitle)),
         container("v03SlicerRegion", 1046, 12, 210, 60, 3,
                   slicer("dim_customer", "customer_region", "Customer region", sync="Region"))]
    if year_slicer:
        v.append(container("v02SlicerYear", 816, 12, 210, 60, 2, slicer("dim_date", "Year", "Year", sync="Year")))
    return v


def no_filter(source, page_visuals):
    return [{"source": source, "target": v["name"], "type": "NoFilter"} for v in page_visuals if v["name"] != source]


# ---------------------------------------------------------------- the five pages (04-pages.md)

money = f", {CURRENCY}"
p1 = header("Sales overview", "Orders that count as sales") + cards_row([
    ("Revenue", "Revenue" + money, "M", 2), ("Orders", "Orders"), ("Customers", "Customers"),
    ("Repeat Customers %", "Repeat customers"), ("Late Deliveries %", "Late deliveries"), ("Average Review", "Average review")], 196) + [
    container("v20LineRevenueByMonth", 24, 192, 808, 248, 200,
              line(column("dim_date", "Year Month"), ["Revenue"], "Revenue by month", [T1])),
    container("v21BarRevenueByRegion", 848, 192, 402, 248, 201,
              bar(column("dim_customer", "customer_region"), "Revenue", "Revenue by customer region", labels=("M", 1))),
    container("v22BarTopCategories", 24, 456, 808, 248, 202,
              bar(column("dim_product", "category"), "Revenue", "Top 5 categories by revenue", labels=("M", 2)),
              filters=[top_n("fTop5Categories", "dim_product", "category", 5, "Revenue")]),
    container("v23ColumnReviewOnTimeLate", 848, 456, 402, 248, 203, {
        "visualType": "clusteredColumnChart",
        "query": {"queryState": {"Y": {"projections": [proj(measure("Average Review On Time"), "On time"), proj(measure("Average Review Late"), "Late")]}}},
        "objects": {**axes(), "labels": data_labels("none", 2),
                    "valueAxis": [{"properties": {"start": lit("0D"), "end": lit("5D"), "showAxisTitle": lit("false")}}],
                    "legend": [{"properties": {"show": lit("true"), "position": s("Top")}}],
                    "dataPoint": [{"properties": {"fill": colour(c)}, "selector": {"metadata": f"_Measures.{m}"}}
                                  for m, c in [("Average Review On Time", T1), ("Average Review Late", DANGER)]]},
        "visualContainerObjects": title("Average review, on time against late"), "drillFilterOtherVisuals": True}),
]
i1 = no_filter("v23ColumnReviewOnTimeLate", p1)

p2 = header("Sales against last year", "Last year = the same days one year earlier", year_slicer=False) + [
    container("v02SlicerYearSingle", 816, 12, 210, 60, 2,
              slicer("dim_date", "Year", "Year", single=True, pick=in_filter("dim_date", "Year", [f"{YEAR}L"])))
] + cards_row([
    ("Revenue", "Revenue" + money, "M", 2), ("Revenue LY", "Revenue last year" + money, "M", 2),
    ("Revenue vs LY %", "Against last year"), ("Orders", "Orders"),
    ("Average Order Value", "Average order value" + money, "none", 2), ("Freight % of Revenue", "Freight % of revenue")], 196) + [
    container("v20LineRevenueThisLastYear", 24, 192, 808, 300, 200,
              line(column("dim_date", "Month"), ["Revenue", "Revenue LY"], "Revenue by month, this year and last year",
                   [T1, T4], dashed=("Revenue LY",))),
    container("v21BarRevenueByState", 848, 192, 402, 512, 201,
              bar(column("dim_customer", "customer_state"), "Revenue", "Top 15 customer states by revenue"),
              filters=[top_n("fTop15CustomerStates", "dim_customer", "customer_state", 15, "Revenue")]),
    container("v22MatrixMonthByMonth", 24, 508, 808, 196, 202, {
        "visualType": "pivotTable",
        "query": {"queryState": {"Rows": {"projections": [proj(column("dim_date", "Year Month"))]},
                                 "Values": {"projections": [proj(measure(m)) for m in
                                                            ["Orders", "Revenue", "Average Order Value", "Revenue vs LY %"]]}}},
        "objects": {"columnFormatting": [data_bar("Revenue")], "columnHeaders": [{"properties": {"bold": lit("true")}}]},
        "visualContainerObjects": title("Month by month"), "drillFilterOtherVisuals": True}),
]
i2 = []

p3 = header("What sells", "Revenue by product category") + cards_row([
    ("Revenue", "Revenue" + money, "M", 2), ("Items Sold", "Items sold"), ("Categories With Sales", "Categories with sales"),
    ("Top Categories Share", f"Top {TOP_N} categories share")], 300) + [
    container("v20BarTop15Categories", 24, 192, 500, 512, 200,
              bar(column("dim_product", "category"), "Revenue", "Top 15 categories by revenue", labels=("M", 2)),
              filters=[top_n("fTop15Categories", "dim_product", "category", 15, "Revenue")]),
    container("v21TableAllCategories", 540, 192, 716, 512, 201, table(
        [proj(column("dim_product", "category"), "Category")] +
        [proj(measure(m), d) for m, d in [("Revenue", "Revenue"), ("Share of Revenue %", "Share"), ("Items Sold", "Items"),
                                          ("Average Review", "Avg review"), ("Late Deliveries %", "Late")]],
        "All categories", "Revenue")),
]
i3 = []

p4 = header("Who sells", "Sellers as suppliers: revenue, delivery and reviews") + cards_row([
    ("Active Sellers", "Active sellers"), ("Top Sellers Share", f"Top {TOP_PCT}% sellers share"),
    ("Revenue", "Revenue" + money, "M", 2), ("Late Deliveries %", "Late deliveries")], 300) + [
    container("v20BarRevenueBySellerState", 24, 192, 400, 512, 200,
              bar(column("dim_seller", "seller_state"), "Revenue", "Top 15 seller states by revenue"),
              filters=[top_n("fTop15SellerStates", "dim_seller", "seller_state", 15, "Revenue")]),
    container("v21ScatterLateVsReview", 440, 192, 816, 248, 201, {
        "visualType": "scatterChart",
        "query": {"queryState": {"Category": {"projections": [proj(column("dim_seller", "seller_short_id"))]},
                                 "X": {"projections": [proj(measure("Late Deliveries %"))]},
                                 "Y": {"projections": [proj(measure("Average Review"))]},
                                 "Size": {"projections": [proj(measure("Revenue"))]},
                                 "Tooltips": {"projections": [proj(measure("Orders"))]}}},
        "objects": {"dataPoint": [{"properties": {"fill": colour(T1)}}],
                    "categoryAxis": [{"properties": {"showAxisTitle": lit("true")}}],
                    "valueAxis": [{"properties": {"showAxisTitle": lit("true")}}]},
        "visualContainerObjects": title("Late deliveries against reviews, sellers with 30+ orders"),
        "drillFilterOtherVisuals": True}, filters=[measure_at_least("fOrders30", "Orders", 30)]),
    container("v22TableSellers", 440, 456, 816, 248, 202, table(
        [proj(column("dim_seller", "seller_short_id"), "Seller"), proj(column("dim_seller", "seller_state"), "State")] +
        [proj(measure(m), d) for m, d in [("Revenue", "Revenue"), ("Orders", "Orders"), ("Late Deliveries %", "Late"),
                                          ("Average Review", "Avg review")]],
        "Sellers", "Revenue")),
]
i4 = []

p5 = header("How delivery drives reviews", "Orders that arrive late get far lower reviews") + cards_row([
    ("Average Delivery Days", "Average delivery days", "none", 1), ("Late Deliveries %", "Late deliveries"),
    ("Late Orders", "Late orders"), ("Average Review On Time", "Average review, on time"),
    ("Average Review Late", "Average review, late")], 238) + [
    container("v20ColumnReviewScores", 24, 192, 616, 248, 200, {
        "visualType": "clusteredColumnChart",
        "query": {"queryState": {"Category": {"projections": [proj(column("fact_sales", "review_score"))]},
                                 "Series": {"projections": [proj(column("fact_sales", "delivery_status"))]},
                                 "Y": {"projections": [proj(measure("Review Share %"))]}},
                  "sortDefinition": {"sort": [{"field": column("fact_sales", "review_score"), "direction": "Ascending"}],
                                     "isDefaultSort": False}},
        "objects": {**axes(categorical=True), "labels": data_labels("none", 0),
                    "legend": [{"properties": {"show": lit("true"), "position": s("Top"), "showTitle": lit("false")}}],
                    "dataPoint": [{"properties": {"fill": colour(c)},
                                   "selector": {"data": [{"scopeId": {"Comparison": {
                                       "ComparisonKind": 0, "Left": column("fact_sales", "delivery_status"),
                                       "Right": {"Literal": {"Value": f"'{status}'"}}}}}]}}
                                  for status, c in [("On time", T1), ("Late", DANGER)]]},
        "visualContainerObjects": title("Review scores, on time against late"), "drillFilterOtherVisuals": True},
        filters=[not_blank("fReviewNotBlank", "fact_sales", "review_score"),
                 basic_in("fOnTimeOrLate", "fact_sales", "delivery_status", ["'On time'", "'Late'"])]),
    container("v21LineLateByMonth", 656, 192, 600, 248, 201,
              line(column("dim_date", "Year Month"), ["Late Deliveries %"], "Late deliveries % by month", [DANGER])),
    container("v22BarLateStates", 24, 456, 616, 248, 202,
              {**bar(column("dim_customer", "customer_state"), "Late Deliveries %", "10 states with the most late deliveries",
                     labels=("none", 1), fill=DANGER), "visualType": "clusteredColumnChart"},
              filters=[top_n("fTop10LateStates", "dim_customer", "customer_state", 10, "Late Deliveries %")]),
    container("v23BarDeliveryDaysByRegion", 656, 456, 600, 248, 203,
              bar(column("dim_customer", "customer_region"), "Average Delivery Days",
                  "Average delivery days by customer region", labels=("none", 1))),
]
i5 = no_filter("v20ColumnReviewScores", p5)


def page(name, display, visuals, interactions):
    return name, {"$schema": f"{S}/page/2.0.0/schema.json", "name": name, "displayName": display,
                  "displayOption": "FitToPage", "width": 1280, "height": 720,
                  **({"visualInteractions": interactions} if interactions else {})}, visuals


PAGES = [page("pg01Overview", "Overview", p1, i1), page("pg02Sales", "Sales", p2, i2),
         page("pg03Categories", "Categories", p3, i3), page("pg04Sellers", "Sellers", p4, i4),
         page("pg05Delivery", "Delivery", p5, i5)]
ACTIVE = sys.argv[1] if len(sys.argv) > 1 else PAGES[0][0]

# ---------------------------------------------------------------- write everything

for d in (REP / "definition", SEM / "model.bim"):
    if d.is_dir():
        shutil.rmtree(d)
platform = "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json"
write(HERE / f"{NAME}.pbip", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
    "version": "1.0", "artifacts": [{"report": {"path": f"{NAME}.Report"}}], "settings": {"enableAutoRecovery": True}})
write(SEM / ".platform", {"$schema": platform, "metadata": {"type": "SemanticModel", "displayName": NAME},
                          "config": {"version": "2.0", "logicalId": "8d3c2a51-6f0e-4b7a-9c1d-5e2f3a4b6c70"}})
write(SEM / "definition.pbism", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
    "version": "1.0", "settings": {}})
write(SEM / "model.bim", model)

write(REP / ".platform", {"$schema": platform, "metadata": {"type": "Report", "displayName": NAME},
                          "config": {"version": "2.0", "logicalId": "2b7e9f14-3c5d-4e6a-8b9c-0d1e2f3a4b5c"}})
write(REP / "definition.pbir", {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
    "version": "4.0", "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}}})
DEF = REP / "definition"
write(DEF / "version.json", {"$schema": f"{S}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
write(DEF / "report.json", {
    "$schema": f"{S}/report/1.3.0/schema.json",
    "themeCollection": {
        "baseTheme": {"name": BASE_THEME, "reportVersionAtImport": "5.68", "type": "SharedResources"},
        "customTheme": {"name": CUSTOM_THEME, "reportVersionAtImport": "5.68", "type": "RegisteredResources"}},
    "layoutOptimization": "None",
    "resourcePackages": [
        {"name": "SharedResources", "type": "SharedResources",
         "items": [{"name": BASE_THEME, "path": f"BaseThemes/{BASE_THEME}.json", "type": "BaseTheme"}]},
        {"name": "RegisteredResources", "type": "RegisteredResources",
         "items": [{"name": CUSTOM_THEME, "path": CUSTOM_THEME, "type": "CustomTheme"}]}],
    "settings": {"useStylableVisualContainerHeader": True, "defaultFilterActionIsDataFilter": True,
                 "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True, "useEnhancedTooltips": True}})
base_copy = REP / f"StaticResources/SharedResources/BaseThemes/{BASE_THEME}.json"
if not base_copy.exists():  # first run on a machine: take Power BI's own base theme from the Desktop install
    install = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-AppxPackage Microsoft.MicrosoftPowerBIDesktop).InstallLocation"],
                             capture_output=True, text=True).stdout.strip()
    base = Path(install) / f"bin/WebView2Resources/minerva/sharedresources/BaseThemes/{BASE_THEME}.json"
    assert install and base.exists(), "base theme not found: install Power BI Desktop from the Microsoft Store"
    base_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(base, base_copy)
(REP / "StaticResources/RegisteredResources").mkdir(parents=True, exist_ok=True)
shutil.copy(HERE / "05-theme.json", REP / f"StaticResources/RegisteredResources/{CUSTOM_THEME}")

write(DEF / "pages/pages.json", {"$schema": f"{S}/pagesMetadata/1.0.0/schema.json",
                                 "pageOrder": [p[0] for p in PAGES], "activePageName": ACTIVE})
count = 0
for name, page_json, visuals in PAGES:
    write(DEF / f"pages/{name}/page.json", page_json)
    for v in visuals:
        assert len(v["name"]) <= 50, v["name"]
        write(DEF / f"pages/{name}/visuals/{v['name']}/visual.json", v)
        count += 1
write(HERE / ".gitignore", "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")
print(f"written {NAME}.pbip: {len(PAGES)} pages, {count} visuals, {len(MEASURES)} measures, "
      f"{len(model['model']['tables'])} tables, {len(model['model']['relationships'])} relationships, "
      f"{len(model['model']['roles'])} roles; output folder {OUTPUT}")
