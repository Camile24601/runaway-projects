# SAP 下载后处理与运行状态规则

适用场景：SAP 下载脚本在主体 Excel 导出后，还需要 temp 文件、Excel 回写、物料/供应商补充、文件重命名、跨系统补下载等后处理。

## 核心原则

运行状态只能在完整下载链路全部成功后更新。主体 Excel 文件存在不等于步骤成功。

## 必查链路

对于每个下载项目，先列清楚：

1. 主体文件是否成功导出；
2. 是否需要 temp/辅助文件；
3. temp 是否必须重新下载，是否允许复用旧 temp；
4. 是否需要回写主体 Excel；
5. 是否需要字段补充或格式保留；
6. 哪些环节失败时必须阻断运行状态更新。

## 状态更新位置

`update_run_status(...)` 必须放在所有必要后处理之后。

```python
temp_downloaded = download_temp(...)
if not temp_downloaded:
    raise RuntimeError("主体文件已下载，但 temp 下载失败，本次不更新成功状态。")

postprocess_ok = postprocess_temp(...)
if not postprocess_ok:
    raise RuntimeError("temp 回写失败，本次不更新成功状态。")

supplement_ok = fill_required_fields(...)
if not supplement_ok:
    raise RuntimeError("必要字段补充失败，本次不更新成功状态。")

update_run_status(...)
```

不要捕获异常后只打印警告然后继续更新成功状态。

## Excel 后处理

SAP 导出的 Excel 需要保留原工作簿结构时，优先使用 `xlwings` 定点回写单元格。不要用 `pandas.ExcelWriter(..., mode='w')` 重建工作簿，否则可能改变工作表名称、格式、列宽、筛选、隐藏内容、日期和长编码格式。

补充字段只能补空时，必须明确空值判断，不能覆盖原表已有值。

## 布局与页面层级

同一 TCode 多公司循环时，布局选择位置必须按已验证流程保留。不要擅自把“每家公司选择一次布局”改成“只第一家公司选择一次布局”，也不要凭想象增加 `layout_applied` 之类状态变量。

返回页面时，必须逐行确认 F3、Shift+F3、F12 与外层 TCode 循环的关系；禁止因为推测导致退出 SAP 或跳错层级。

## SAP Logon 兼容

不同 SAP Logon 版本差异应优先按窗口标题或已验证 UI 特征判断。不要因为某个控件存在就推断版本；例如新版本中也可能存在其他 Edit 控件。

真实 IP、账号、密码不得写入 skill 或公开母版，应从项目配置文件读取。
