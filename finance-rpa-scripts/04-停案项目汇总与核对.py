#!/usr/bin/env python
# coding: utf-8

# In[1]:


import configparser
import os
import re

import pandas as pd
import xlwings as xw


# # 1. 项目参数

# In[3]:


project_dir = os.getcwd()

root_dir = os.path.join(project_dir, "1.原始数据")
save_dir = os.path.join(project_dir, "2.运行结果")
business_file = os.path.join(root_dir, "sap_business_config.ini")
business_section = "FI_GL064"

email_prefixes = ["01-邮件数据", "01_01-邮件数据"]
fagll03h_prefixes = ["02_01-FAGLL03H", "02_01-fagll03h"]

email_columns = [
    "创建日期",
    "项目编号",
    "项目名称",
    "客户编号",
    "客户名称",
    "实际成本-不含立项",
    "材料成本-不含立项",
    "人工成本-不含立项",
    "设备成本-不含立项",
    "其他辅助成本-不含立项",
    "工序委外-不含立项",
    "TECO日期",
]

fagll03h_columns = [
    "公司代码",
    "WBS元素",
    "总帐帐目",
    "总账科目：长文本",
    "凭证日期",
    "过账日期",
    "凭证类型",
    "凭证编号",
    "公司代码货币价值",
    "公司代码货币代码",
    "凭证货币价值",
    "凭证货币代码",
    "集团货币价值",
    "集团货币代码",
    "文本",
    "输入时间",
    "输入日期",
]

summary_columns = email_columns + [
    "参考号",
    "物料消耗/材料成本",
    "职工薪酬/人工",
    "其他费用/设备成本",
    "其他费用/其他辅助成本",
    "物料消耗/工序委外",
    "总成本",
    "转入成本中心",
    "转出科目",
    "FAGLL03H成本",
    "核对",
]


# # 2. Excel 与字段处理

# In[4]:


def normalize_header(value):
    text = "" if value is None else str(value)
    text = text.replace("：", ":").replace("\xa0", " ")
    return re.sub(r"\s+", "", text).casefold()


def normalize_code(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    return re.sub(r"\.0+$", "", text)


def find_excel(root_path, prefixes):
    if not os.path.isdir(root_path):
        raise FileNotFoundError(f"目录不存在：{root_path}")
    files = []
    for name in os.listdir(root_path):
        lower_name = name.casefold()
        if name.startswith("~$") or not lower_name.endswith((".xlsx", ".xlsm", ".xls")):
            continue
        if any(lower_name.startswith(prefix.casefold()) for prefix in prefixes):
            files.append(os.path.join(root_path, name))
    if not files:
        raise FileNotFoundError(
            f"{root_path} 下未找到前缀为 {prefixes} 的 Excel 文件。"
        )
    if len(files) > 1:
        raise RuntimeError(f"匹配到多个文件，请只保留一个：{files}")
    return files[0]


def read_sheet(path, sheet_name=0):
    app = None
    wb = None
    try:
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        wb = app.books.open(path, update_links=False, read_only=True)
        visible_sheets = [sheet for sheet in wb.sheets if sheet.api.Visible == -1]
        if isinstance(sheet_name, int):
            sheet = visible_sheets[sheet_name]
        else:
            sheet = wb.sheets[sheet_name]
        data = sheet.used_range.value
        if data is None:
            return pd.DataFrame()
        if not isinstance(data, list):
            data = [[data]]
        elif data and not isinstance(data[0], list):
            data = [data]
        if len(data) < 1:
            return pd.DataFrame()
        headers = ["" if value is None else str(value).strip() for value in data[0]]
        result = pd.DataFrame(data[1:], columns=headers)
        return result.dropna(how="all").reset_index(drop=True)
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


def locate_columns(df, required_columns, source_name):
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


def write_dataframe(sheet, df):
    clean_df = df.astype(object).where(pd.notna(df), None)
    values = [df.columns.tolist()] + clean_df.values.tolist()
    last_row = max(len(values), 1)
    last_col = max(len(df.columns), 1)
    output_range = sheet.range((1, 1), (last_row, last_col))
    output_range.value = values
    header = sheet.range((1, 1), (1, last_col))
    header.api.Font.Bold = True
    header.color = (189, 215, 238)
    header.api.HorizontalAlignment = -4108
    header.api.VerticalAlignment = -4108
    output_range.api.Borders.LineStyle = 1
    output_range.api.VerticalAlignment = -4108
    output_range.columns.autofit()
    for column_index in range(1, last_col + 1):
        column = sheet.range((1, column_index), (last_row, column_index))
        if column.column_width > 32:
            column.column_width = 32
            column.api.WrapText = True


def write_summary_dataframe(sheet, df):
    """写入停案项目汇总：第一行为分组标题，第二行为字段标题。"""
    clean_df = df.astype(object).where(pd.notna(df), None)
    data_values = clean_df.values.tolist()
    last_row = max(len(data_values) + 2, 2)
    last_col = len(df.columns)
    project_last_col = len(email_columns)
    accounting_first_col = project_last_col + 1

    sheet.range((2, 1), (2, last_col)).value = [df.columns.tolist()]
    if data_values:
        sheet.range((3, 1), (last_row, last_col)).value = data_values

    project_title = sheet.range((1, 1), (1, project_last_col))
    project_title.merge()
    project_title.value = "项目数据"

    accounting_title = sheet.range(
        (1, accounting_first_col), (1, last_col)
    )
    accounting_title.merge()
    accounting_title.value = "账务处理"

    project_header = sheet.range((1, 1), (2, project_last_col))
    accounting_header = sheet.range(
        (1, accounting_first_col), (2, last_col)
    )
    project_header.color = (189, 215, 238)
    accounting_header.color = (255, 230, 153)

    header = sheet.range((1, 1), (2, last_col))
    header.api.Font.Bold = True
    header.api.HorizontalAlignment = -4108
    header.api.VerticalAlignment = -4108

    output_range = sheet.range((1, 1), (last_row, last_col))
    output_range.api.Borders.LineStyle = 1
    output_range.api.VerticalAlignment = -4108
    output_range.columns.autofit()
    for column_index in range(1, last_col + 1):
        column = sheet.range((1, column_index), (last_row, column_index))
        if column.column_width > 32:
            column.column_width = 32
            column.api.WrapText = True


# # 3. 读取期间和输入文件

# In[5]:


business_config = configparser.ConfigParser()
business_config.read(business_file, encoding="utf-8-sig")
if not business_config.has_section(business_section):
    raise KeyError(f"业务配置缺少 section：[{business_section}]")

fin_period = business_config[business_section].get("fin_period", "").strip()
if not re.fullmatch(r"\d{6}", fin_period):
    raise ValueError(f"fin_period 应为 YYYYMM，当前值：{fin_period}")

year = int(fin_period[:4])
month = int(fin_period[4:6])
if not 1 <= month <= 12:
    raise ValueError(f"fin_period 月份无效：{fin_period}")

email_path = find_excel(root_dir, email_prefixes)
fagll03h_path = find_excel(root_dir, fagll03h_prefixes)

df_email_raw = read_sheet(email_path, "sheet1")
df_fagll03h_raw = read_sheet(fagll03h_path, 0)

email_map = locate_columns(df_email_raw, email_columns, "邮件数据")
fagll03h_map = locate_columns(df_fagll03h_raw, fagll03h_columns, "FAGLL03H")

df_email = pd.DataFrame({
    target: df_email_raw[source]
    for target, source in email_map.items()
})
df_fagll03h = pd.DataFrame({
    target: df_fagll03h_raw[source]
    for target, source in fagll03h_map.items()
})

df_email = df_email[
    df_email["项目编号"].apply(normalize_code) != ""
].reset_index(drop=True)
df_fagll03h = df_fagll03h[
    df_fagll03h["WBS元素"].apply(normalize_code) != ""
].reset_index(drop=True)

df_email["_项目键"] = df_email["项目编号"].apply(normalize_code)
df_fagll03h["_WBS键"] = df_fagll03h["WBS元素"].apply(normalize_code)


# # 4. 按 WBS 元素筛选 FAGLL03H，并逐行匹配邮件项目

# In[6]:


project_keys = set(df_email["_项目键"])
df_fagll03h_filtered = df_fagll03h[
    df_fagll03h["_WBS键"].isin(project_keys)
].copy()

# 只验证一个项目不能对应多个不同总帐帐目；不对金额做任何汇总。
account_conflicts = []
project_key_order = list(dict.fromkeys(df_fagll03h_filtered["_WBS键"].tolist()))
for project_key in project_key_order:
    project_rows = df_fagll03h_filtered[
        df_fagll03h_filtered["_WBS键"] == project_key
    ]
    accounts = sorted({
        normalize_code(value)
        for value in project_rows["总帐帐目"]
        if normalize_code(value)
    })
    if len(accounts) > 1:
        account_conflicts.append(f"{project_key}: {accounts}")

if account_conflicts:
    raise ValueError(
        "以下项目匹配到多个不同总帐帐目，程序已停止：\n"
        + "\n".join(account_conflicts)
    )

matched_keys = set(df_fagll03h_filtered["_WBS键"])
df_exception = df_email[
    ~df_email["_项目键"].isin(matched_keys)
][["项目编号", "项目名称"]].copy()
if not df_exception.empty:
    df_exception["异常原因"] = "邮件项目编号未匹配到FAGLL03H的WBS元素"

# 直接逐行关联；SAP 有几条匹配行就保留几条。
df_match_source = df_fagll03h_filtered[
    ["_WBS键", "总帐帐目", "公司代码货币价值"]
].copy()
df_summary = df_email.merge(
    df_match_source,
    how="left",
    left_on="_项目键",
    right_on="_WBS键",
    sort=False,
)

df_summary["参考号"] = range(1, len(df_summary) + 1)
df_summary["物料消耗/材料成本"] = df_summary["材料成本-不含立项"]
df_summary["职工薪酬/人工"] = df_summary["人工成本-不含立项"]
df_summary["其他费用/设备成本"] = df_summary["设备成本-不含立项"]
df_summary["其他费用/其他辅助成本"] = df_summary["其他辅助成本-不含立项"]
df_summary["物料消耗/工序委外"] = df_summary["工序委外-不含立项"]
df_summary["总成本"] = df_summary["实际成本-不含立项"]
df_summary["转入成本中心"] = "150A010000"
df_summary["转出科目"] = df_summary["总帐帐目"].apply(normalize_code)
df_summary["FAGLL03H成本"] = df_summary["公司代码货币价值"]

total_cost = pd.to_numeric(
    df_summary["总成本"].astype(str).str.replace(",", "", regex=False),
    errors="coerce",
)
fagll03h_cost = pd.to_numeric(
    df_summary["FAGLL03H成本"].astype(str).str.replace(",", "", regex=False),
    errors="coerce",
)
df_summary["核对"] = total_cost - fagll03h_cost
df_summary = df_summary[summary_columns]

df_fagll03h_output = df_fagll03h_filtered[fagll03h_columns].copy()


# # 5. 生成结果工作簿

# In[7]:


os.makedirs(save_dir, exist_ok=True)
output_name = f"CD01_{year}年{month}月停案项目成本明细.xlsx"
output_path = os.path.join(save_dir, output_name)
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
    wb = app.books.add()

    sheet_summary = wb.sheets[0]
    sheet_summary.name = "停案项目汇总"
    write_summary_dataframe(sheet_summary, df_summary)

    sheet_fagll03h = wb.sheets.add(after=wb.sheets[-1])
    sheet_fagll03h.name = "FAGLL03H"
    write_dataframe(sheet_fagll03h, df_fagll03h_output)

    if not df_exception.empty:
        sheet_exception = wb.sheets.add(after=wb.sheets[-1])
        sheet_exception.name = "异常清单"
        write_dataframe(sheet_exception, df_exception)

    for sheet in wb.sheets:
        sheet.activate()
        app.api.ActiveWindow.FreezePanes = False
        freeze_cell = "A3" if sheet.name == "停案项目汇总" else "A2"
        sheet.range(freeze_cell).select()
        app.api.ActiveWindow.FreezePanes = True

    sheet_summary.activate()
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

print(f"✅ 停案项目汇总行数：{len(df_summary)}")
print(f"✅ FAGLL03H筛选行数：{len(df_fagll03h_output)}")
print(f"⚠️ 未匹配项目数：{len(df_exception)}")
print(f"结果文件：{output_path}")


# In[ ]:
