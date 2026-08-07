#!/usr/bin/env python
# coding: utf-8

import calendar
import configparser
import os
import re

import pandas as pd
import xlwings as xw


# =============================================================================
# 1. 项目参数
# =============================================================================

try:
    project_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    project_dir = os.getcwd()

root_dir = os.path.join(project_dir, "1.原始数据")
save_dir = os.path.join(project_dir, "2.运行结果")
business_file = os.path.join(root_dir, "sap_business_config.ini")
business_section = "FI_GL064"

template_keywords = ["CD02_会计凭证导入模板", "会计凭证导入模板"]

summary_required_columns = [
    "项目编号",
    "参考号",
    "物料消耗/材料成本",
    "职工薪酬/人工",
    "其他费用/设备成本",
    "其他费用/其他辅助成本",
    "物料消耗/工序委外",
    "总成本",
    "转出科目",
]

template_write_columns = [
    "公司代码",
    "凭证类型",
    "凭证日期",
    "记账日期",
    "汇率换算日期",
    "货币",
    "凭证抬头文本",
    "参考号",
    "总账科目",
    "凭证货币金额",
    "成本中心",
    "行项目文本",
]


# =============================================================================
# 2. 可复用的 Excel 与字段处理函数
# =============================================================================

def normalize_header(value):
    text = "" if value is None else str(value)
    text = text.replace("：", ":").replace("\xa0", " ")
    return re.sub(r"\s+", "", text).casefold()


def normalize_code(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return re.sub(r"\.0+$", "", str(value).strip())


def to_amount(value, field_name, project_code):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    text = str(value).replace(",", "").replace("，", "").strip()
    if text in ("", "-", "--"):
        return 0.0
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(
            f"项目 {project_code} 的字段“{field_name}”不是有效金额：{value}"
        ) from exc


def find_summary_file(expected_name):
    if not os.path.isdir(save_dir):
        raise FileNotFoundError(f"运行结果目录不存在：{save_dir}")
    files = [
        os.path.join(save_dir, name)
        for name in os.listdir(save_dir)
        if not name.startswith("~$")
        and name == expected_name
        and name.casefold().endswith((".xlsx", ".xlsm", ".xls"))
    ]
    if not files:
        raise FileNotFoundError(f"{save_dir} 下未找到当期结果文件：{expected_name}")
    if len(files) > 1:
        raise RuntimeError(f"匹配到多个停案项目结果文件，请只保留当期文件：{files}")
    return files[0]


def find_template_file():
    files = []
    for name in os.listdir(project_dir):
        lower_name = name.casefold()
        if name.startswith("~$") or not lower_name.endswith((".xlsx", ".xlsm", ".xls")):
            continue
        if any(keyword.casefold() in lower_name for keyword in template_keywords):
            files.append(os.path.join(project_dir, name))
    if not files:
        raise FileNotFoundError(
            "项目根目录下未找到会计凭证导入模板。"
            "请把只有表头的模板放在与“1.原始数据”同级的位置。"
        )
    if len(files) > 1:
        raise RuntimeError(f"匹配到多个会计凭证导入模板，请只保留一个：{files}")
    return files[0]


def read_sheet(path, sheet_name):
    app = None
    wb = None
    try:
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        wb = app.books.open(path, update_links=False, read_only=True)
        sheet = wb.sheets[sheet_name]
        data = sheet.used_range.value
        if data is None:
            return pd.DataFrame()
        if not isinstance(data, list):
            data = [[data]]
        elif data and not isinstance(data[0], list):
            data = [data]
        headers = ["" if value is None else str(value).strip() for value in data[0]]
        return pd.DataFrame(data[1:], columns=headers).dropna(how="all").reset_index(drop=True)
    finally:
        if wb is not None:
            try:
                wb.close()
            except Exception:
                pass
        if app is not None:
            try:
                app.quit()
            except Exception:
                app.kill()


def locate_dataframe_columns(df, required_columns, source_name):
    actual_by_normalized = {
        normalize_header(column): column
        for column in df.columns
        if normalize_header(column)
    }
    result = {}
    missing = []
    for required in required_columns:
        actual = actual_by_normalized.get(normalize_header(required))
        if actual is None:
            missing.append(required)
        else:
            result[required] = actual
    if missing:
        raise KeyError(f"{source_name} 缺少字段：{missing}")
    return result


# =============================================================================
# 3. 读取期间和停案项目汇总
# =============================================================================

business_config = configparser.ConfigParser()
business_config.read(business_file, encoding="utf-8-sig")
if not business_config.has_section(business_section):
    raise KeyError(f"业务配置缺少 section：[{business_section}]")

fin_period = business_config[business_section].get("fin_period", "").strip()
if not re.fullmatch(r"\d{6}", fin_period):
    raise ValueError(f"fin_period 应为 YYYYMM，当前值：{fin_period}")

com_lists = business_config[business_section].get("com_lists", "").strip()
company_codes = list(dict.fromkeys(re.findall(r"(?<!\d)\d{4}(?!\d)", com_lists)))
if len(company_codes) != 1:
    raise ValueError(
        f"com_lists 必须且只能包含一个四位公司代码，当前值：{com_lists}"
    )
company_code = company_codes[0]

year = int(fin_period[:4])
month = int(fin_period[4:6])
if not 1 <= month <= 12:
    raise ValueError(f"fin_period 月份无效：{fin_period}")
period_end = f"{year:04d}{month:02d}{calendar.monthrange(year, month)[1]:02d}"

summary_name = f"CD01_{year}年{month}月停案项目成本明细.xlsx"
summary_path = find_summary_file(summary_name)
template_path = find_template_file()
df_summary_raw = read_sheet(summary_path, "停案项目汇总")
summary_map = locate_dataframe_columns(
    df_summary_raw,
    summary_required_columns,
    "停案项目汇总",
)
df_summary = pd.DataFrame({
    target: df_summary_raw[source]
    for target, source in summary_map.items()
})
df_summary = df_summary[
    df_summary["项目编号"].apply(normalize_code) != ""
].reset_index(drop=True)
if df_summary.empty:
    raise ValueError("停案项目汇总没有可生成凭证的数据行。")

missing_transfer_account = df_summary[
    df_summary["转出科目"].apply(normalize_code) == ""
]
if not missing_transfer_account.empty:
    projects = missing_transfer_account["项目编号"].apply(normalize_code).tolist()
    raise ValueError(
        f"以下项目没有转出科目，不能生成凭证模板，请先检查异常清单：{projects}"
    )


# =============================================================================
# 4. 每个项目按固定顺序生成六行凭证数据
# =============================================================================

voucher_rows = []
for _, project_row in df_summary.iterrows():
    project_code = normalize_code(project_row["项目编号"])
    reference = project_row["参考号"]
    transfer_account = normalize_code(project_row["转出科目"])

    amount_fields = [
        "物料消耗/材料成本",
        "职工薪酬/人工",
        "其他费用/设备成本",
        "其他费用/其他辅助成本",
        "物料消耗/工序委外",
    ]
    amounts = [
        to_amount(project_row[field], field, project_code)
        for field in amount_fields
    ]
    total_cost = to_amount(project_row["总成本"], "总成本", project_code)

    accounts = [
        "6601150000",
        "6601080003",
        "6601990000",
        "6601990000",
        "6601150000",
        transfer_account,
    ]
    line_texts = [
        f"停案项目费用转入管理费用-材料成本{project_code}",
        f"停案项目费用转入管理费用-人工成本{project_code}",
        f"停案项目费用转入管理费用-设备成本{project_code}",
        f"停案项目费用转入管理费用-其他辅助成本{project_code}",
        f"停案项目费用转入管理费用-工序委外{project_code}",
        f"停案项目费用转入{project_code}",
    ]

    for line_index in range(6):
        voucher_rows.append({
            "公司代码": company_code,
            "凭证类型": "SA",
            "凭证日期": period_end,
            "记账日期": period_end,
            "汇率换算日期": period_end,
            "货币": "CNY",
            "凭证抬头文本": f"停案项目转入管理费用{project_code}",
            "参考号": reference,
            "总账科目": accounts[line_index],
            "凭证货币金额": amounts[line_index] if line_index < 5 else -total_cost,
            "成本中心": "150A010000" if line_index < 5 else "",
            "行项目文本": line_texts[line_index],
        })

df_voucher = pd.DataFrame(voucher_rows, columns=template_write_columns)


# =============================================================================
# 5. 打开空模板，按列名写入并另存结果
# =============================================================================

os.makedirs(save_dir, exist_ok=True)
template_ext = os.path.splitext(template_path)[1]
output_path = os.path.join(save_dir, f"CD02_会计凭证导入模板{template_ext}")
if os.path.exists(output_path):
    try:
        os.remove(output_path)
    except PermissionError as exc:
        raise PermissionError(f"请先关闭已打开的结果文件：{output_path}") from exc

app = None
wb = None
try:
    app = xw.App(visible=False, add_book=False)
    app.display_alerts = False
    app.screen_updating = False
    wb = app.books.open(template_path, update_links=False)

    if "导入模板" in [sheet.name for sheet in wb.sheets]:
        sheet = wb.sheets["导入模板"]
    else:
        visible_sheets = [sheet for sheet in wb.sheets if sheet.api.Visible == -1]
        sheet = visible_sheets[0]

    last_column = sheet.used_range.last_cell.column
    template_headers = sheet.range((1, 1), (1, last_column)).value
    if not isinstance(template_headers, list):
        template_headers = [template_headers]
    template_column_numbers = {
        normalize_header(header): index + 1
        for index, header in enumerate(template_headers)
        if normalize_header(header)
    }

    missing_template_columns = [
        column
        for column in template_write_columns
        if normalize_header(column) not in template_column_numbers
    ]
    if missing_template_columns:
        raise KeyError(f"会计凭证导入模板缺少字段：{missing_template_columns}")

    if len(df_voucher) > 0:
        last_row = len(df_voucher) + 1
        for column in template_write_columns:
            column_number = template_column_numbers[normalize_header(column)]
            values = [[value] for value in df_voucher[column].tolist()]
            target_range = sheet.range((2, column_number), (last_row, column_number))
            if column in (
                "公司代码",
                "凭证日期",
                "记账日期",
                "汇率换算日期",
                "总账科目",
                "成本中心",
            ):
                target_range.number_format = "@"
            elif column == "凭证货币金额":
                target_range.number_format = "#,##0.00;[Red]-#,##0.00;-"
            target_range.value = values

    wb.save(output_path)
finally:
    if wb is not None:
        try:
            wb.close()
        except Exception:
            pass
    if app is not None:
        try:
            app.quit()
        except Exception:
            app.kill()

print(f"✅ 项目数：{len(df_summary)}")
print(f"✅ 凭证行数：{len(df_voucher)}")
print(f"结果文件：{output_path}")
