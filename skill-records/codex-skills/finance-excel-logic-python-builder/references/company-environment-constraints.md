# 公司环境与实现约束

## 可用第三方库

公司环境以项目提供的 `requirements.txt` 为准。生成或修改程序时，不新增该清单以外的第三方库；确需新增时，必须先向用户说明用途、替代方案、风险并等待确认。

当前已确认可用的关键库包括：

- Web/界面：`Flask==2.2.2`、`Jinja2`、`Werkzeug`、`click`。
- 数据库：`SQLAlchemy==1.4.46`、`PyMySQL==1.0.3`。
- Excel/表格：`pandas==1.4.3`、`numpy==1.24.4`、`openpyxl==3.0.10`、`XlsxWriter==3.2.0`、`xlwings==0.27.13`。
- 日期/配置/常用：`python-dateutil==2.8.2`、`configparser` 属于内置库。
- 自动化/SAP/GUI：`PyAutoGUI`、`pywin32`、`DrissionPage` 等已在公司清单中，但 SAP 下载逻辑优先遵守项目给定母版和 `sap-pyautogui-download-builder`。
- PDF/OCR：`pdfplumber`、`pdfminer.six`、`PyMuPDF`、`PyPDF2`、`pypdfium2`、`pytesseract` 等在清单中。

## Excel 读取约束

公司文件常有加密或受保护场景。默认读取 Excel 使用公司母版的 `xlwings` + `read()` 函数，不优先使用 `openpyxl` 直接读取业务文件，除非：

- 只是在分析非加密逻辑说明文件；
- 用户明确允许；
- 或 `xlwings` 不适合当前任务并已向用户说明。

参考母版：桌面 `03-跟进汇总表生成-预付未开票.py`。其中保留以下公司习惯：

- `app = xw.App(visible=True, add_book=False)` 后用 `app.books.open(path, update_links=False)` 打开。
- 只读取可见 Sheet：`[s for s in wb.sheets if s.api.Visible == -1]`。
- 读取前取消筛选和隐藏列：`sheet.api.AutoFilterMode = False`，并取消指定范围隐藏列。
- `read(path, sht_num_name=0, row=0, col_list=0)` 负责表头行、列校验、空表处理和关闭 workbook。
- `df_notnull()` 用于清理空值和编号字符，但会去前导零；对客户代码、供应商、物料号、凭证号等字段要先确认是否允许去零。

## 数据库读写约束

公司当前推荐模式来自 `数据库操作.txt`：

- 用 `configparser` 读取共享 `parameter.ini`。
- 用 `decode_b64_in_url()` 解码连接串中的 `${B64:...}` 密码。
- 用 `SQLAlchemy create_engine()` 创建 MySQL engine。
- 读取时优先使用 `sqlalchemy.text()` + 参数化查询 + `pd.read_sql()`，避免直接拼接用户输入。
- 大数据可用 `chunksize` 分块读取。
- 写入时已有 `replace_data_by_condition()` 模式：按条件批量删除旧数据，再 `to_sql(if_exists="append")` 插入。

如果需要优化数据库读写方法，必须先向用户列出：

- 现有方法的问题；
- 拟优化方式；
- 对历史程序兼容性的影响；
- 是否会改变删除/覆盖/追加口径；
- 回滚方案。

未经用户确认，不擅自替换公司数据库公共方法。

本地实验版或界面原型存在例外：如果用户已经在目标机器上证明 `pymysql.connect(...)` 直连成功，且共享 `parameter.ini` 路径会卡住或不可用，可以在用户确认后优先使用直连配置。此时不要在启动或登录路径中先探测共享盘；如保留共享路径检测，必须用 `try/except OSError` 包裹，避免 Windows 网络名不可用导致程序卡死。

数据库结构、示例数据和程序写入逻辑必须同步维护。任何表字段口径变化后，检查清单至少包括：DDL 字段、唯一键、示例 `INSERT`、Python 写库列、界面展示列、界面编辑列、查询筛选列。若目标库已经创建过旧表，必须明确提示 `CREATE TABLE IF NOT EXISTS` 不会改旧结构，并按需提供单独迁移 SQL。

## 数据查看/编辑界面约束

当财务项目生成 Web、Tkinter 或 PyQt 数据界面时：

- 结果表允许人工修改前，必须确认唯一定位列，如中文 `序号`。
- 默认采用“编辑后统一保存”的模式：双击修改、修改单元格高亮、保存前确认、可撤销未保存修改。
- 保存时按唯一定位列写回，并尽量写入 `operation_log`。
- 配置表默认只读；如业务需要停用，优先做按钮化停用/恢复，而不是让业务直接编辑状态列。
- 可编辑表筛选候选值必须合并数据库候选值与当前界面模型值，保证未保存修改也能被筛选；保存成功后清理相关缓存。
- 业务人员界面应贴近 Excel 心智模型，筛选入口应与列名强关联，避免单独筛选栏与表格列错位。
- 数据查询界面的列筛选默认应支持多选候选值；若还提供输入搜索，需同时保留清空筛选、切换表后重置或继承默认筛选的明确行为。
- PyQt 界面若可能在 Spyder/Jupyter/RPA 宿主中重复运行，启动段优先使用 `QApplication.instance() or QApplication(sys.argv)`，窗口引用挂到 `app` 上防止被回收；不要默认 `sys.exit(app.exec_())` 结束宿主进程，可用 `QEventLoop` 等局部事件循环在窗口关闭后清理引用。

## Bug 修复复盘

每次用户要求“修改 bug”“报错修复”“结果不对”时，交付必须记录：

- bug 现象；
- 根因；
- 修改点；
- 影响文件、数据库表或输出 Sheet；
- 已做验证；
- 是否需要沉淀为 skill 规则或项目注意事项。

如果同类 bug 可能重复出现，主动建议把规则补进 skill 或项目 README/TODO，但不要擅自新增杂乱文档。
