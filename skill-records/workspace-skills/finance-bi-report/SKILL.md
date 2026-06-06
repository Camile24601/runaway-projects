---
name: finance-bi-report
description: Use when generating local finance BI-style HTML reports from Excel, CSV, or approved database/MCP data sources, especially for sales, purchase, payment, profit statement, payable, unit-price, or payment-term analysis with strict privacy masking and non-exaggerated conclusions.
---

# Finance BI Report

## Required preflight

Before generating a report, confirm or infer these items:

- Data type: sales, purchase, payment, profit statement, payable, or mixed.
- Input source: local Excel/CSV, approved database export, or approved MCP data source.
- Analysis angles requested by the user.
- Field mapping for date, customer, supplier, product/material, purchase amount, sales amount, cost, profit, unit price, quantity, and payment term days.
- Sensitive fields. Default: mask customer, supplier, and all amount fields.
- Audience and whether cause speculation is allowed. Default: do not speculate.

## Default analysis modules

Use these modules when fields are available:

- Purchase amount analysis: trend index, supplier contribution percent, product/category contribution percent.
- Profit analysis: profit trend index and profit margin when revenue is available.
- Unit price analysis: use tables by default. Horizontal comparison means same period + same product/material across suppliers/customers, indexed to that peer-group median=100. Vertical comparison means same product/material + same supplier/customer across periods, indexed to that combination's first period=100.
- Payment term analysis: average payment days, period-over-period day changes, supplier/customer split when available.
- Data limitations: list fields not present and conclusions that cannot be supported.

## Privacy rules

- Never display raw amount values by default.
- Display amounts only as index, percentage, ranking, contribution share, or change rate.
- Mask customer and supplier names with stable labels.
- Do not include raw row-level data in the HTML unless the user explicitly asks and confirms the sensitivity risk.
- Keep processing local unless the user explicitly approves an external connection.

## Writing rules

- Every conclusion must be supported by a visible number in the report.
- Use neutral wording: "increase", "decrease", "higher than", "lower than", "concentrated in".
- Avoid unsupported words such as "显著", "严重", "优秀", "强劲", "大幅改善" unless the user supplied a threshold and the metric crosses it.
- If the data does not contain cause fields, write "当前数据无法判断原因".
- Separate facts from possible explanations.
- For unit-price analysis, do not compare overall average unit price across mixed product structures unless the user explicitly requests it. Prefer same-product peer and same-combination time comparisons.

## MCP guidance

For database access, prefer MCP tools that expose constrained read-only operations:

- List approved sources and schemas.
- Query only approved tables/views.
- Use parameterized or named queries where possible.
- Enforce row limits and column allowlists.
- Return aggregated data by default.
- Reject writes, DDL, credential export, and unrestricted `SELECT *`.

Do not ask for direct production database credentials in chat. Ask the user to configure a read-only MCP server or provide a local export.
