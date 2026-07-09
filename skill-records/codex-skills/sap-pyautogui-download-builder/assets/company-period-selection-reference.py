#!/usr/bin/env python
# coding: utf-8

"""轻量期间选择母版：初始化 SAP 登录/业务配置、录入参数并备份上期目录。

该母版来自用户修改后的通用版本。生成具体项目脚本时必须替换
`TODO_APPROVED_PROJECT_PATH` 和 `TODO_BUSINESS_SECTION`。
"""

# In[1]:


get_ipython().run_line_magic('cd', r'TODO_APPROVED_PROJECT_PATH')


# In[2]:


import win32com.client,win32gui,win32con
import pandas as pd
import numpy as np
import os,sys,re,shutil,psutil,time,datetime,traceback,ctypes,subprocess,configparser
import fitz,calendar
import importlib.util
from tkinter import messagebox
import configparser
from pathlib import Path
pd.set_option("display.float_format", lambda x: "%.2f" % x)#不显示科学计数

pd.options.mode.chained_assignment = None#忽略警告


# In[3]:


root_dir = "1.原始数据"
save_dir = "2.运行结果"


# In[4]:


default_com = next((s for s in os.getcwd().split('\\')[-1].split('-') if s.isdigit()), '')


# In[5]:


today = datetime.date.today()
this_month = today.strftime('%Y%m')

# ==================== SAP登录配置 ====================
login_file = r'd:/sap_download_config.ini'
login_section = 'FI_FB'
login_config = configparser.ConfigParser()
need_save = False

if os.path.exists(login_file):
    # 方法1：使用 utf-8-sig 自动处理 BOM
    import codecs
    with codecs.open(login_file, 'r', encoding='utf-8-sig') as f:
        login_config.read_file(f)
else:
    need_save = True

if login_section not in login_config:
    login_config[login_section] = {'SAP账号': 'FI000', '密码': '000000'}
    need_save = True

if need_save:
    with open(login_file, 'w', encoding='utf-8-sig') as f:
        login_config.write(f)
    print("✅ SAP登录配置文件已初始化")

# ==================== 业务配置 ====================
# 创建配置表目录
root_path = os.path.join(os.getcwd(), root_dir)
os.makedirs(root_path, exist_ok=True)

# 业务配置文件路径
business_file = os.path.join(root_path, 'sap_business_config.ini')
business_section = 'TODO_BUSINESS_SECTION'
business_config = configparser.ConfigParser()
need_save = False

if os.path.exists(business_file):
    business_config.read(business_file, encoding='utf-8-sig')
else:
    need_save = True

if business_section not in business_config:
    business_config[business_section] = {'com_lists': default_com, 'fin_period': this_month}
    need_save = True

if need_save:
    with open(business_file, 'w', encoding='utf-8-sig') as f:
        business_config.write(f)
    print(f"✅ 业务配置文件已初始化: {business_file}")

# ==================== 读取配置 ====================
username = login_config.get(login_section, 'SAP账号')
password = login_config.get(login_section, '密码')
com_lists = business_config.get(business_section, 'com_lists')
fin_period = business_config.get(business_section, 'fin_period')

date_input = (username, password, com_lists, fin_period)
# print(f"📋 当前配置: 账号={username}, 公司代码={com_lists}, 账期={fin_period}")


# In[6]:


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def center_window(window, width=400, height=300):
    """使窗口居中显示"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (width / 2))
    y_cordinate = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")
    
def create_input_window(num_entries, text, text_list, result_variable, default_values=None):
    def validate_period(raw_period):
        raw = raw_period.strip()
        if raw.isdigit():
            if len(raw) == 6:
                return raw
            if len(raw) == 5:
                return raw[:4] + raw[4:].zfill(2)
        return None

    def submit():
        result_variable.clear()

        for i in range(num_entries):
            value = entries[i].get()

            # 密码框特殊处理：index = 1
            if i == 1:
                if value == "******":
                    if default_values and len(default_values) > 1:
                        value = default_values[1]

            result_variable.append(value)

        # 校验期间
        valid_period = validate_period(result_variable[3])
        if valid_period is None:
            messagebox.showerror("格式错误", "期间必须为 YYYYMM，例如：202507")
            return
        result_variable[3] = valid_period

        root.quit()

    def on_enter_key(event):
        # 确保在任何控件上按Enter都能触发提交
        submit()
        return "break"  # 阻止事件进一步传播

    root = tk.Tk()
    root.title("SAP下载参数")
    root.attributes("-topmost", True)
    center_window(root)

    # 在根窗口上绑定Enter键事件
    root.bind_all('<Key-Return>', on_enter_key)
    root.bind_all('<KP_Enter>', on_enter_key)  # 同时支持数字键盘的Enter

    ttk.Label(root, text=text).grid(row=0, column=0, padx=10, pady=10)

    entries = []
    for i in range(num_entries):
        ttk.Label(root, text=text_list[i]).grid(row=i+1, column=0, padx=12, pady=5, sticky="w")
        entry = ttk.Entry(root)

        if i == 1:  # 密码字段
            entry.config(show="*")
            if default_values and len(default_values) > 1:
                entry.insert(0, "******")
        else:
            if default_values and i < len(default_values):
                entry.insert(0, default_values[i])

        entry.grid(row=i+1, column=1, padx=12, pady=7)
        entries.append(entry)
        
        # 为每个输入框也绑定事件
        entry.bind('<Key-Return>', on_enter_key)
        entry.bind('<KP_Enter>', on_enter_key)

    # 确保第一个输入框获得焦点
    if entries:
        entries[0].focus_set()

    ttk.Button(root, text="确认", command=submit).grid(row=num_entries+1, column=1, columnspan=2, pady=20)

    root.mainloop()
    root.destroy()


# In[7]:


# 用于存储用户输入的值
date_input = []

# 默认参数值，如果为None或不提供，输入框将为空
default_values = [username, password, com_lists, this_month]

# 调用函数，创建4个输入框
create_input_window(4, "请输入参数：", ['SAP账号', '密码','公司代码', '期间'],date_input, default_values)

# 清理掉中文逗号并打印用户输入的日期
date_input = [i.replace('，', ',') for i in date_input]
date_input_copy=date_input.copy()
date_input_copy[1]='*'


# In[8]:


# ==================== 更新配置文件 ====================
if date_input:
    username, password, com_lists, fin_period = date_input
    
    # 更新SAP登录信息到原配置文件
    login_config = configparser.ConfigParser()
    login_config.read(login_file, encoding='utf-8-sig')
    if login_section not in login_config:
        login_config[login_section] = {}
    login_config[login_section]['SAP账号'] = username
    login_config[login_section]['密码'] = password
    with open(login_file, 'w', encoding='utf-8-sig') as f:
        login_config.write(f)
    
    # 更新业务配置信息到新配置文件
    business_config = configparser.ConfigParser()
    business_config.read(business_file, encoding='utf-8-sig')
    if business_section not in business_config:
        business_config[business_section] = {}
    business_config[business_section]['com_lists'] = com_lists
    business_config[business_section]['fin_period'] = fin_period
    with open(business_file, 'w', encoding='utf-8-sig') as f:
        business_config.write(f)
    
    print(f"📋 最新配置: SAP账号 = {username}, 分公司代码 = {com_lists}, 账期 = {fin_period}")
else:
    print("⚠️ 未更新任何配置，使用原有配置")


# In[9]:


# 参数设置
backup_dir = "0.数据备份"

# 计算上一个月份
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 将 fin_period 转换为日期并减去一个月
current_period = datetime.strptime(fin_period, '%Y%m')
previous_period = (current_period - relativedelta(months=1)).strftime('%Y%m')
backup_target_period = previous_period  # 例如：fin_period='202602' 时，备份到 '202601'

# 创建备份主目录
Path(backup_dir).mkdir(exist_ok=True)

# 创建备份目标子文件夹（使用上一个月份）
target_backup_dir = os.path.join(backup_dir, backup_target_period)
Path(target_backup_dir).mkdir(exist_ok=True)

# 复制 root_dir 到备份文件夹
if os.path.exists(root_dir):
    dest_root = os.path.join(target_backup_dir, os.path.basename(root_dir))
    if os.path.exists(dest_root):
        shutil.rmtree(dest_root)  # 如果已存在，先删除
    shutil.copytree(root_dir, dest_root)
    print(f"已复制 {root_dir} 到 {dest_root}")

# 复制 save_dir 到备份文件夹
if os.path.exists(save_dir):
    dest_save = os.path.join(target_backup_dir, os.path.basename(save_dir))
    if os.path.exists(dest_save):
        shutil.rmtree(dest_save)
    shutil.copytree(save_dir, dest_save)
    print(f"已复制 {save_dir} 到 {dest_save}")

print(f"备份完成！所有内容已保存到 {backup_dir}/{backup_target_period}/")
