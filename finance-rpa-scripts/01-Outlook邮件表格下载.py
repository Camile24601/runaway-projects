#!/usr/bin/env python
# coding: utf-8

import configparser
import datetime
import html as html_lib
import os
import re
import subprocess
import time
from html.parser import HTMLParser

import win32com.client as win32
import xlwings as xw


# =============================================================================
# 1. 项目参数
# =============================================================================

try:
    project_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    project_dir = os.getcwd()

root_dir = os.path.join(project_dir, "1.原始数据")
business_file = os.path.join(root_dir, "sap_business_config.ini")
business_section = "FI_GL064"
output_path = os.path.join(root_dir, "01-邮件数据.xlsx")

main_table_key_columns = [
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

# =============================================================================
# 2. 公共函数
# =============================================================================

def normalize_text(value):
    """统一空格、换行和全角冒号，便于匹配 Outlook HTML 内容。"""
    text = "" if value is None else str(value)
    text = text.replace("\xa0", " ").replace("：", ":")
    return re.sub(r"\s+", "", text).strip()


def normalize_subject(subject):
    """移除邮件客户端反复叠加的回复、转发前缀。"""
    result = normalize_text(subject)
    prefix_pattern = re.compile(
        r"^(?:(?:RE|FW|FWD|答复|回复|转发)\s*:\s*)+",
        flags=re.IGNORECASE,
    )
    previous = None
    while result != previous:
        previous = result
        result = prefix_pattern.sub("", result)
    return result


def normalize_column_name(value):
    """清理列名首尾空格和换行，并统一大小写。"""
    text = "" if value is None else str(value)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[\r\n]+", "", text)
    return text.strip().casefold()


class OutlookTableParser(HTMLParser):
    """只使用 Python 标准库解析 Outlook 正文中的 HTML 表格。"""

    def __init__(self):
        super().__init__()
        self.tables = []
        self._table_depth = 0
        self._current_table = None
        self._current_row = None
        self._current_cell = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "table":
            self._table_depth += 1
            if self._table_depth == 1:
                self._current_table = []
        elif self._table_depth == 1 and tag == "tr":
            self._current_row = []
        elif self._table_depth == 1 and tag in ("td", "th"):
            self._current_cell = []
        elif self._table_depth == 1 and tag == "br" and self._current_cell is not None:
            self._current_cell.append(" ")

    def handle_data(self, data):
        if self._table_depth == 1 and self._current_cell is not None:
            self._current_cell.append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self._table_depth == 1 and tag in ("td", "th"):
            if self._current_row is not None:
                value = "".join(self._current_cell or [])
                value = re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()
                self._current_row.append(value)
            self._current_cell = None
        elif self._table_depth == 1 and tag == "tr":
            if self._current_table is not None and self._current_row:
                self._current_table.append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._table_depth > 0:
            if self._table_depth == 1 and self._current_table:
                self.tables.append(self._current_table)
                self._current_table = None
            self._table_depth -= 1


def iter_folders(folder):
    """递归遍历收件箱及其子文件夹。"""
    yield folder
    try:
        for index in range(1, folder.Folders.Count + 1):
            yield from iter_folders(folder.Folders.Item(index))
    except Exception as exc:
        print(f"⚠️ 无法读取子文件夹：{getattr(folder, 'Name', '')}，{exc}")


def extract_mail_tables(html_body):
    """提取全部实质性表格，并优先选择包含关键列名的主表。"""
    parser = OutlookTableParser()
    parser.feed(html_body or "")

    normalized_key_columns = {
        normalize_column_name(column)
        for column in main_table_key_columns
    }
    result = []
    for table_index, table in enumerate(parser.tables):
        non_empty_rows = [
            row for row in table
            if any(normalize_text(cell) for cell in row)
        ]
        if not non_empty_rows:
            continue

        max_columns = max(len(row) for row in non_empty_rows)
        # 过滤 Outlook 签名、分隔线等单格布局表；不检查具体表头内容。
        if len(non_empty_rows) < 2 or max_columns < 2:
            continue

        rectangular_table = [
            row + [""] * (max_columns - len(row))
            for row in non_empty_rows
        ]
        non_empty_cells = sum(
            1
            for row in rectangular_table
            for cell in row
            if normalize_text(cell)
        )

        matched_data_rows = -1
        for row_index, row in enumerate(rectangular_table):
            normalized_cells = {
                normalize_column_name(cell)
                for cell in row
                if normalize_column_name(cell)
            }
            if normalized_key_columns.issubset(normalized_cells):
                data_rows = sum(
                    1
                    for data_row in rectangular_table[row_index + 1:]
                    if any(normalize_text(cell) for cell in data_row)
                )
                matched_data_rows = max(matched_data_rows, data_rows)

        result.append({
            "table_index": table_index,
            "non_empty_cells": non_empty_cells,
            "max_columns": max_columns,
            "matched_data_rows": matched_data_rows,
            "table": rectangular_table,
        })

    # 其余表格继续沿用原排序：非空单元格最多优先，其次列数最多。
    fallback_order = sorted(
        result,
        key=lambda item: (item["non_empty_cells"], item["max_columns"]),
        reverse=True,
    )
    matched_tables = [
        item for item in fallback_order
        if item["matched_data_rows"] >= 0
    ]

    if matched_tables:
        # 多张表都包含关键列时，非空数据行最多的表作为主表；
        # 数据行数相同时保留原兜底排序。
        main_table = max(
            matched_tables,
            key=lambda item: item["matched_data_rows"],
        )
    elif fallback_order:
        main_table = fallback_order[0]
    else:
        return []

    ordered_tables = [main_table]
    ordered_tables.extend(
        item for item in fallback_order
        if item["table_index"] != main_table["table_index"]
    )
    return [item["table"] for item in ordered_tables]


def connect_outlook():
    """沿用公司既有自动发邮件脚本的 Outlook COM 连接方式。"""
    try:
        return win32.Dispatch("Outlook.Application")
    except Exception:
        subprocess.Popen("outlook.exe", shell=True)
        time.sleep(5)
        return win32.Dispatch("Outlook.Application")


def get_outlook_roots(namespace):
    """获取 Outlook 左侧当前已挂载的全部邮箱和数据文件根目录。"""
    roots = []
    for index in range(1, namespace.Folders.Count + 1):
        try:
            roots.append(namespace.Folders.Item(index))
        except Exception as exc:
            print(f"⚠️ 无法读取 Outlook 第 {index} 个根目录：{exc}")
    if not roots:
        raise RuntimeError("Outlook 当前没有可读取的邮箱或数据文件根目录。")
    return roots


def split_html_message_rounds(html_body):
    """按 Outlook 回复/转发分隔标记切分邮件轮次，顺序保持从新到旧。"""
    source = html_body or ""
    marker_patterns = [
        re.compile(
            r"<div\b[^>]*\bid\s*=\s*[\"']?divRplyFwdMsg\b",
            flags=re.IGNORECASE,
        ),
        re.compile(
            r"(?:发件人|From)(?:(?:&nbsp;)|\s|<[^>]*>){0,20}[:：]",
            flags=re.IGNORECASE,
        ),
    ]

    split_positions = {0}
    for pattern in marker_patterns:
        split_positions.update(match.start() for match in pattern.finditer(source))

    positions = sorted(split_positions)
    rounds = []
    for index, start in enumerate(positions):
        end = positions[index + 1] if index + 1 < len(positions) else len(source)
        fragment = source[start:end]
        if fragment.strip():
            rounds.append(fragment)
    return rounds or [source]


def parse_round_sent_timestamp(html_fragment):
    """尽量解析中英文历史邮件头中的发送时间。"""
    text = re.sub(r"<[^>]+>", " ", html_fragment or "")
    text = html_lib.unescape(text).replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()

    match = re.search(
        r"(?:发送时间|Sent)\s*[:：]\s*(.*?)"
        r"(?=(?:收件人|To|抄送|Cc|主题|Subject)\s*[:：]|$)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    date_text = match.group(1).strip()
    date_text = re.sub(r"星期[一二三四五六日天]", "", date_text).strip()
    date_formats = [
        "%Y年%m月%d日 %H:%M",
        "%Y年%m月%d日 %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d %H:%M",
        "%A, %B %d, %Y %I:%M %p",
        "%B %d, %Y %I:%M %p",
    ]
    for date_format in date_formats:
        try:
            return datetime.datetime.strptime(date_text, date_format).timestamp()
        except ValueError:
            continue
    return None


def extract_latest_round_table(html_body, received_time=None):
    """选择时间最新且包含实质性表格的邮件轮次，并只返回一个主表。"""
    round_candidates = []
    for round_index, html_fragment in enumerate(split_html_message_rounds(html_body)):
        tables = extract_mail_tables(html_fragment)
        if not tables:
            continue

        sent_timestamp = parse_round_sent_timestamp(html_fragment)
        if round_index == 0 and received_time is not None:
            try:
                sent_timestamp = received_time.timestamp()
            except Exception:
                pass

        round_candidates.append({
            "round_index": round_index,
            "sent_timestamp": sent_timestamp,
            "table": tables[0],
        })

    if not round_candidates:
        return None

    # 能比较历史发送时间时取时间最新者；任何轮次时间无法解析时，
    # 按 Outlook 正文从上到下（新到旧）的顺序取最靠前者。
    if all(item["sent_timestamp"] is not None for item in round_candidates):
        return max(
            round_candidates,
            key=lambda item: item["sent_timestamp"],
        )["table"]
    return round_candidates[0]["table"]


def find_latest_mail_table(outlook_roots, target_subject):
    """查找最新的匹配邮件；主题相同但无目标表格时继续查找下一封。"""
    target_normalized = normalize_subject(target_subject)
    matches = []

    for root in outlook_roots:
        for folder in iter_folders(root):
            try:
                items = folder.Items
                items.Sort("[ReceivedTime]", True)
            except Exception as exc:
                print(f"⚠️ 跳过无法读取的文件夹：{getattr(folder, 'Name', '')}，{exc}")
                continue

            for item in items:
                try:
                    if getattr(item, "Class", None) != 43:
                        continue
                    subject = getattr(item, "Subject", "")
                    if normalize_subject(subject) != target_normalized:
                        continue
                    received_time = getattr(item, "ReceivedTime", None)
                    matches.append((received_time, item))
                except Exception:
                    continue

    if not matches:
        raise FileNotFoundError(f"Outlook 中未找到主题为“{target_subject}”的邮件。")

    matches.sort(
        key=lambda pair: pair[0].timestamp() if pair[0] is not None else 0,
        reverse=True,
    )

    for received_time, item in matches:
        table = extract_latest_round_table(
            getattr(item, "HTMLBody", ""),
            received_time=received_time,
        )
        if table:
            return item, table
        print(
            "⚠️ 已跳过无目标表格的同主题邮件："
            f"{getattr(item, 'Subject', '')} / {received_time}"
        )

    raise ValueError(f"找到同主题邮件，但正文中未识别到实质性表格：{target_subject}")


def save_to_excel(table, save_path):
    """通过 xlwings 生成公司电脑可直接使用的 Excel 文件。"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if os.path.exists(save_path):
        try:
            os.remove(save_path)
        except PermissionError as exc:
            raise PermissionError(
                f"无法覆盖 {save_path}，请先关闭已打开的同名 Excel 文件。"
            ) from exc

    app = None
    wb = None
    try:
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        wb = app.books.add()
        sheet = wb.sheets[0]
        sheet.name = "sheet1"

        last_row = len(table)
        last_col = max(len(row) for row in table)
        output_range = sheet.range((1, 1), (last_row, last_col))
        output_range.value = table

        first_row = sheet.range((1, 1), (1, last_col))
        first_row.api.Font.Bold = True
        first_row.color = (189, 215, 238)
        first_row.api.HorizontalAlignment = -4108
        first_row.api.VerticalAlignment = -4108

        output_range.api.Borders.LineStyle = 1
        output_range.api.VerticalAlignment = -4108
        output_range.columns.autofit()
        for column_index in range(1, last_col + 1):
            column = sheet.range((1, column_index), (last_row, column_index))
            if column.column_width > 32:
                column.column_width = 32
                column.api.WrapText = True

        sheet.range("A2").select()
        app.api.ActiveWindow.FreezePanes = True
        wb.save(save_path)
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


# =============================================================================
# 3. 读取期间并生成目标主题
# =============================================================================

if not os.path.exists(business_file):
    raise FileNotFoundError(f"业务配置文件不存在：{business_file}")

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

target_subject = f"1500国锐项目费用调整-{year % 100}年{month}月"
print(f"目标邮件主题：{target_subject}")


# =============================================================================
# 4. 连接 Outlook、提取表格并保存 Excel
# =============================================================================

outlook = connect_outlook()
namespace = outlook.GetNamespace("MAPI")
outlook_roots = get_outlook_roots(namespace)
print(f"Outlook 已挂载根目录数：{len(outlook_roots)}")

mail, mail_table = find_latest_mail_table(outlook_roots, target_subject)
save_to_excel(mail_table, output_path)

print(f"✅ 已提取邮件：{mail.Subject}")
print(f"邮件时间：{mail.ReceivedTime}")
print("提取表格数：1")
print(f"主表行列数：{len(mail_table)} 行 × {len(mail_table[0])} 列")
print(f"Excel 已保存：{output_path}")
