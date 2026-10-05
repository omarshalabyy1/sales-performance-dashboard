"""The one place client values come from: config/client.yaml. `python config.py` checks the input files."""

from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).parent
FILES = ["orders", "items", "products", "sellers", "customers", "reviews", "category_names", "regions"]
# The standard columns every input file must map (columns.<file>.<standard> in client.yaml).
STANDARD = {
    "orders": ["order_id", "customer_id", "status", "purchased_at", "delivered_at", "estimated_at"],
    "items": ["order_id", "item_no", "product_id", "seller_id", "price", "freight"],
    "products": ["product_id", "category"],
    "sellers": ["seller_id", "city", "state"],
    "customers": ["customer_id", "person_id", "city", "state"],
    "reviews": ["order_id", "score", "answered_at"],
    "category_names": ["category", "name"],
}
REQUIRED = (
    ["client.name", "client.currency", "client.decimals"]
    + [f"inputs.{f}" for f in FILES]
    + [f"columns.{f}.{c}" for f, cols in STANDARD.items() for c in cols]
    + ["rules.sale_statuses", "rules.late_after_days",
       "report.title", "report.compare_year", "report.top_categories", "report.top_sellers_percent",
       "report.colours.data", "report.colours.text", "report.colours.muted",
       "report.colours.page", "report.colours.line", "report.colours.danger"]
)


def load_config():
    try:
        cfg = yaml.safe_load((ROOT / "config" / "client.yaml").read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        line = error.problem_mark.line + 1 if getattr(error, "problem_mark", None) else "?"
        raise SystemExit(f"config/client.yaml is not valid YAML near line {line} (quote a value with # or :)")
    for key in REQUIRED:
        node = cfg
        for part in key.split("."):
            if not isinstance(node, dict) or part not in node:
                raise SystemExit(f"config/client.yaml is missing {key}")
            node = node[part]
    cfg["input_dir"] = ROOT / "data" / "input"
    cfg["output_dir"] = ROOT / "output"
    return cfg


def check_inputs(cfg):
    """Stop with one line if an input file is missing or lacks a required column."""
    for name in FILES:
        path = cfg["input_dir"] / cfg["inputs"][name]
        if not path.exists():
            raise SystemExit(f"missing data/input/{path.name} (inputs.{name} in config/client.yaml)")
        header = pd.read_csv(path, nrows=0, encoding="utf-8-sig").columns
        wanted = ["state", "region"] if name == "regions" else cfg["columns"][name].values()
        missing = [c for c in wanted if c not in header]
        if missing:
            raise SystemExit(f"data/input/{path.name}: missing column(s): {', '.join(missing)}")


if __name__ == "__main__":
    check_inputs(load_config())
    print("config and input files OK")
