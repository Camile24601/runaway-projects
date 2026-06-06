---
name: sap-pyautogui-download-builder
description: Generate or modify SAP GUI download Python scripts by faithfully following the company's existing pyautogui, win32gui, xlwings, and configuration-file style. Use when the user provides a TCode, SAP key-operation steps, Excel export naming, upstream Excel dependencies, or asks to update company SAP download scripts while retaining original shared functions and framework behavior.
---

# SAP 下载脚本保真生成器

## 核心原则

以公司现有脚本写法为标准，而不是重新设计框架。默认只修改业务相关代码，不重构公共函数。

## 工作流程

1. 修改已有脚本时，先读取目标脚本，并以该文件本身为最高优先级母版。
2. 新建脚本时，先读取 [assets/company-sap-download-mother-reference.py](assets/company-sap-download-mother-reference.py)，复制其公共结构，再替换业务段。
3. 新建或修改包含 SAP 下载的完整项目时，必须默认同时生成或保留 `01-公司期间选择.py` 和 `02-SAP数据下载*.py`；读取 [assets/company-period-selection-reference.py](assets/company-period-selection-reference.py) 作为轻量通用母版，读取 [assets/company-sap-download-mother-reference.py](assets/company-sap-download-mother-reference.py) 作为下载母版。只有用户明确说明已有可复用期间选择脚本或不需要第一步时才跳过 `01`。
4. 修改代码前读取 [references/preservation-rules.md](references/preservation-rules.md)，识别允许变更段和默认禁止变更段。
5. 用户需求不完整时，按 [references/request-spec.md](references/request-spec.md) 补充缺失项，或生成带 `TODO` 的草稿并明确不可直接执行。
6. 生成期间选择脚本时，读取 [references/period-selection-rules.md](references/period-selection-rules.md)，优先套用账号/密码/公司/期间四输入框模式。
7. 涉及上游 Excel 和多项选择时，参考 [references/zmm020-worked-example.md](references/zmm020-worked-example.md) 的原写法模式；遇到 AP051/F.19/FBL1N/ZMM020 组合时，优先读取 [references/ap051-worked-example.md](references/ap051-worked-example.md)。
8. 输出完整 `.py` 文件，除非用户明确只要代码片段或解释。
9. 生成后运行 `python -m py_compile <output.py>`；不得声称已验证真实 SAP 点击流程，除非确实在用户环境完成验证。

## 默认保留内容

修改现有脚本或基于公司母版新建时，除非用户明确要求，否则原样保留：

- `get_path()`、`read()`、`df_notnull()` 及其调用风格。
- `find_hwnd_all()`、`find_hwnd_blur()`、`click_multi_logon()`、`mul_choice()`、`load_complete()`。
- `save_excel()` 与已有的经确认特殊保存函数。
- SAP 登录、配置读取和退出 SAP 的整体流程。
- 原脚本的变量命名风格，例如 `sap_path`、`com_lists`、`fin_period`、`df_01`。
- AP051/F.19 类特殊布局处理应保留在对应 `load_F19()` 中，不默认挪到主循环后处理。
- 期间选择程序中的登录/业务配置初始化与写入、密码脱敏显示、主键盘与数字键盘 `Enter` 提交绑定，以及按上一期间备份项目数据目录的处理方式。

不得为“更优雅”而默认替换成 dataclass、任务注册表、上下文对象、新读取函数或新的异常处理框架。

## 可修改内容

根据用户提供的下载需求，通常只修改：

- `ticode_dict` 与 `ticode_number_map`。
- 需要下载的 TCode 对应的 `load_<TCODE>()` 或 `load_<TCODE>_<序号>()`。
- 与该 TCode 直接关联的上游 Excel 读取准备段。
- 必要的执行后特殊动作或已确认的特殊导出函数调用。
- 输出文件序号及描述。

生成 `01-公司期间选择.py` 时，应自动替换项目路径、`login_section`、`business_section`、项目目录名和备份目录清单；若用户未说明，默认 `login_section='FI_FB'`、`root_dir='1.原始数据'`、`save_dir='2.运行结果'`、`backup_dir='0.数据备份'`。应提示用户该母版在同一备份期间已存在时会覆盖旧备份目录；除非用户明确要求，不要移除备份步骤。

对上游 Excel 的读取，优先组合原母版中的：

```python
source_path = get_path(root_dir=sap_path, text_num='01')[0]
df_01 = read(source_path, col_list=['凭证编号'])
df_01 = df_notnull(df_01, split_list=['凭证编号'], null_list=['凭证编号'])
df_01 = df_01.drop_duplicates(subset=['凭证编号'], keep='first')
```

如果编号需要保留前导零，不得直接使用会执行 `str.lstrip('0')` 的清理逻辑；先向用户确认或只过滤空值。

## 资料

- [references/preservation-rules.md](references/preservation-rules.md)：保真修改规则与检查清单。
- [references/request-spec.md](references/request-spec.md)：以后提交新 TCode 需求的格式。
- [references/period-selection-rules.md](references/period-selection-rules.md)：轻量期间选择脚本生成规则。
- [references/zmm020-worked-example.md](references/zmm020-worked-example.md)：本轮示例如何映射到公司原脚本。
- [references/ap051-worked-example.md](references/ap051-worked-example.md)：AP051 人工修正版中的关键规则。
- [assets/company-sap-download-mother-reference.py](assets/company-sap-download-mother-reference.py)：已脱敏的 SAP 下载母版参考。
- [assets/company-period-selection-reference.py](assets/company-period-selection-reference.py)：已脱敏的期间选择参考，仅在需要时读取。
