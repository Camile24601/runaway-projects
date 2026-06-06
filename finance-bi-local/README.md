# 本地财务 BI 报告生成器

第一版目标：从本地 Excel/CSV 生成 HTML 报告，默认脱敏客户、供应商和所有金额。

## 运行示例

```bash
cd finance-bi-local
python3 -m pip install -r requirements.txt
python3 report_generator.py sample_data/finance_sample.csv --output output/report.html
```

如果使用 Codex 内置 Python，可运行：

```bash
/Users/camile/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 report_generator.py sample_data/finance_sample.csv --output output/report.html
```

## 第一版分析角度

- 采购金额趋势指数，首期=100。
- 供应商采购占比，供应商名称脱敏。
- 利润趋势指数，首期=100。
- 利润率趋势，如有收入字段。
- 单价横向比较：同一期间、同一产品/物料内，不同供应商的单价指数，组内中位数=100。
- 单价纵向变动：同一产品/物料、同一供应商内，跨期间比较单价指数，首期=100。
- 单价不展示原始值，只展示指数、较同组中位数偏离、较首期/上期变化。
- 账期变动分析。

## 隐私规则

- 默认不展示原始金额。
- 金额仅以指数、占比、变化率、利润率展示。
- 客户和供应商用稳定哈希标签替代。
- 报告不包含原始明细数据。
