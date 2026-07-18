# Recorded SQL Bug Cases

## sqlbug-20260718-me2l-po-item-grain-loss

```yaml
bug_entry:
  id: "sqlbug-20260718-me2l-po-item-grain-loss"
  status: "recorded"
  language: "sql"
  title: "ME2L purchase order items collapsed by too-wide unique/delete key"
  severity: "critical"
  issue_mode: "silent_wrong_result"
  source:
    task_summary: "采购大表 03 数据库导入中，ME2L 在 load_me2l 已按期间+采购组织+采购凭证+项目去重后，又在入库替换函数中按期间+采购凭证二次去重。"
    database_or_engine: "MySQL / SQLAlchemy pandas to_sql"
    query_or_model: "CS019_me2l_purchase_order"
    user_reported: true
  symptom:
    error_message: ""
    wrong_result_summary: "同一采购凭证多个行项目只保留最后一行。"
    expected_result: "202606/1100/5100001818/10、20、30 三个项目均应保留。"
    observed_result: "入库前被 drop_duplicates(['期间','采购凭证']) 压缩成一行。"
  root_cause:
    category: "schema_drift"
    explanation: "Python 入库删除键和数据库唯一索引粒度落后于业务粒度，没有包含采购组织和项目。"
  decomposition_link:
    caused_by: "missing_grain_check"
    explanation: "修改入库覆盖逻辑时没有同步核对表的一行粒度、DataFrame 去重键和数据库唯一索引。"
  fix:
    fix_summary: "ME2L 删除/去重键改为期间+采购组织+采购凭证+项目，并提供不删表的唯一索引迁移 SQL。"
    safer_query_pattern: "覆盖更新前先确认业务粒度，并让删除键、唯一索引、界面 key_columns 一致。"
    prevention_rule: "采购订单类明细表不得只按单号去重；若存在行项目，唯一键必须包含项目字段。"
  validation:
    checks:
      - "grain_check"
      - "distinct_key_count"
      - "schema_drift_check"
    evidence: "代码搜索确认旧 key_cols=['期间','采购凭证'] 被替换为 ['期间','采购组织','采购凭证','项目']。"
  tags:
    - "silent-data-loss"
    - "unique-key"
    - "grain"
    - "me2l"
```

## sqlbug-20260718-mysql-ddl-breaks-delete-insert-rollback

```yaml
bug_entry:
  id: "sqlbug-20260718-mysql-ddl-breaks-delete-insert-rollback"
  status: "recorded"
  language: "sql"
  title: "ALTER TABLE AUTO_INCREMENT inside replace transaction commits DELETE before INSERT"
  severity: "critical"
  issue_mode: "transaction"
  source:
    task_summary: "采购大表 03 数据库导入中，DELETE 旧数据和 to_sql 插入之间调用 reset_auto_increment_if_empty，内部可能执行 ALTER TABLE AUTO_INCREMENT。"
    database_or_engine: "MySQL"
    query_or_model: "DELETE + ALTER TABLE + pandas to_sql"
    user_reported: true
  symptom:
    error_message: ""
    wrong_result_summary: "如果 INSERT 失败，DELETE 可能已经被 ALTER TABLE 隐式提交，旧数据无法回滚。"
    expected_result: "删除和插入在同一可回滚事务中，插入失败时删除回滚。"
    observed_result: "ALTER TABLE 破坏事务边界。"
  root_cause:
    category: "transaction"
    explanation: "MySQL DDL 会隐式提交，不能放在覆盖更新事务中。"
  decomposition_link:
    caused_by: "review_gap"
    explanation: "代码审查只关注自增序号重置，没有检查 DDL 对事务回滚的影响。"
  fix:
    fix_summary: "删除 reset_auto_increment_if_empty 调用和函数，覆盖更新事务中不再执行 ALTER TABLE。"
    safer_query_pattern: "DELETE 和 INSERT 之间只允许 DML 和参数化查询，不允许 DDL。"
    prevention_rule: "自增序号不连续不影响业务；禁止为了重置序号破坏可回滚事务。"
  validation:
    checks:
      - "transaction_boundary_check"
      - "schema_drift_check"
    evidence: "全文搜索 reset_auto_increment_if_empty|AUTO_INCREMENT|ALTER TABLE 无残留。"
  tags:
    - "mysql"
    - "transaction"
    - "implicit-commit"
    - "data-loss-risk"
```
