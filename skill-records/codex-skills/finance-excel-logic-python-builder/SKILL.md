---
name: finance-excel-logic-python-builder
description: Generate or modify company-style Python automation programs from finance business logic described in Excel workbooks, sample source files, result templates, and existing scripts. Use when a finance requester supplies one or more Excel sheets containing filtering, matching, calculations, reconciliations, workbook updates, report-output rules, or step-by-step processing requirements, and Codex must analyze the rules, identify clarification items, split the work into multiple numbered .py files where appropriate, and implement pandas/xlwings-based processing while preserving established company patterns. Do not use as the primary skill for SAP GUI download clicking steps; coordinate with sap-pyautogui-download-builder for those steps.
---

# 财务 Excel 逻辑程序生成器

## 核心原则

将业务人员提供的逻辑说明、样例数据和目标报表转换成可核对的业务规格，再按实际执行顺序生成一份或多份 Python 程序。不要把一个业务需求默认塞进一份脚本，也不要猜测会计判断、匹配口径或报表更新口径。

生成完整代码前必须先向用户提交确认稿，列明脚本拆分、每步输入输出、每张过程表/结果表、核心业务逻辑、待确认事项和验证方式。只有用户明确回复“可以生成”“确认生成”或同等意思后，才开始写完整 `.py` 文件；在确认前只能做资料读取、规则梳理、方案设计和草稿级 TODO。

确认稿中的待确认事项必须可追溯：逐条标明来源 Sheet、对应程序步骤、影响的字段/表、需要业务确认的问题，以及不确认会影响什么结果。不要只给笼统问题。

## 开始前读取

1. 读取 [references/requirement-intake.md](references/requirement-intake.md)，核查资料是否足够。
2. 读取 [references/company-python-style.md](references/company-python-style.md)，遵守现有程序风格。
3. 读取 [references/company-environment-constraints.md](references/company-environment-constraints.md)，遵守公司可用库、数据库读写、Excel 加密文件读取和 bug 复盘约束。
4. 需求涉及多个程序或多个输出阶段时，读取 [references/multi-step-design.md](references/multi-step-design.md)。
5. 写完代码后读取 [references/validation-checklist.md](references/validation-checklist.md)。
6. 新建数据处理或结果回写脚本时，可复制 [assets/business-processing-template.py](assets/business-processing-template.py) 的相关片段；如有同业务或同类现有脚本，以现有脚本为最高优先级母版。

## 工作流程

### 1. 收集与识别资料

收集逻辑说明工作簿、各输入文件样例、目标输出模板或历史输出、同类现有 `.py`、配置文件字段约定和执行步骤要求。

对于逻辑说明 Excel，逐个 Sheet 建立清单，不只读取第一个 Sheet。识别：

- Sheet 名称、用途、标题行位置及关键区域。
- 输入来源、所需字段、过滤规则、匹配键、计算规则、核对规则、输出去向。
- 颜色、批注、示例行、公式、跨 Sheet 引用是否承载规则。
- 同一条规则是否与其他 Sheet 矛盾或依赖人工判断。

不得修改用户提供的逻辑说明、原始数据样例或历史输出文件，除非用户明确要求修改。

### 2. 形成业务规格并识别缺口

在写代码前输出或内部整理以下表格：

- `Sheet/规则清单`：每个逻辑 Sheet 对应哪些程序步骤与输出。
- `输入数据清单`：文件、Sheet、表头行、必需字段、读取方式、清洗要求。
- `业务规则清单`：筛选、匹配、计算、分类、异常处理、核对口径。
- `输出清单`：目标工作簿/Sheet、写入方式、追加或覆盖、格式/公式保留要求。
- `程序拆分清单`：每份 `.py` 的序号、名称、输入、输出、与上下步骤的交接文件。
- `逐 Sheet 理解清单`：每个已读取 Sheet 的用途、已理解逻辑、落地到哪个程序步骤、生成/影响哪些表、仍缺哪些字段或口径。
- `数据库搭建审查清单`：凡需求涉及数据库，确认稿必须列出拟建库/表、主键/唯一键、字段来源、数据覆盖或追加策略、需要增删改查的维护表、建议页面组织、导入日志和状态表；未经用户确认不得直接创建正式数据库结构。
- `待确认事项`：影响结果正确性的歧义或缺失资料。

凡是影响金额、税额、分类、匹配优先级、期间数据覆盖、报表公式或人工复核的缺口，先标为待确认项；可生成不执行关键判断的草稿，但不得静默选择口径。

### 3. 判断应生成多少份程序

保留用户已有的步骤拆分与编号习惯。没有明确拆分时，按职责和交付边界拆分，而不是按代码长度拆分。

典型步骤可包含：

- `01-公司期间选择.py`：包含 SAP 下载的项目默认创建或保留此第一步；按当前公司母版录入 SAP/业务参数、支持 `Enter` 提交，并执行上期目录数据备份。只有用户明确已有可复用第一步或不需要时才跳过。
- `02-SAP数据下载-*.py`：如包含 SAP GUI 下载动作，使用 `sap-pyautogui-download-builder` 处理该程序。
- `03-数据处理-*.py`：读取源文件、清洗、匹配、计算并生成过程数据。
- `04-结果输出.py`：更新目标工作簿多个 Sheet、保留模板格式/公式、生成最终结果。
- 后续独立步骤：PDF、HTML 分析报表、邮件发送等，只有需求明确时创建。

多个业务规则 Sheet 不等于必须生成多个脚本；多个有独立运行顺序、独立输入输出、可单独重跑或需要人工检查的步骤，通常应拆成多个脚本。参照 [references/multi-step-design.md](references/multi-step-design.md)。

### 4. 编写程序

开始写完整程序前，先检查用户是否已经确认生成。若用户尚未明确确认，停止在规格确认阶段，输出需要确认的拆分方案与逻辑清单，不创建完整 `.py`。

修改已有程序时，先读取目标程序并保持其公共函数、目录结构、变量命名、配置读取和 Excel 写回方式。

新建程序时：

- 优先读取同类现有程序作为母版。
- 没有合适母版时，使用 [assets/business-processing-template.py](assets/business-processing-template.py)。
- 默认沿用 `pandas`、`numpy`、`xlwings`、`configparser`、`get_path()`、`find_files()`、`read()` 和 `df_notnull()` 的公司模式。
- 不新增 `requirements.txt` 外的第三方库；确有必要时，先向用户说明原因并等待确认。
- 数据库读写若要优化公司现有方法，必须先列出优化点、影响范围和兼容性风险，等待用户确认后再修改。
- 对每个输入 DataFrame 明确来源文件、Sheet、字段列表、类型转换与清洗口径。
- 对每个输出 Sheet 明确覆盖、追加、替换当期数据或复制公式/格式的行为。
- 对长数字、前导零、日期、期间、百分比和金额格式进行专项处理。

修改 bug 时，交付说明中必须记录：bug 现象、根因、修改点、影响文件/表、验证方式、后续避免重复发生的注意事项。若同类问题应沉淀到本 skill 或项目 TODO，主动建议沉淀。

涉及数据库 DDL 或建库脚本时，必须遵守：

- 先输出数据库表结构确认稿，等待用户明确“可以生成”后再生成 SQL。
- 如用户或业务要求中文列名，MySQL DDL 必须使用中文列名，并用反引号包裹所有中文列名；表名可使用英文，但确认稿必须写明英文表名对应的中文业务表名。
- 数据库表优先精简，能不建中间表就不建；仅为取数辅助的 SAP 表默认不入库，除非用户确认需要追溯。
- 同一来源且字段高度一致的 SAP 数据可存一张底表，用中文列如 `数据类型` 区分业务用途；Web 可以按 `数据类型` 拆成多个菜单/视图展示。
- 结果表字段优先继承最终输出模板中文字段，不另造字段名；如 SAP 入库前用户已在外部处理成整合大表字段口径，优先按该口径入库。
- 每张业务表如用户要求“序号列”，必须保留中文列 `序号`。
- 导入日志、操作日志和运行状态如已由用户确认需要，必须纳入数据库确认稿；但字段保持精简。
- 数据库读取/写入涉及中文列名时，必须使用安全转义/参数化；任何数据库方法优化必须先给用户确认。

如果用户只提供逻辑说明而未提供样例原始数据或输出模板，可以生成带明确 `TODO` 和待确认清单的程序草稿；说明其未经过真实字段及结果验证。

### 5. 校验与交付

对生成或修改的每份 `.py` 运行：

```bash
python -m py_compile <output.py>
```

资料充足时，再做字段检查、样例结果生成和关键金额/行数/未匹配数据核对。涉及 Excel 输出模板时，验证目标 Sheet 名称、写入位置、保留公式和格式要求。不得声称业务结果正确，除非已经用用户确认过的样例与核对口径完成验证。

交付时列明：

- 已生成或修改的程序文件及执行顺序。
- 每个步骤的输入和输出。
- 已完成的验证。
- 仍需业务人员确认或补给的事项。

## 与 SAP 下载 Skill 配合

需求若同时包含 SAP 下载与后续业务加工，将需求拆成步骤：

1. 使用 `sap-pyautogui-download-builder` 生成或修改 SAP 下载程序。
2. 默认使用其期间选择母版生成或保留 `01-公司期间选择.py`，包括配置写入、`Enter` 提交和数据备份；确认备份目录与重复运行覆盖规则。
3. 使用本 Skill 生成数据处理、匹配、结果回写和报表输出程序。
4. 在程序拆分清单中明确 SAP 导出文件如何作为后续步骤输入。
