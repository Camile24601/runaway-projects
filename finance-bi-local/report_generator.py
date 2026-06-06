#!/usr/bin/env python3
"""Generate a local, privacy-preserving finance BI HTML report."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


def load_profile(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_data(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported input file: {path}")


def first_existing(columns: Iterable[str], candidates: Iterable[str]) -> Optional[str]:
    column_set = {str(c).strip(): c for c in columns}
    for candidate in candidates:
        if candidate in column_set:
            return column_set[candidate]
    return None


def detect_fields(df: pd.DataFrame, profile: Dict[str, Any]) -> Dict[str, Optional[str]]:
    candidates = profile["field_candidates"]
    return {name: first_existing(df.columns, cols) for name, cols in candidates.items()}


def to_number(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.replace(",", "", regex=False).str.replace("¥", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def masked_label(value: Any, prefix: str = "对象") -> str:
    raw = "" if pd.isna(value) else str(value)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:6].upper()
    return f"{prefix}-{digest}"


def safe_div(numerator: float, denominator: float) -> Optional[float]:
    if denominator in (0, None) or pd.isna(denominator):
        return None
    return float(numerator) / float(denominator)


def pct(value: Optional[float]) -> str:
    if value is None or pd.isna(value):
        return "无法计算"
    return f"{value * 100:.1f}%"


def signed_pct(value: Optional[float]) -> str:
    if value is None or pd.isna(value):
        return "无法计算"
    return f"{value * 100:+.1f}%"


def index_value(value: Optional[float], base: Optional[float]) -> Optional[float]:
    if value is None or base in (0, None) or pd.isna(value) or pd.isna(base):
        return None
    return float(value) / float(base) * 100


def fmt_index(value: Optional[float]) -> str:
    if value is None or pd.isna(value):
        return "无法计算"
    return f"{value:.1f}"


def normalize_period(df: pd.DataFrame, date_col: Optional[str], period: str) -> pd.Series:
    if not date_col:
        return pd.Series(["未识别日期"] * len(df), index=df.index)
    dates = pd.to_datetime(df[date_col], errors="coerce")
    if period == "D":
        return dates.dt.strftime("%Y-%m-%d").fillna("未识别日期")
    if period == "Y":
        return dates.dt.strftime("%Y").fillna("未识别日期")
    return dates.dt.strftime("%Y-%m").fillna("未识别日期")


def svg_bar_chart(rows: List[Dict[str, Any]], label_key: str, value_key: str, title: str) -> str:
    if not rows:
        return empty_state("当前字段不足，无法生成图表。")
    max_value = max([abs(float(r.get(value_key) or 0)) for r in rows] or [1]) or 1
    bars = []
    for row in rows:
        label = html.escape(str(row.get(label_key, "")))
        value = row.get(value_key)
        width = max(2, min(100, abs(float(value or 0)) / max_value * 100))
        bars.append(
            f"""
            <div class="bar-row">
              <div class="bar-label" title="{label}">{label}</div>
              <div class="bar-track"><div class="bar-fill" style="width:{width:.1f}%"></div></div>
              <div class="bar-value">{fmt_index(value)}</div>
            </div>
            """
        )
    return f"""
    <section class="panel">
      <h2>{html.escape(title)}</h2>
      <div class="bar-chart">{''.join(bars)}</div>
    </section>
    """


def table(headers: List[str], rows: List[List[Any]]) -> str:
    if not rows:
        return empty_state("当前字段不足，无法生成表格。")
    thead = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row) + "</tr>")
    return f"<div class=\"table-wrap\"><table><thead><tr>{thead}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"


def narrative(items: List[str]) -> str:
    if not items:
        return ""
    return f"<div class=\"narrative\">{''.join(f'<p>{html.escape(item)}</p>' for item in items)}</div>"


def empty_state(message: str) -> str:
    return f"<div class=\"empty\">{html.escape(message)}</div>"


def prepare_df(df: pd.DataFrame, fields: Dict[str, Optional[str]], profile: Dict[str, Any], period: str) -> pd.DataFrame:
    work = df.copy()
    work["_period"] = normalize_period(work, fields.get("date"), period)
    for key in ["purchase_amount", "sales_amount", "cost_amount", "profit_amount", "unit_price", "quantity", "payment_days"]:
        col = fields.get(key)
        if col:
            work[f"_{key}"] = to_number(work[col])
    prefix = profile.get("privacy", {}).get("dimension_mask_prefix", "对象")
    for key in ["customer", "supplier"]:
        col = fields.get(key)
        if col:
            work[f"_{key}_masked"] = work[col].map(lambda v: masked_label(v, prefix))
    return work


def build_purchase_analysis(df: pd.DataFrame, fields: Dict[str, Optional[str]], top_n: int) -> str:
    if "_purchase_amount" not in df:
        return svg_bar_chart([], "period", "index", "采购金额趋势指数")
    by_period = df.groupby("_period", dropna=False)["_purchase_amount"].sum().sort_index()
    base = by_period.iloc[0] if len(by_period) else None
    rows = [{"period": p, "index": index_value(v, base)} for p, v in by_period.items()]
    notes = []
    if len(by_period) >= 2:
        first_period, last_period = by_period.index[0], by_period.index[-1]
        notes.append(
            f"采购金额趋势以 {first_period} 为 100，{last_period} 指数为 {fmt_index(index_value(by_period.iloc[-1], base))}；该指标只表达规模变化，不展示原始金额。"
        )
        max_period = by_period.idxmax()
        notes.append(f"采购金额指数最高期间为 {max_period}，需要结合采购数量、品类结构和价格变化进一步拆解。")
    supplier_html = ""
    if "_supplier_masked" in df:
        total = df["_purchase_amount"].sum()
        supplier = df.groupby("_supplier_masked")["_purchase_amount"].sum().sort_values(ascending=False).head(top_n)
        supplier_rows = [[name, pct(safe_div(value, total))] for name, value in supplier.items()]
        supplier_html = f"""
        <section class="panel">
          <h2>供应商采购占比 Top {top_n}</h2>
          {table(["脱敏供应商", "采购金额占比"], supplier_rows)}
        </section>
        """
    return f"""
    <section class="panel">
      <h2>采购金额分析说明</h2>
      {narrative(notes)}
    </section>
    """ + svg_bar_chart(rows, "period", "index", "采购金额趋势指数（首期=100）") + supplier_html


def build_profit_analysis(df: pd.DataFrame) -> str:
    if "_profit_amount" not in df:
        return svg_bar_chart([], "period", "index", "利润趋势指数")
    by_period = df.groupby("_period", dropna=False)["_profit_amount"].sum().sort_index()
    base = by_period.iloc[0] if len(by_period) else None
    rows = [{"period": p, "index": index_value(v, base)} for p, v in by_period.items()]
    notes = []
    if len(by_period) >= 2:
        first_period, last_period = by_period.index[0], by_period.index[-1]
        notes.append(
            f"利润趋势以 {first_period} 为 100，{last_period} 指数为 {fmt_index(index_value(by_period.iloc[-1], base))}；指数用于保护金额敏感性。"
        )
        notes.append("利润变化可能受到收入、成本、产品结构、价格和费用归集影响；当前报告只根据已提供字段展示结果，不推断经营原因。")
    margin_html = ""
    if "_sales_amount" in df:
        margin_rows = []
        sales = df.groupby("_period", dropna=False)["_sales_amount"].sum().sort_index()
        for period_name, profit in by_period.items():
            margin_rows.append([period_name, pct(safe_div(profit, sales.get(period_name)))])
        margin_html = f"""
        <section class="panel">
          <h2>利润率趋势</h2>
          {table(["期间", "利润率"], margin_rows)}
        </section>
        """
    return f"""
    <section class="panel">
      <h2>利润分析说明</h2>
      {narrative(notes)}
    </section>
    """ + svg_bar_chart(rows, "period", "index", "利润趋势指数（首期=100）") + margin_html


def build_unit_price_analysis(df: pd.DataFrame, fields: Dict[str, Optional[str]], top_n: int) -> str:
    if "_unit_price" not in df:
        return empty_state("未识别单价字段，跳过单价变动分析。")
    product_col = fields.get("product")
    supplier_col = "_supplier_masked" if "_supplier_masked" in df else None
    if not product_col or not supplier_col:
        return f"""
        <section class="panel">
          <h2>单价分析</h2>
          {empty_state("单价横向/纵向分析需要同时识别产品/物料、供应商和单价字段。当前字段不足，无法按同物料口径比较。")}
        </section>
        """

    work = df.dropna(subset=["_unit_price"]).copy()
    horizontal_rows = []
    horizontal_groups = work.groupby(["_period", product_col], dropna=False)
    for (period_name, product), group in horizontal_groups:
        supplier_count = group[supplier_col].nunique(dropna=False)
        if supplier_count < 2:
            continue
        supplier_avg = group.groupby(supplier_col)["_unit_price"].mean()
        median_price = supplier_avg.median()
        for supplier, avg_price in supplier_avg.items():
            deviation = safe_div(avg_price - median_price, median_price)
            horizontal_rows.append({
                "period": period_name,
                "product": product,
                "supplier": supplier,
                "index": index_value(avg_price, median_price),
                "deviation": deviation,
                "peer_count": supplier_count,
            })
    horizontal_rows = sorted(
        horizontal_rows,
        key=lambda r: abs(r["deviation"] or 0),
        reverse=True,
    )[:top_n]
    horizontal_table = [
        [r["period"], r["product"], r["supplier"], fmt_index(r["index"]), signed_pct(r["deviation"]), r["peer_count"]]
        for r in horizontal_rows
    ]

    vertical_rows = []
    vertical_groups = work.groupby([product_col, supplier_col], dropna=False)
    for (product, supplier), group in vertical_groups:
        by_period = group.groupby("_period")["_unit_price"].mean().sort_index()
        if len(by_period) < 2:
            continue
        first_period = by_period.index[0]
        first_price = by_period.iloc[0]
        prev_price = None
        for period_name, avg_price in by_period.items():
            if period_name == first_period:
                prev_price = avg_price
                continue
            change_from_first = safe_div(avg_price - first_price, first_price)
            change_from_prev = safe_div(avg_price - prev_price, prev_price)
            vertical_rows.append({
                "product": product,
                "supplier": supplier,
                "period": period_name,
                "index": index_value(avg_price, first_price),
                "from_first": change_from_first,
                "from_prev": change_from_prev,
                "base_period": first_period,
            })
            prev_price = avg_price
    vertical_rows = sorted(
        vertical_rows,
        key=lambda r: max(abs(r["from_first"] or 0), abs(r["from_prev"] or 0)),
        reverse=True,
    )[:top_n]
    vertical_table = [
        [
            r["product"],
            r["supplier"],
            r["period"],
            fmt_index(r["index"]),
            signed_pct(r["from_first"]),
            signed_pct(r["from_prev"]),
            r["base_period"],
        ]
        for r in vertical_rows
    ]

    notes = [
        "横向比较口径：同一期间、同一产品/物料内，对不同供应商的平均单价进行比较，基准为该组供应商单价中位数=100。",
        "纵向比较口径：同一产品/物料、同一供应商内，按期间比较平均单价，基准为该组合首期单价=100。",
        "单价属于金额类信息，报告不展示原始单价，只展示指数和偏离比例。"
    ]
    if horizontal_rows:
        top = horizontal_rows[0]
        notes.append(
            f"横向偏离最大的记录为 {top['period']}、{top['product']}、{top['supplier']}，单价指数 {fmt_index(top['index'])}，较同组中位数 {signed_pct(top['deviation'])}。"
        )
    if vertical_rows:
        top = vertical_rows[0]
        notes.append(
            f"纵向变动最大的记录为 {top['product']}、{top['supplier']}、{top['period']}，较首期 {signed_pct(top['from_first'])}，较上期 {signed_pct(top['from_prev'])}。"
        )
    if not horizontal_rows:
        notes.append("横向比较未形成结果，通常是因为同一期间、同一产品下不足两个供应商。")
    if not vertical_rows:
        notes.append("纵向比较未形成结果，通常是因为同一产品、同一供应商没有跨多个期间的数据。")

    return f"""
    <section class="panel">
      <h2>单价分析说明</h2>
      {narrative(notes)}
    </section>
    <section class="panel">
      <h2>单价横向比较 Top {top_n}</h2>
      {table(["期间", "产品/物料", "脱敏供应商", "单价指数", "较同组中位数", "同组供应商数"], horizontal_table)}
    </section>
    <section class="panel">
      <h2>单价纵向变动 Top {top_n}</h2>
      {table(["产品/物料", "脱敏供应商", "期间", "单价指数", "较首期", "较上期", "基准期间"], vertical_table)}
    </section>
    """


def build_payment_days_analysis(df: pd.DataFrame) -> str:
    if "_payment_days" not in df:
        return empty_state("未识别账期字段，跳过账期变动分析。")
    by_period = df.groupby("_period", dropna=False)["_payment_days"].mean().sort_index()
    first = by_period.iloc[0] if len(by_period) else None
    rows = []
    for period_name, value in by_period.items():
        delta = value - first if first is not None and not pd.isna(first) else None
        rows.append([period_name, f"{value:.1f}", "无法计算" if delta is None else f"{delta:+.1f}"])
    return f"""
    <section class="panel">
      <h2>账期变动分析</h2>
      {narrative(["账期分析展示平均账期天数及其相对首期的变化。账期拉长或缩短只表示数据结果变化，不直接推断付款政策、议价能力或客户信用变化。"])}
      {table(["期间", "平均账期（天）", "较首期变化（天）"], rows)}
    </section>
    """


def build_data_notes(fields: Dict[str, Optional[str]], profile: Dict[str, Any]) -> str:
    detected = [[name, col or "未识别"] for name, col in fields.items()]
    rules = [
        "报告默认不展示任何原始金额，仅展示指数、占比、变化率或利润率。",
        "客户与供应商默认使用稳定哈希标签脱敏，同一对象在同一报告中标签一致。",
        "原因解释只基于数据字段；当前数据没有原因字段时，不推断业务原因。",
        "如字段未识别，对应分析模块会跳过或标注无法判断。"
    ]
    return f"""
    <section class="panel">
      <h2>数据口径与隐私规则</h2>
      {table(["字段类型", "识别结果"], detected)}
      <ul class="notes">{''.join(f"<li>{html.escape(rule)}</li>" for rule in rules)}</ul>
    </section>
    """


def build_html_report(df: pd.DataFrame, profile: Dict[str, Any], source_name: str, period: str) -> str:
    fields = detect_fields(df, profile)
    work = prepare_df(df, fields, profile, period)
    top_n = int(profile.get("top_n", 8))
    sections = [
        build_purchase_analysis(work, fields, top_n),
        build_profit_analysis(work),
        build_unit_price_analysis(work, fields, top_n),
        build_payment_days_analysis(work),
        build_data_notes(fields, profile),
    ]
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(profile.get("report_title", "本地财务 BI 分析报告"))}</title>
  <style>
    :root {{
      --bg: #f6f7f9;
      --ink: #18212f;
      --muted: #667085;
      --line: #d9dee7;
      --panel: #ffffff;
      --accent: #176b87;
      --accent-2: #d97706;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
      background: var(--bg);
      color: var(--ink);
      letter-spacing: 0;
    }}
    header {{
      padding: 32px 40px 22px;
      background: #ffffff;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{ margin: 0 0 10px; font-size: 28px; line-height: 1.25; }}
    .meta {{ color: var(--muted); font-size: 14px; }}
    main {{ width: min(1180px, calc(100% - 32px)); margin: 24px auto 48px; }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 18px;
    }}
    h2 {{ margin: 0 0 16px; font-size: 18px; }}
    .bar-row {{
      display: grid;
      grid-template-columns: minmax(96px, 180px) 1fr 76px;
      gap: 12px;
      align-items: center;
      min-height: 34px;
      margin: 8px 0;
    }}
    .bar-label {{
      color: var(--muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-size: 13px;
    }}
    .bar-track {{
      height: 14px;
      background: #e8edf2;
      border-radius: 999px;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
    }}
    .bar-value {{
      font-variant-numeric: tabular-nums;
      text-align: right;
      color: var(--ink);
      font-size: 13px;
    }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 10px 8px; text-align: left; }}
    th {{ color: var(--muted); font-weight: 600; background: #fafbfc; }}
    .empty {{
      border: 1px dashed var(--line);
      border-radius: 8px;
      padding: 16px;
      color: var(--muted);
      background: #fbfcfd;
    }}
    .notes {{ margin: 16px 0 0; color: var(--muted); line-height: 1.8; }}
    @media (max-width: 720px) {{
      header {{ padding: 24px 18px 18px; }}
      main {{ width: calc(100% - 20px); margin-top: 12px; }}
      .panel {{ padding: 14px; }}
      .bar-row {{ grid-template-columns: 88px 1fr 56px; gap: 8px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(profile.get("report_title", "本地财务 BI 分析报告"))}</h1>
    <div class="meta">数据源：{html.escape(source_name)} · 报告周期：{html.escape(period)} · 金额已脱敏</div>
  </header>
  <main>
    {''.join(sections)}
  </main>
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a local finance BI HTML report.")
    parser.add_argument("input", type=Path, help="Input Excel or CSV file")
    parser.add_argument("--output", "-o", type=Path, default=Path("report.html"), help="Output HTML path")
    parser.add_argument("--profile", type=Path, default=Path("config/analysis_profile.json"), help="Analysis profile JSON")
    parser.add_argument("--period", choices=["D", "M", "Y"], default=None, help="D=day, M=month, Y=year")
    args = parser.parse_args()

    profile = load_profile(args.profile)
    period = args.period or profile.get("default_period", "M")
    df = load_data(args.input)
    html_report = build_html_report(df, profile, args.input.name, period)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_report, encoding="utf-8")
    print(f"Generated: {args.output}")


if __name__ == "__main__":
    main()
