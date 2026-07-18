# Recorded Python Bug Cases

## pybug-20260607-shared-parameterini-path-blocks-local-web

```yaml
bug_entry:
  id: "pybug-20260607-shared-parameterini-path-blocks-local-web"
  status: "recorded"
  language: "python"
  title: "Windows local web app hangs after login because code probes unavailable shared parameter.ini"
  severity: "high"
  source:
    task_summary: "采购大表本地 Web 展示页面登录后长时间加载，最终报 WinError 64。"
    user_reported: true
    environment: "Windows company PC, local Flask app, MySQL available on 127.0.0.1"
    command_or_action: "User logged in to local web UI after independently proving pymysql.connect succeeded."
  symptom:
    error_type: "OSError"
    message: "[WinError 64] 指定的网络名不再可用"
    traceback_summary: "Path(PARAMETER_INI).exists() attempted to access \\\\192.168...\\parameter.ini before using the already-working local DB settings."
    wrong_output_summary: "Login page appeared to hang even though direct PyMySQL database connection succeeded."
  root_cause:
    category: "environment"
    explanation: "The app prioritized or probed a shared network parameter.ini path. On a company Windows machine the share was unavailable, so the path existence check blocked/failed before the app could use the verified local MySQL connection."
  decomposition_link:
    caused_by: "environment_assumption"
    explanation: "The database connection layer assumed shared configuration was reachable during local testing, instead of using the user-verified connection method first."
  fix:
    changed_files:
      - "purchase_big_table_web.py"
    fix_summary: "Removed shared parameter.ini probing from the experimental local version and switched to direct PyMySQL connection parameters matching the user's successful test."
    prevention_rule: "For local experiment scripts in restricted company environments, prefer the user-verified DB connection method first. If shared parameter.ini probing is retained, make it optional and wrap network path checks in try/except OSError."
  validation:
    commands:
      - "python -m py_compile purchase_big_table_web.py"
    evidence: "After switching to direct PyMySQL, the user confirmed the web page could open."
  skill_updates:
    should_update_other_skills: true
    targets:
      - skill: "finance-excel-logic-python-builder"
        proposed_rule: "Local DB/UI prototypes should not block on shared parameter.ini; direct verified DB settings may be used when the user confirms company environment constraints."
  tags:
    - "database"
    - "environment"
    - "network-share"
    - "flask"
```

## pybug-20260607-editable-table-filter-cache-misses-unsaved-values

```yaml
bug_entry:
  id: "pybug-20260607-editable-table-filter-cache-misses-unsaved-values"
  status: "recorded"
  language: "python"
  title: "Editable PyQt table filter options miss newly edited unsaved cell values"
  severity: "medium"
  source:
    task_summary: "采购大表 PyQt5 界面中，结果表可双击修改，但筛选菜单仍只显示数据库旧值。"
    user_reported: true
    environment: "PyQt5 desktop UI, pandas DataFrame model, MySQL-backed result tables"
    command_or_action: "User changed 公司代码 from 1100 to 1200, then opened the column filter menu."
  symptom:
    error_type: "wrong_output"
    message: "筛选框没有那个修改后的筛选"
    traceback_summary: ""
    wrong_output_summary: "Filter candidates still showed only 1100 and did not include the edited value 1200."
  root_cause:
    category: "dataframe"
    explanation: "Filter candidates came from cached database DISTINCT values only. The UI model contained unsaved edited values, but get_options did not merge values from the current DataFrame model."
  decomposition_link:
    caused_by: "missing_validation"
    explanation: "Editable-table validation checked edit/save behavior but did not test whether filters reflect unsaved in-memory edits."
  fix:
    changed_files:
      - "purchase_big_table_pyqt5.py"
    fix_summary: "Changed filter option generation to merge database cached options with current model DataFrame values; cleared the current table option cache after successful save."
    prevention_rule: "For editable DataFrame-backed UI tables, filter option lists must include current in-memory model values in addition to database/cache values, and table-specific option caches must be cleared after save."
  validation:
    commands:
      - "python -m py_compile purchase_big_table_pyqt5.py"
    evidence: "The code path now extends cached values with model.df[column] values and clears option cache after save."
  skill_updates:
    should_update_other_skills: true
    targets:
      - skill: "finance-excel-logic-python-builder"
        proposed_rule: "Generated finance data editing UIs must validate filter behavior after unsaved edits and after save."
  tags:
    - "pyqt5"
    - "dataframe"
    - "filter-cache"
    - "editable-ui"
```

## pybug-20260718-pyqt-menu-calls-missing-method

```yaml
bug_entry:
  id: "pybug-20260718-pyqt-menu-calls-missing-method"
  status: "recorded"
  language: "python"
  title: "PyQt menu action bound to missing method passes py_compile but fails at runtime"
  severity: "high"
  source:
    task_summary: "采购大表查询界面启动时报 AttributeError: PurchaseMainWindow object has no attribute select_columns。"
    user_reported: true
    environment: "PyQt5 desktop UI, Jupyter/Spyder-style execution"
    command_or_action: "window = PurchaseMainWindow()"
  symptom:
    error_type: "AttributeError"
    message: "'PurchaseMainWindow' object has no attribute 'select_columns'"
    traceback_summary: "build_action_menus() used view_menu.addAction('选择显示列', self.select_columns) but class did not define select_columns."
    wrong_output_summary: "界面无法启动。"
  root_cause:
    category: "logic"
    explanation: "UI 菜单 wiring 没有做实例化级别验证；py_compile 只能检查语法，不能发现缺方法绑定。"
  decomposition_link:
    caused_by: "missing_validation"
    explanation: "修改 PyQt UI 后只做语法检查，没有实例化窗口或搜索 QAction 回调是否存在。"
  fix:
    changed_files:
      - "08-采购大表查询.py"
    fix_summary: "补齐/对齐选择显示列方法并复用已有 CheckableListWidget 交互。"
    prevention_rule: "PyQt UI 修改后除 py_compile 外，应至少实例化主窗口或静态检查所有 self.xxx 回调方法是否存在。"
  validation:
    commands:
      - "python -m py_compile 08-采购大表查询.py"
    evidence: "后续启动错误消失，用户继续验证 UI 交互。"
  skill_updates:
    should_update_other_skills: true
    targets:
      - skill: "finance-excel-logic-python-builder"
        proposed_rule: "生成/修改 PyQt 数据界面时，验证 QAction/button signal 绑定的方法存在。"
  tags:
    - "pyqt5"
    - "ui"
    - "runtime-validation"
```

## pybug-20260718-excelwriter-rebuilds-sap-export

```yaml
bug_entry:
  id: "pybug-20260718-excelwriter-rebuilds-sap-export"
  status: "recorded"
  language: "python"
  title: "pandas ExcelWriter mode=w rebuilds SAP export workbook and loses workbook structure"
  severity: "high"
  source:
    task_summary: "SAP 非订单采购主体文件需要回写供应商和物料描述，旧代码用 pandas ExcelWriter mode='w' 整体重写。"
    user_reported: true
    environment: "SAP-exported Excel files, xlwings/pandas automation"
    command_or_action: "postprocess_non_po_supplier_temp() and fill_non_po_material_desc_from_text()"
  symptom:
    error_type: "wrong_output"
    message: ""
    traceback_summary: ""
    wrong_output_summary: "工作表名称可能变为 Sheet1，格式、列宽、筛选、隐藏内容和日期/编码格式可能丢失。"
  root_cause:
    category: "excel"
    explanation: "用 DataFrame 整体重建工作簿处理少量单元格回写，破坏了 SAP 原始 workbook 结构。"
  decomposition_link:
    caused_by: "unclear_boundary"
    explanation: "数据清洗和原始 SAP 文件格式保留边界没有分清。"
  fix:
    changed_files:
      - "02-SAP数据下载.py"
    fix_summary: "改为 xlwings 打开原 workbook，按表头定位列，只定点回写需要补充的单元格。"
    prevention_rule: "需要保留 SAP 导出原格式时，优先 xlwings 单元格回写；不要用 ExcelWriter mode='w' 重建整个文件。"
  validation:
    commands:
      - "python -m py_compile 02-SAP数据下载.py"
    evidence: "代码路径不再调用 pandas ExcelWriter 重写原文件。"
  skill_updates:
    should_update_other_skills: true
    targets:
      - skill: "sap-pyautogui-download-builder"
        proposed_rule: "SAP 下载后处理需要保留 workbook 结构时使用 xlwings 定点回写。"
  tags:
    - "excel"
    - "sap-export"
    - "xlwings"
    - "format-preservation"
```
