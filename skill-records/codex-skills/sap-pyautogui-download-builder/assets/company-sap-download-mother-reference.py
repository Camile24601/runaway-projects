#!/usr/bin/env python
# coding: utf-8

"""SAP 下载保真母版：包含 AP051 人工修正后的下载流程。

该母版来自用户修改后的公司脚本。生成具体项目脚本时必须替换
`TODO_APPROVED_PROJECT_PATH`、`TODO_SAP_SYSTEM` 和 `TODO_BUSINESS_SECTION`。
"""

# In[1]:


# get_ipython().run_line_magic('cd', r'TODO_APPROVED_PROJECT_PATH')


# In[2]:


# 请使用 $sap-pyautogui-download-builder，基于公司原脚本新建下载程序。
# 公共函数、SAP 登录及退出流程原样保留，不做结构性重构。

# 输出脚本路径：桌面/02-SAP数据下载-AP051.py
# 已有文件策略：仅补下载缺失文件

# ## 下载任务清单
# | 序号 | TCode | 输出编号 | Excel 描述 | 最终文件名 |
# | --- | --- | --- | --- | --- |
# | 1 | F.19 | 01 | 收货/发货清算 | `01-F.19-收货/发货清算.xlsx` |
# | 2 | ZMM020 | 02 | 采购对账单 | `02-ZMM020-采购对账单.xlsx` |
# | 3 | FBL1N | 03 | 供应商特别总账业务 | `03-FBL1N-供应商特别总账业务.xlsx` |
# | 4 | ZMM020 | 04 | 采购对账单 | `04-ZMM020-采购对账单.xlsx` |

# ### 任务 1：F.19
# - 上游 Excel 依赖：无
# - 参数来源：公司代码取 `com_item`，年度取 `year`，期间取 `period`
# - SAP 操作步骤：
#   1. 输入总账科目 `2202020100`
#   2. tab*3
#   3. 输入公司代码 `com_item`
#   4. down*2
#   5. tab*3
#   6. 输入程序运行当天yyyy-mm-dd
#   7. load_complete()加载
#   8. 判断若出现‘更改布局’才进行后续操作
#   9. 点击‘更改布局’界面的最后一个按钮向左偏移的250像素的坐标处
#   10. 点击两次 shift+tab
#   11. 点击enter
#   12. 判断若出现‘扫描字段列表’字样才进行后续操作
#   13. 复制'过账日期'
#   14. 粘贴 ctrl+v
#   15. enter
#   16. ctrl+f3
#   17. enter
# - 查询执行：`enter`
# - 导出方式：原 `save_F19()`

# ### 任务 2：FBL1N
# - 上游 Excel 依赖：无
# - 参数来源：公司代码取 `com_item`，日期取 `s_date` 和 `e_date`
# - SAP 操作步骤：
#   1. `down` 1 次
#   2. 输入公司代码'com_item'
#   3. enter
#   4. down*2
#   5. tab*3
#   6. ctrl+a
#   7. 输入程序当天运行日期yyyy-mm-dd
#   8. enter
#   9. down*4
#   10. space
#   11.down
#   12. space
# - 查询执行：`F8`
# - 导出方式：原 `save_excel()`

# ### 任务 3：ZMM020
# - 上游 Excel 依赖：有
# - 来源文件：`sap_path` 下前缀 `01` 的 Excel
# - 上游文件处理：文件列名位于第三行开始，读取过账日期为上年的期初到上月的期末的数据，提取去重后的采购凭证
# - 参数来源：公司代码取 `com_item`，日期取 `s_date` 和 `e_date`
# - SAP 操作步骤：
#   1. ctrl+a,然后输入公司代码
#   2. enter
#   3. down*6
#   4. ctrl+a
#   5. 输入fin_period对应期间的上一年的期初日期，例如fin_period=202501,则输入2024-01-01
#   6. tab
#   7. 输入ctrl+a, 然后输入fin_period对应期间的上月的期末日期，例如fin_period=202501,则输入2024-12-31
#   8. tab*4
#   9. enter
#   10.mul_choice(输入上游excel文件的采购凭证列)
#   11. down*6
#   12. f4
#   13. down*2
#   14. enter
# - 查询执行：`F8`
# - 导出方式：原 `save_excel()`

# ### 任务 4：ZMM020
# - 上游 Excel 依赖：有
# - 来源文件：`sap_path` 下前缀 `03` 的 Excel
# - 上游文件处理：文件列名位于第一行开始，读取文本列，从文本列提取52开头的数字为采购凭证
# - 参数来源：公司代码取 `com_item`，日期取 `s_date` 和 `e_date`
# - SAP 操作步骤：
#   1. ctrl+a,然后输入公司代码
#   2. enter
#   3. down*6
#   4. ctrl+a
#   5. 输入fin_period对应期间的上一年的期初日期，例如fin_period=202501,则输入2024-01-01
#   6. tab
#   7. 输入ctrl+a, 然后输入fin_period对应期间的上月的期末日期，例如fin_period=202501,则输入2024-12-31
#   8. tab*4
#   9. enter
#   10.mul_choice(输入上游excel文件的采购凭证列)
#   11. down*6
#   12. f4
#   13. down*2
#   14. enter
# - 查询执行：`F8`
# - 导出方式：原 `save_excel()`

# ## 任务间依赖
# - 必须按顺序下载：是
# - 第一张ZMM020 读取 F.19 生成的 `01-F.19-收货/发货清算.xlsx`
# - 第二张ZMM020 读取 FBL1N 生成的 `03-FBL1N-供应商特别总账业务.xlsx`
# - 如果上游文件不存在：终止并报错

# ## 交付要求
# - 生成完整 Python 文件
# - 标注业务修改段
# - 语法检查
# - 不执行 SAP


# In[3]:


ticode_dict={
    'F.19': ['收货凭证',]
    ,'FBL1N': ['入账订单明细',]
    ,'ZMM020': ['采购对账单','采购对账单',]
}
print_ticode='\n'.join([f'{key}-{ticode_dict[key]}' for key in ticode_dict])
print(f'SAP下载TICODE:\n{print_ticode}')


# In[4]:


import win32com.client,win32gui,win32con
import pandas as pd
import numpy as np
import os,sys,re,shutil,psutil,time,datetime,traceback,ctypes,subprocess,configparser
import fitz,calendar
import importlib.util
import xlwings as xw
import tkinter as tk
from tkinter import messagebox
import pyperclip
import psutil
import pyautogui as ag
from dateutil.relativedelta import relativedelta

ag.PAUSE = 0.3
ag.FAILSAFE = True
pd.set_option("display.float_format", lambda x: "%.2f" % x)#不显示科学计数
pd.options.mode.chained_assignment = None#忽略警告


# In[5]:


def get_path(root_dir='1.原始数据', text_num='01'):
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"目录 '{root_dir}' 不存在。")
    paths = [
        os.path.join(root_dir, f)
        for f in os.listdir(root_dir)
        if not f.startswith("~$ ") and f.startswith(text_num)
    ]
    if not paths:
        raise ValueError(f"'{root_dir}' 下不存在以 '{text_num}' 开头的文件。")
    
    return paths

def read(path, sht_num_name=0, row=0, col_list=0):
    wb = None
    try:
        # 尝试打开 Excel
        try:
            wb = app.books.open(path, update_links=False)
        except Exception as e:
            raise Exception(f"打开 Excel 文件失败：{path}\n错误信息：{e}")

        # 获取可见工作表
        shts = [s for s in wb.sheets if s.api.Visible == -1]
        if isinstance(sht_num_name, int):
            sheet = shts[sht_num_name]
        else:
            if "*" in sht_num_name:
                sheet = [sht for sht in shts if sht_num_name[1:] in sht.name][0]
            else:
                sheet = wb.sheets[sht_num_name]

        # 取消筛选和隐藏列
        sheet.api.AutoFilterMode = False
        sheet.api.Columns("a:bz").EntireColumn.Hidden = False

        # 获取数据
        data = sheet.used_range.value

        # 处理空表或单行单列情况
        if data is None:
            return pd.DataFrame()
        elif not isinstance(data, list):
            data = [[data]]
        elif len(data) > 0 and not isinstance(data[0], list):
            if sheet.used_range.columns.count == 1:
                data = [[x] for x in data]
            else:
                data = [data]

        df = pd.DataFrame(data)

        # 检查是否有足够的行来设置列名
        if len(df) <= row:
            return pd.DataFrame()

        # 设置列名
        df.columns = df.iloc[row, :].astype(str)

        # 检查是否有数据行
        if len(df) <= row + 1:
            empty_df = pd.DataFrame(columns=df.columns.str.strip())
            if col_list != 0:
                df_error_cols = [i for i in col_list if i not in empty_df.columns]
                if df_error_cols:
                    raise Exception(f"文件 {path} 缺少列：{df_error_cols}")
                empty_df = empty_df[col_list]
            return empty_df

        # 正常情况，取数据行
        df = df.iloc[row + 1:, :]
        df.columns = df.columns.str.strip()

        # 列筛选
        if col_list != 0:
            df_error_cols = [i for i in col_list if i not in df.columns]
            if df_error_cols:
                raise Exception(f"文件 {path} 缺少列：{df_error_cols}")
            df = df[col_list]

        return df

    finally:
        if wb is not None:
            try:
                wb.close()
            except:
                pass

# 常用数据清理,两者均可只运行其一
def df_notnull(df, split_list=None,null_list=None):
    if split_list:
        df[split_list] = (
            df[split_list]
            .fillna("")
            .astype(str)
            .replace(r'\.0+$', '', regex=True)
            .apply(lambda col: col.str.lstrip('0'))
        )
        df1=df.copy()
    if null_list:
        df1= df[
            ~df[null_list].fillna("").astype(str).applymap(lambda x: x in ["", "None"]).all(axis=1)
        ]
    return df1


# In[6]:


# 已知期间-得到该期间的期初期末
def get_month_start_end(period_str: str):
    digits = "".join(filter(str.isdigit, period_str))
    # 不合法时补零
    if len(digits) == 6:
        pass
    elif len(digits) == 5:
        digits = digits[:4] + digits[4:].zfill(2)
    else:
        raise ValueError(f"日期格式错误，应为'YYYYMM'，收到{period_str}")

    year = int(digits[:4])
    month = int(digits[4:6])

    # 月份
    if not(1 <= month <= 12):
        raise ValueError(f"月份错误，输入的月份为{month}")

    # 月初
    month_start = datetime.date(year, month, 1)
    # 月末
    last_day = calendar.monthrange(year, month)[1]
    month_end = datetime.date(year, month, last_day)

    return month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d")


# # 自定义函数

# ## 窗口句柄查找

# In[7]:


def find_hwnd_all(name):#全词匹配
    hwnd_title = {}
    def get_all_hwnd(hwnd, mouse):
        if (win32gui.IsWindow(hwnd)
                and win32gui.IsWindowEnabled(hwnd)
                and win32gui.IsWindowVisible(hwnd)):
            hwnd_title[hwnd] = win32gui.GetWindowText(hwnd)

    win32gui.EnumWindows(get_all_hwnd, 0)
    for hwnd, title in hwnd_title.items():
        if name == title:
            return hwnd
    return 0

def find_hwnd_blur(name):#模糊匹配
    hwnd_title = {}
    def get_all_hwnd(hwnd, mouse):
        if (win32gui.IsWindow(hwnd)
                and win32gui.IsWindowEnabled(hwnd)
                and win32gui.IsWindowVisible(hwnd)):
            hwnd_title[hwnd] = win32gui.GetWindowText(hwnd)

    win32gui.EnumWindows(get_all_hwnd, 0)
    for hwnd, title in hwnd_title.items():
        if name in title:
            return hwnd
    return 0


# ## 多人登陆

# In[8]:


# 点击多次登录窗口的勾选框
def click_multi_logon_checkbox(offset_x=-250):
    hwnd_parent = find_hwnd_blur('更改布局')
    """
    找到最后一个 Button，向左偏移 offset_x 像素（默认 -100），并点击该位置。
    """
    buttons = []
    def enum_child_proc(hwnd, _):
        try:
            if win32gui.GetClassName(hwnd) == "Button":
                buttons.append(hwnd)
        except:
            pass
    win32gui.EnumChildWindows(hwnd_parent, enum_child_proc, None)

    if not buttons:
        print("❌ 未找到任何 Button 控件")
        raise Exception("❌ 未找到任何 Button 控件")

    last_btn = buttons[-1]
    text = win32gui.GetWindowText(last_btn)
    rect = win32gui.GetWindowRect(last_btn)
    x_btn, y_btn = rect[0], rect[1]  # 左上角坐标（屏幕坐标）

    # 计算偏移后的位置：向左 100px，Y 保持在按钮垂直中心
    x_click = x_btn + offset_x
    y_click = y_btn + (rect[3] - rect[1]) // 2  # 按钮高度的一半，居中点击

    # 直接点击该位置
    ag.click(x_click, y_click)


# In[9]:


# 多人登录选中右下角 "√"
def click_multi_logon(offset_x=-100):
    hwnd_parent=find_hwnd_blur('多次登录')
    """
    找到最后一个 Button，向左偏移 offset_x 像素（默认 -100），并点击该位置。
    """
    buttons = []
    def enum_child_proc(hwnd, _):
        try:
            if win32gui.GetClassName(hwnd) == "Button":
                buttons.append(hwnd)
        except:
            pass
    win32gui.EnumChildWindows(hwnd_parent, enum_child_proc, None)

    if not buttons:
        print("❌ 未找到任何 Button 控件")
        raise Exception("❌ 未找到任何 Button 控件")

    last_btn = buttons[-1]
    text = win32gui.GetWindowText(last_btn)
    rect = win32gui.GetWindowRect(last_btn)
    x_btn, y_btn = rect[0], rect[1]  # 左上角坐标（屏幕坐标）

    # 计算偏移后的位置：向左 100px，Y 保持在按钮垂直中心（更合理）
    x_click = x_btn + offset_x
    y_click = y_btn + (rect[3] - rect[1]) // 2  # 按钮高度的一半，居中点击

    # 移动鼠标（可选，用于可视化）
    ag.click(x_click,y_click)
    ag.press('tab',2,0.3)
    ag.press('up')
    ag.press('enter')


# ## 多项选择

# In[10]:


def mul_choice(company_codes):    
    for _ in range(15):
        ag.press('f24')
        time.sleep(0.3)
        if find_hwnd_blur('多种选择')==0:
            continue
        else:
            time.sleep(0.5)
            break
    ag.hotkey('shift','f4')
    # pd.Series(com_lists).to_clipboard(excel = True,index=False,header=False)
    company_codes.to_clipboard(index = False, header = False)
    time.sleep(0.3)
    ag.hotkey('shift','f12')
    ag.press('f8',interval=0.5)
    for _ in range(15):
        ag.press('f24')
        time.sleep(0.3)
        if find_hwnd_blur('多种选择')!=0:
            ag.press('f8',interval=0.5)
            continue
        else:
            time.sleep(0.3)
            break


# ## load_complete判断加载

# In[11]:


user32 = ctypes.windll.user32
def get_menu_string(menu, index):
    buf_size = 256
    buf = ctypes.create_unicode_buffer(buf_size)
    user32.GetMenuStringW(menu, index, buf, buf_size, win32con.MF_BYPOSITION)
    return buf.value


# In[12]:


def wait_window_blur(title, exists=True, max_times=30, interval=0.5):
    for _ in range(max_times):
        ag.press('f24')
        time.sleep(interval)
        found = find_hwnd_blur(title) != 0
        if found == exists:
            return True
    return False


def choose_layout(layout_text):
    layout_text = str(layout_text or "").strip()
    if not layout_text:
        return False

    ag.click(182, 350)
    time.sleep(0.3)
    ag.hotkey('shift', 'tab')
    ag.hotkey('shift', 'tab')
    ag.press('enter')
    if not wait_window_blur('选择布局', exists=True, max_times=20):
        raise Exception('未出现“选择布局”，无法切换布局')

    ag.rightClick()
    time.sleep(0.3)
    ag.press('up', 4, 0.2)
    ag.press('enter')
    if not wait_window_blur('查找', exists=True, max_times=20):
        raise Exception('未出现“查找”，无法输入布局')

    ag.press('f4')
    ag.press('enter')
    ag.hotkey('shift', 'tab')
    pyperclip.copy(layout_text)
    time.sleep(0.2)
    ag.hotkey('ctrl', 'v')
    ag.press('enter')
    ag.press('f12')
    if not wait_window_blur('选择布局', exists=True, max_times=20):
        raise Exception('查找布局后未返回“选择布局”界面')
    ag.press('enter')
    if not wait_window_blur('选择布局', exists=False, max_times=20):
        raise Exception('确认布局后“选择布局”界面未关闭')

    # 二次打开确认布局界面可正常进入，再 F12 退出，不再重复选择。
    ag.click(182, 350)
    time.sleep(0.3)
    ag.hotkey('shift', 'tab')
    ag.hotkey('shift', 'tab')
    ag.press('enter')
    if not wait_window_blur('选择布局', exists=True, max_times=20):
        raise Exception('二次确认时未出现“选择布局”')
    ag.press('f12')
    wait_window_blur('选择布局', exists=False, max_times=10)
    return True


def load_complete(max_duration=1200,pre_name='F8',time_sleep=1.3):
    def _get_menu_items():
        hwnd = win32gui.GetForegroundWindow()
        menu_hwnd = win32gui.GetMenu(hwnd)
        if not menu_hwnd:
            return []
        count = win32gui.GetMenuItemCount(menu_hwnd)
        items = []
        for i in range(count):
            try:
                text = get_menu_string(menu_hwnd, i)
                items.append(text)
            except Exception:
                items.append("")
        return items
    # Step 1: 获取执行前菜单
    menu_before = _get_menu_items()
    ag.press(pre_name)
    if not menu_before:
        menu_before = _get_menu_items()
    for i in range(max_duration):
        time.sleep(0.5)
        ag.press('f24')
        menu_after = _get_menu_items()
        if menu_before != menu_after:
            time.sleep(time_sleep)
            break
        else:
            if i==max_duration-1:
                raise Exception(print(f"超时！{max_duration} 秒内未检测到菜单变化，判定加载失败。"))
            continue


# ## 保存函数

# ### 通用

# In[13]:



def save_foreground_window():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        return hwnd
    return None


def activate_window(hwnd):
    if not hwnd or not win32gui.IsWindow(hwnd):
        return False
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    try:
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception as e:
        print(f"⚠️ 激活失败（可能受系统限制）: {e}")
        return False


def get_excel_pids():
    return {
        proc.info['pid']
        for proc in psutil.process_iter(['pid', 'name'])
        if proc.info['name'] and proc.info['name'].lower() == 'excel.exe'
    }


def save_excel(save_path):
    # 保存数据，并只关闭本次导出新打开的 Excel 进程。
    window_A = save_foreground_window()
    for i in range(0,3):
        ag.press('f24')
        w, h = ag.size()
        ag.rightClick(w // 4-i*3, h // 2-i*3)
        time.sleep(0.3)
        ag.press('up')
        time.sleep(0.3)
        ag.press('enter')
        time.sleep(0.3)
        if find_hwnd_blur('选择电子表格')==0:
            time.sleep(3)
            continue
        else:
            ag.press('enter')
            break
    for _ in range(500):
        ag.press('f24')
        time.sleep(0.7)
        if find_hwnd_blur('另存为')==0:
            continue
        else:
            break
    time.sleep(1.2)
    ag.press('tab')
    ag.hotkey('shift','tab')
    try:
        os.remove(save_path)
    except Exception:
        pass
    pyperclip.copy(save_path)
    time.sleep(0.3)
    ag.hotkey('ctrl','v')
    before_pids_s = get_excel_pids()
    ag.hotkey('alt','s')
    for _ in range(30):
        ag.press('f24')
        time.sleep(0.5)
        before_pids_e = get_excel_pids()
        if find_hwnd_blur('GUI 安全性')==0 and before_pids_s == before_pids_e:
            continue
        else:
            time.sleep(0.7)
            break
    if find_hwnd_blur('GUI 安全性')!=0:
        ag.hotkey('alt','a')
    for _ in range(30):
        ag.press('f24')
        time.sleep(0.5)
        before_pids_e = get_excel_pids()
        if before_pids_s == before_pids_e:
            if find_hwnd_blur('GUI 安全性')!=0:
                ag.hotkey('alt','d')
                time.sleep(0.6)
                ag.press('enter')
            continue
        else:
            for pid in before_pids_e - before_pids_s:
                try:
                    psutil.Process(pid).terminate()
                except Exception:
                    pass
            time.sleep(0.7)
            break
    activate_window(window_A)
    time.sleep(0.8)
    ag.press('f3')


# In[14]:


def save_f19(save_path):
    name_part, ext_part = os.path.splitext(dir_name)
    # 在文件名部分的版本号后添加空格，并更改扩展名为.xls
    new_name = name_part.replace('-F.19', '-F.19 ') + '.xls'
    
    # alt + l  f + s
    ag.hotkey('alt','l')
    ag.press('s')
    ag.press('f')
    for _ in range(335):
        time.sleep(0.7)
        if find_hwnd_blur('列表保存') != 0:
            break
        else:
            continue
    time.sleep(1)
    ag.press('down')
    ag.press('enter')

    for _ in range(335):
        time.sleep(0.7)
        if find_hwnd_blur('将列表保存在') == 0:
            break
        else:
            continue
    time.sleep(1)

    # 路径
    ag.hotkey('shift','tab')
    ag.hotkey('ctrl','a')
    ag.press('delete')
    pyperclip.copy(save_dir)
    time.sleep(0.7)
    ag.hotkey('ctrl', 'v')

    # 文件名
    ag.press('tab')
    ag.hotkey('ctrl','a')
    ag.press('delete')
    pyperclip.copy(new_name)
    time.sleep(0.7)
    ag.hotkey('ctrl', 'v')

    ag.press('enter')
    for _ in range(207):
        if find_hwnd_blur("GUI 安全性") != 0:
            ag.hotkey('alt', 'a')
            break
        time.sleep(1)
    else:
        print("错误：保存对话框未弹出！")

    ag.hotkey('shift', 'f3')
    ag.press('f3')
    ag.press('f3')


# # 用户信息

# ## 参数读取

# In[15]:


# SAP登录配置文件路径
login_file = r'd:/sap_download_config.ini'
login_section = 'FI_FB'
login_config = configparser.ConfigParser()
login_config.read(login_file, encoding='utf-8-sig')

# 业务配置文件路径
root_dir = "1.原始数据"
business_path = os.path.join(os.getcwd(), root_dir)
business_file = os.path.join(business_path, 'sap_business_config.ini')
business_section = 'TODO_BUSINESS_SECTION'
business_config = configparser.ConfigParser()
business_config.read(business_file, encoding='utf-8-sig')


# 期间、公司
username = login_config[login_section].get('SAP账号')
password = login_config[login_section].get('密码')

com_lists = business_config[business_section].get('com_lists')
fin_period = business_config[business_section].get('fin_period')


# # 登陆开始

# In[16]:


sap_app = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe" #saplogon程序本地完整路径
subprocess.Popen(sap_app)
time.sleep(1)
flt=0
while flt==0:
    try:
        hwnd = win32gui.FindWindow(None,"SAP Logon 740")
        flt=win32gui.FindWindowEx(hwnd,None,"Edit", None)
    except:
        time.sleep(0.5)

win32gui.SendMessage(flt,win32con.WM_SETTEXT,None,"TODO_SAP_SYSTEM")#系统名
win32gui.SendMessage(flt,win32con.WM_KEYDOWN,win32con.VK_RIGHT,0)
win32gui.SendMessage(flt,win32con.WM_KEYUP,win32con.VK_RIGHT,0)
time.sleep(0.1)

dlg = win32gui.FindWindowEx(hwnd,None,"Button", None) #登陆（0）
win32gui.SendMessage(dlg,win32con.WM_LBUTTONDOWN,0)
win32gui.SendMessage(dlg,win32con.WM_LBUTTONUP,0)

for _ in range(10):
    ag.press('f24')
    time.sleep(0.5)
    if win32gui.FindWindow(None,'SAP')!=0:
        time.sleep(0.3)
        break
    else:
        continue
        
hwnd = win32gui.FindWindow(None,'SAP') # 第二个参数为Excel窗口标题    
win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)#最大化
time.sleep(1)
pyperclip.copy(username)
time.sleep(0.3)
ag.hotkey('ctrl','v')
ag.press('tab')# 单击tab键

pyperclip.copy(password)
time.sleep(0.3)
ag.hotkey('ctrl','v')

ag.press('enter')#登陆
time.sleep(1)
if find_hwnd_blur('多次登录')!=0:
    click_multi_logon()
        #不终止其他人登陆


# # SAP数据加载

# ## 参数输入

# In[17]:


sap_path = os.path.join(os.getcwd(), root_dir)
os.makedirs(sap_path, exist_ok=True)

# 自定义编号映射
ticode_number_map = {
    'F.19': ['01'],
    'FBL1N': ['03'],
    'ZMM020': ['02', '05'],
}

ticode_dict={
    'F.19': ['收货凭证',]
    ,'FBL1N': ['入账订单明细',]
    ,'ZMM020': ['采购对账单','采购对账单',]
}


print_ticode='\n'.join([f'{key}-{ticode_dict[key]}' for key in ticode_dict])
print(f'SAP下载TICODE:\n{print_ticode}')

# 布局选择配置：优先按 item 精确匹配，如 ZMM020_1；找不到再按 TCode 匹配。
# F.19/FAGLL03H 等已有特殊布局流程的 TCode 默认不走 choose_layout。
LAYOUT_BY_ITEM = {
    # "ZMM020_1": "/布局",
}
LAYOUT_BY_TCODE = {
    # "ZMM020": "/CO006-1",
}
print_layout = {"按条目": LAYOUT_BY_ITEM, "按TCode": LAYOUT_BY_TCODE}
print(f'SAP布局配置:\n{print_layout}')


def get_layout_text(item, tcode):
    if tcode in {'F.19', 'FAGLL03H'}:
        return ""
    value = LAYOUT_BY_ITEM.get(item, LAYOUT_BY_TCODE.get(tcode, ""))
    return value() if callable(value) else value


# --- 构造每个 tcode 对应的文件名前缀 ---
expected_prefixes = {}
for tcode, desc_list in ticode_dict.items():
    number_list = ticode_number_map[tcode]
    # 遍历描述和编号的列表，按索引配对
    for i, (desc, number) in enumerate(zip(desc_list, number_list)):
        prefix = f"{number}-"
        expected_prefixes.setdefault(tcode, []).append(prefix)


# In[18]:


# 获取当前目录下的文件列表
dir_files = os.listdir(sap_path)
missing_tcodes = []

# --- 修改开始 ---
for tcode, prefix_list in expected_prefixes.items():
    # 判断这个 tcode 是否只有一个文件
    is_single_file = len(prefix_list) == 1
    
    for idx, prefix in enumerate(prefix_list, 1):
        prefix_clean = prefix.strip()
        found = any(fname.replace(' ', '').startswith(prefix_clean.replace(' ', '')) for fname in dir_files)
        
        if not found:
            if is_single_file:
                # 如果只有一个文件，直接添加 tcode，不加后缀
                missing_tcodes.append(tcode)
            else:
                # 如果有多个文件，添加 tcode_序号
                missing_tcodes.append(f"{tcode}_{idx}")
# --- 修改结束 ---

# 如果有缺失的 tcode，只重下载缺失的那些 tcode
if missing_tcodes:
    not_contained = missing_tcodes
else:
    # 如果没有缺失的 tcode，说明所有 expected_prefixes 中的文件都存在
    # 则删除所有这些已存在的前缀对应的文件，并重新下载全部
    for fname in list(dir_files):
        # 遍历所有已知的期望前缀
        for tcode, prefix_list in expected_prefixes.items():
            for prefix in prefix_list:
                prefix_clean = prefix.strip()
                # 检查文件是否以任何一个期望的前缀开头
                if fname.replace(' ', '').startswith(prefix_clean.replace(' ', '')):
                    fpath = os.path.join(sap_path, fname)
                    if os.path.exists(fpath):
                        try:
                            os.remove(fpath)
                        except OSError as e:
                            print(f"❌警告: 删除 {fpath} 失败: {e}")
                    break 
            else:
                continue
            break 

    print("SAP导出数据已全部存在，全部替换重新下载")
    # 全部重新下载：使用所有 tcode
    not_contained = []
    for tcode, prefix_list in expected_prefixes.items():
        is_single_file = len(prefix_list) == 1
        for idx in range(1, len(prefix_list) + 1):
            if is_single_file:
                not_contained.append(tcode)
            else:
                not_contained.append(f"{tcode}_{idx}")


# ## 导出函数

# In[19]:


def load_F19():
    ag.hotkey('ctrl','a')
    ag.write('2202020100') # 总帐科目
    ag.press('tab', 3, 0.2)
    ag.hotkey('ctrl','a')
    ag.write(com_item) # 公司代码
    ag.press('enter')   
    ag.press('down', 2, 0.2)
    ag.press('tab', 3, 0.2)
    ag.hotkey('ctrl','a')
    ag.write(today) # 当天
    load_complete()
    ag.hotkey('ctrl','f8')
    for _ in range(20):
        ag.press('f24')
        time.sleep(0.5)
        if find_hwnd_blur('更改布局')==0:
            continue
        else:
            time.sleep(0.5)
            break
    click_multi_logon_checkbox()
    ag.hotkey('shift','tab')
    ag.hotkey('shift','tab')
    ag.press('enter')
    for _ in range(20):
        ag.press('f24')
        time.sleep(0.5)
        if find_hwnd_blur('扫描字段列表')==0:
            continue
        else:
            time.sleep(0.5)
            break
    time.sleep(0.5)
    pyperclip.copy('过账日期')
    time.sleep(0.3)
    ag.hotkey('ctrl', 'v')
    ag.press('enter')
    time.sleep(0.5)
    ag.hotkey('ctrl', 'f3')
    ag.press('enter')


def load_FBL1N():
    ag.press('down')
    ag.hotkey('ctrl','a')
    ag.write(com_item) # 公司代码
    ag.press('enter')
    ag.press('down', 2, 0.2)
    ag.press('tab', 3, 0.2)
    ag.hotkey('ctrl','a')
    ag.write(today) # 当天
    ag.press('enter')
    ag.press('down', 4, 0.3)
    ag.press('space')
    ag.press('down')
    ag.press('space')


def load_ZMM020_1():
    ag.hotkey('ctrl','a')
    ag.write(com_item) # 公司代码
    ag.press('enter')
    ag.press('down', 6, 0.2)
    ag.hotkey('ctrl','a')
    ag.write(l_month_start) # 上年期初
    ag.press('tab')
    ag.hotkey('ctrl','a')
    ag.write(l_date) # 上月期末
    ag.press('tab', 4, 0.2)
    ag.press('enter')
    mul_choice(df_01['采购凭证'])
    ag.press('down', 6, 0.2)
    ag.press('f4')
    ag.press('down', 2, 0.2)
    ag.press('enter')
    


def load_ZMM020_2():
    ag.hotkey('ctrl','a')
    ag.write(com_item) # 公司代码
    ag.press('enter')
    ag.press('down', 6, 0.3)
    ag.hotkey('ctrl','a')
    ag.write(l_month_start) # 上年期初
    ag.press('tab')
    ag.hotkey('ctrl','a')
    ag.write(l_date) # 上月期末
    ag.press('tab', 4, 0.3)
    ag.press('enter')
    mul_choice(df_02['采购凭证'])
    ag.press('down', 6, 0.2)
    ag.press('f4')
    ag.press('down', 2, 0.2)
    ag.press('enter')


# ## 导出加载

# In[20]:


# 期间选择
s_date, e_date = get_month_start_end(fin_period)

year = fin_period[:4]
period = fin_period[4:6]
period_int = int(period)

# 公司代码
com_item = com_lists

# 工厂代码
factory_code = str(int(com_item) + 1)

today = pd.Timestamp.now().strftime('%Y-%m-%d')

# 上月月底（当前月往前推1个月）
l_date = (pd.to_datetime(fin_period, format='%Y%m') - pd.offsets.MonthEnd(1)).strftime('%Y-%m-%d')

# 上月月初往期推1年（即上月的月初再减12个月）
l_month_start = (pd.to_datetime(fin_period, format='%Y%m') - pd.offsets.MonthBegin(1) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')

# 根据公司代码设置采购项目
if com_item == '0020':
    purchase_item = '110'
elif com_item == '0021':
    purchase_item = '120'
else:
    purchase_item = '111'


# In[21]:


for item in not_contained:
    # 判断是否带 _序号
    if '_' in item:
        tcode, seq_str = item.split('_')
        seq = int(seq_str) - 1  # list 索引从 0 开始
        desc_list = ticode_dict[tcode]
        desc = desc_list[seq]
        load_func_name = f"load_{tcode.replace(r'.','')}_{seq+1}"  # 构造函数名，如 load_zmm020_2
        
        full_prefix = expected_prefixes[tcode][seq]
        index_str = full_prefix.rstrip('-')
        
    else:
        tcode = item
        desc_list = ticode_dict[tcode]
        desc = desc_list[0]
        load_func_name = f"load_{tcode.replace(r'.','')}"  # 构造函数名，如 load_zmm026
        
        full_prefix = expected_prefixes[tcode][0]
        index_str = full_prefix.rstrip('-')

    
    # 原有的处理逻辑（非 IDCNBSAIS）
    # 文件名
    dir_name = f"{index_str}-{tcode}-{desc}.xlsx"

    # 保存路径
    save_dir = os.path.join(os.getcwd(), sap_path)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, dir_name).replace('/', '\\')

    # SAP 自动化流程
    for _ in range(8):
        ag.press('f24')
        time.sleep(0.7)
        if find_hwnd_blur('SAP 轻松访问') != 0:
            break
        else:
            continue
    time.sleep(0.5)
    pyperclip.copy(tcode)
    time.sleep(0.3)
    ag.hotkey('ctrl', 'v')
    load_complete(max_duration=20, pre_name='enter')

    # 特殊处理：如果是 FBL1N，先去读取zmm020的供应商编码
    if item == 'ZMM020_1':
        # 需要供应商编码
        app = xw.App(visible=True, add_book=False)
    
        # 获取 ZSD011 文件路径
        F19_dir = get_path(root_dir=sap_path, text_num='01')[0]
    
        # 读取并处理 df
        df_01 = read(F19_dir, row=5, col_list=['采购凭证','供应商','过账日期'])
        df_01 = df_notnull(df_01, split_list=['采购凭证', '供应商'], null_list=['供应商'])
        df_01['过账日期'] = pd.to_datetime(df_01['过账日期'], errors='coerce')
        df_01 = df_01[(df_01['过账日期'] >= l_month_start) & (df_01['过账日期'] <= l_date)]
        df_01 = df_01.drop_duplicates(subset=['采购凭证'], keep='first')
        app.kill()
        
    elif item == 'ZMM020_2':
        # 需要供应商编码
        app = xw.App(visible=True, add_book=False)
        # 获取 ZSD011 文件路径
        FBL1N_dir = get_path(root_dir=sap_path, text_num='03')[0]
        
        # 读取并处理 df
        df_02 = read(FBL1N_dir, col_list=['特别总帐标志','文本'])
        df_02 = df_notnull(df_02, split_list=['特别总帐标志','文本'], null_list=['文本'])
        df_02 = df_02[df_02['特别总帐标志'] == 'Z']
        
        # 提取文本中以52开头的数字作为采购凭证
        df_02['采购凭证'] = df_02['文本'].apply(lambda x: re.findall(r'\b52\d*\b', str(x))[0] if re.findall(r'\b52\d*\b', str(x)) else None)
        # 去除提取失败的行
        df_02 = df_02.dropna(subset=['采购凭证'])
        # 去重
        df_02 = df_02.drop_duplicates(subset=['采购凭证'], keep='first')
        app.kill()
        
    # 调用对应 load 函数
    load_ticode = globals().get(load_func_name)
    load_ticode()
    
    load_complete()

    # 特殊处理：如果是 FAGLL03H，则执行额外操作
    if load_func_name == "load_FAGLL03H":
        for _ in range(13):
            ag.hotkey('shift', 'tab')
        time.sleep(0.5)  # 等待界面响应
        for _ in range(8):
            ag.press('enter')
            time.sleep(0.3)
            if find_hwnd_blur('查找') != 0:
                break
            else:
                continue
        time.sleep(0.5)
        pyperclip.copy('/FI048')
        time.sleep(0.3)
        ag.hotkey('ctrl', 'v')
        ag.press('enter')
        ag.press('f12')
        ag.press('enter')
        time.sleep(7)
    

    # 保存文件
    layout_text = get_layout_text(item, tcode)
    if layout_text:
        choose_layout(layout_text)
    if tcode == 'F.19':
        for _ in range(5):
            ag.press('f24')
            time.sleep(0.5)
            if find_hwnd_blur('货物/己收发票结算科目分析和购置税显示') == 0:
                continue
            else:
                # 找到了窗口，等0.5秒后退出循环
                time.sleep(0.5)
                break
        # 循环结束后执行保存
        save_f19(save_path)
    else:
        save_excel(save_path)

    time.sleep(0.3)

    for _ in range(7):
        ag.press('f24')
        time.sleep(0.5)
        if find_hwnd_blur(desc) != 0:
            continue
        else:
            time.sleep(0.7)
            break


# # 退出SAP

# In[22]:


time.sleep(0.5)
ag.press('f3')
for _ in range(10):
    ag.press('f24')
    time.sleep(0.7)
    if find_hwnd_blur('SAP 轻松访问')==0:
        continue
    else:
        h=find_hwnd_blur('SAP 轻松访问')
        win32gui.PostMessage(h, win32con.WM_CLOSE, 0, 0)#BOM查询报表
        break

time.sleep(1)
h=win32gui.FindWindow(None,"SAP Logon 740")
win32gui.PostMessage(h, win32con.WM_CLOSE, 0, 0)#SAP Logon 740
