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
