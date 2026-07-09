# ZMM020 示例：按原公司写法落地

## 用户输入示例

```markdown
TCode：ZMM020
输出编号：1-1
Excel 描述：采购订单明细
SAP 操作：
1. down 10 次
2. tab 2 次
3. 调用多项选择函数，输入 df_01 的凭证编号列
数据来源：
- df_01 来自 sap_path 目录下前缀为 01 的 Excel
- 读取列：凭证编号
```

## 仍需确认

- `凭证编号` 是否允许去除前导零。原 `df_notnull(..., split_list=['凭证编号'])` 会删除前导零。
- 上游文件是否就在原脚本变量 `sap_path` 指向的目录。
- 默认第一个可见 Sheet 是否包含 `凭证编号`。
- `down` 十次和 `tab` 两次后是否已经定位到该字段的多项选择入口。
- 是否使用原脚本的标准 `save_excel()` 流程。

## 只改业务配置

```python
ticode_number_map = {
    'ZMM020': ['1-1'],
}

ticode_dict = {
    'ZMM020': ['采购订单明细',],
}
```

## 读取上游数据

当确认允许使用原清洗逻辑，包括删除前导零时：

```python
if tcode == 'ZMM020':
    app = xw.App(visible=True, add_book=False)

    source_path = get_path(root_dir=sap_path, text_num='01')[0]
    df_01 = read(source_path, col_list=['凭证编号'])
    df_01 = df_notnull(
        df_01,
        split_list=['凭证编号'],
        null_list=['凭证编号']
    )
    df_01 = df_01.drop_duplicates(subset=['凭证编号'], keep='first')
    app.kill()
```

当必须保留前导零时，不调用 `split_list` 的原清洗分支，应仅过滤空值并去重，例如：

```python
if tcode == 'ZMM020':
    app = xw.App(visible=True, add_book=False)

    source_path = get_path(root_dir=sap_path, text_num='01')[0]
    df_01 = read(source_path, col_list=['凭证编号'])
    df_01 = df_01[
        ~df_01[['凭证编号']].fillna("").astype(str).applymap(
            lambda x: x in ["", "None"]
        ).all(axis=1)
    ]
    df_01 = df_01.drop_duplicates(subset=['凭证编号'], keep='first')
    app.kill()
```

## 只新增对应 Loader

```python
def load_ZMM020():
    ag.press('down', 10, 0.2)
    ag.press('tab', 2, 0.2)
    mul_choice(df_01['凭证编号'])
```

## 关键认识

这一类需求不需要重写 `read()`、`get_path()`、`mul_choice()` 或主循环。AI 应当将你的描述翻译为原母版中的配置、数据准备段和 `load_ZMM020()`，并把尚未确认的业务规则列出来。
