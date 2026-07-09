# AP051 人工修正版规则

## 适用场景

当用户需求包含 AP051、F.19、FBL1N、ZMM020、收货凭证、入账订单明细、采购对账单、供应商特别总账业务等关键词时，优先参考本文件和下载母版中的 AP051 修正版。

## 输出编号和描述

AP051 修正版最终使用：

```python
ticode_number_map = {
    'F.19': ['01'],
    'FBL1N': ['03'],
    'ZMM020': ['02', '05'],
}

ticode_dict = {
    'F.19': ['收货凭证',],
    ,'FBL1N': ['入账订单明细',]
    ,'ZMM020': ['采购对账单','采购对账单',]
}
```

注意：用户初始需求中可能写 `04-ZMM020` 或 `收货/发货清算`，但人工修正版改成 `05-ZMM020` 和 `F.19: 收货凭证`。以后生成同类 AP051 时，除非用户明确反对，沿用人工修正版。

## F.19 布局处理

不要把 F.19 的布局后处理放到主循环里。人工修正版将其放入 `load_F19()`：

- 输入总账科目 `2202020100`。
- 输入公司代码 `com_item`。
- 输入当天日期变量 `today`。
- 先 `load_complete()`。
- 再 `ag.hotkey('ctrl','f8')` 打开布局。
- 等待 `更改布局`。
- 调用 `click_multi_logon_checkbox()`，该函数固定查找 `更改布局` 窗口，并点击最后一个按钮向左偏移 250 像素的位置。
- 两次 `shift+tab`，`enter`。
- 等待 `扫描字段列表`。
- 粘贴 `过账日期`。
- `enter`，`ctrl+f3`，`enter`。

## F.19 保存

使用 `save_f19(save_path)`。保存前等待窗口：

```python
find_hwnd_blur('货物/己收发票结算科目分析和购置税显示')
```

`save_f19()` 会将文件保存为 `.xls`，并在 `-F.19` 后添加空格。这是公司现用流程，不要擅自改成通用 `save_excel()`。

## 日期变量

人工修正版使用：

```python
today = pd.Timestamp.now().strftime('%Y-%m-%d')
l_date = (pd.to_datetime(fin_period, format='%Y%m') - pd.offsets.MonthEnd(1)).strftime('%Y-%m-%d')
l_month_start = (
    pd.to_datetime(fin_period, format='%Y%m')
    - pd.offsets.MonthBegin(1)
    - pd.DateOffset(years=1)
).strftime('%Y-%m-%d')
```

`l_month_start` 不是简单的 `上一年 01-01`，而是“上月月初往前推 1 年”。例如 `fin_period=202501` 时得到 `2023-12-01`。不要把它改成 `2024-01-01`，除非用户明确要求。

## 上游文件读取

第一张 ZMM020 读取 F.19：

```python
F19_dir = get_path(root_dir=sap_path, text_num='01')[0]
df_01 = read(F19_dir, row=5, col_list=['采购凭证','供应商','过账日期'])
df_01 = df_notnull(df_01, split_list=['采购凭证', '供应商'], null_list=['供应商'])
df_01['过账日期'] = pd.to_datetime(df_01['过账日期'], errors='coerce')
df_01 = df_01[(df_01['过账日期'] >= l_month_start) & (df_01['过账日期'] <= l_date)]
df_01 = df_01.drop_duplicates(subset=['采购凭证'], keep='first')
```

关键点：

- 表头行是 `row=5`，不是第三行。
- 需要读取 `供应商` 并以供应商非空作为有效行判断。
- 使用 `l_month_start` 到 `l_date` 的日期范围。

第二张 ZMM020 读取 FBL1N：

```python
FBL1N_dir = get_path(root_dir=sap_path, text_num='03')[0]
df_02 = read(FBL1N_dir, col_list=['特别总帐标志','文本'])
df_02 = df_notnull(df_02, split_list=['特别总帐标志','文本'], null_list=['文本'])
df_02 = df_02[df_02['特别总帐标志'] == 'Z']
df_02['采购凭证'] = df_02['文本'].apply(
    lambda x: re.findall(r'\b52\d*\b', str(x))[0]
    if re.findall(r'\b52\d*\b', str(x)) else None
)
df_02 = df_02.dropna(subset=['采购凭证'])
df_02 = df_02.drop_duplicates(subset=['采购凭证'], keep='first')
```

关键点：

- 必须读取 `特别总帐标志`。
- 只保留 `特别总帐标志 == 'Z'`。
- 采购凭证变量名为 `df_02['采购凭证']`，对应 `load_ZMM020_2()`。

## 完整项目默认输出

遇到类似“生成 SAP 下载”的完整项目，默认同时输出：

- `01-公司期间选择.py`
- `02-SAP数据下载-<项目名>.py`

二者必须使用相同的 `business_section`。如果用户只要求 `02`，仍应提醒 `01` 是默认需要的，除非用户明确已有。
