#!/usr/bin/env python
# coding: utf-8
"""财务业务处理/结果输出程序母版。

复制本文件后，按逻辑说明、样例数据、目标模板和现有同类脚本替换 TODO 内容。
本母版保留常见的 pandas + xlwings + 配置文件写法，不包含具体会计判断。
"""

import configparser
import os
from datetime import datetime

import numpy as np
import pandas as pd
import xlwings as xw
from dateutil.relativedelta import relativedelta


pd.set_option("display.float_format", lambda x: "%.2f" % x)
pd.options.mode.chained_assignment = None


def get_path(root_dir="1.原始数据", text_num="01"):
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"目录 '{root_dir}' 不存在。")
    paths = [
        os.path.join(root_dir, file_name)
        for file_name in os.listdir(root_dir)
        if not file_name.startswith("~$") and file_name.startswith(text_num)
    ]
    if not paths:
        raise ValueError(f"'{root_dir}' 下不存在以 '{text_num}' 开头的文件。")
    return paths


def find_files(root_dir, prefix_list, file=True):
    current_dirs = [root_dir]
    matched_files = []
    for level, prefix in enumerate(prefix_list):
        next_dirs = []
        for current_dir in current_dirs:
            try:
                items = os.listdir(current_dir)
            except OSError:
                continue
            for item in items:
                item_path = os.path.join(current_dir, item)
                if level == len(prefix_list) - 1:
                    if item.startswith(prefix) and os.path.isfile(item_path) and file and not item.startswith("~$"):
                        matched_files.append(item_path)
                    if item.startswith(prefix) and os.path.isdir(item_path) and not file:
                        matched_files.append(item_path)
                elif item.startswith(prefix) and os.path.isdir(item_path) and not item.startswith("~$"):
                    next_dirs.append(item_path)
        if level < len(prefix_list) - 1:
            current_dirs = next_dirs
    return matched_files


def read(path, sht_num_name=0, row=0, col_list=0):
    wb = None
    try:
        wb = app.books.open(path, update_links=False)
        visible_sheets = [sheet for sheet in wb.sheets if sheet.api.Visible == -1]
        if isinstance(sht_num_name, int):
            sheet = visible_sheets[sht_num_name]
        else:
            sheet = wb.sheets[sht_num_name]
        sheet.api.AutoFilterMode = False
        sheet.api.Columns("a:bz").EntireColumn.Hidden = False
        data = sheet.used_range.value
        if data is None:
            return pd.DataFrame()
        if not isinstance(data, list):
            data = [[data]]
        elif data and not isinstance(data[0], list):
            data = [[value] for value in data] if sheet.used_range.columns.count == 1 else [data]
        df = pd.DataFrame(data)
        if len(df) <= row:
            return pd.DataFrame()
        df.columns = df.iloc[row, :].astype(str).str.strip()
        df = df.iloc[row + 1:, :]
        if col_list != 0:
            missing_columns = [column for column in col_list if column not in df.columns]
            if missing_columns:
                raise Exception(f"文件 {path} 缺少列：{missing_columns}")
            df = df[col_list]
        return df
    finally:
        if wb is not None:
            wb.close()


def df_notnull(df, split_list=None, null_list=None):
    result = df.copy()
    if split_list:
        # TODO: 编码需要保留前导零时，不得使用 lstrip('0')。
        result[split_list] = (
            result[split_list]
            .fillna("")
            .astype(str)
            .replace(r"\.0+$", "", regex=True)
        )
    if null_list:
        result = result[
            ~result[null_list].fillna("").astype(str).applymap(lambda value: value in ["", "None"]).all(axis=1)
        ]
    return result


# 配置文件
root_dir = "1.原始数据"
save_dir = "2.运行结果"
config_dir = "1-1.配置文件"
business_file = os.path.join(os.getcwd(), root_dir, config_dir, "sap_business_config.ini")
business_section = "TODO_BUSINESS_SECTION"
business_config = configparser.ConfigParser()
business_config.read(business_file, encoding="utf-8-sig")

com_lists = business_config[business_section].get("com_lists")
fin_period = business_config[business_section].get("fin_period")
year = fin_period[:4]
last_month = (datetime.strptime(fin_period, "%Y%m") - relativedelta(months=1)).strftime("%Y%m")


# 数据读取
app = xw.App(visible=True, add_book=False)
try:
    # TODO: 按输入清单逐个读取文件/Sheet/必需字段。
    # source_path = get_path(root_dir=root_dir, text_num="01")[0]
    # df_0101 = read(source_path, sht_num_name="TODO_SHEET", col_list=["TODO_COLUMN"])
    pass
finally:
    app.kill()


# 数据处理
# TODO: 按已确认规则分段实现筛选、匹配、计算、核对和结果列排序。


# 结果输出
# TODO: 按输出清单更新目标工作簿的各 Sheet，明确覆盖/追加/删除当期重写/复制公式与格式行为。

