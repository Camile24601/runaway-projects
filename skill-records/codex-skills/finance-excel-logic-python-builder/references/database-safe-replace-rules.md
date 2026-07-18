# 数据库覆盖更新安全规则

适用场景：财务脚本需要先删除旧数据，再插入本次新数据，例如 SAP 来源表、维护表、过程表、结果表的按期间/公司/单据覆盖更新。

## 核心原则

覆盖更新的删除范围必须来自本次新数据的实际业务粒度，而不是用户选择范围、文件名前缀、界面筛选条件或某几个字段的笛卡尔积。

删除和插入必须处于同一个可回滚事务中；如果插入失败，删除必须能够回滚。

## 修改前必查

1. 确认目标表的一行代表什么业务粒度，例如：
   - `期间 + 公司 + 数据类型`
   - `期间 + 采购组织 + 采购凭证 + 项目`
   - `期间 + 公司 + 供应商 + 物料编码`
2. 确认 Python 删除键、DataFrame 去重键、数据库唯一索引、界面编辑 `key_columns` 是否一致。
3. 确认新数据为空时的业务口径：
   - 默认：新数据为空不删除旧数据。
   - 仅当业务明确要求“空结果覆盖旧数据”时，才允许按已确认范围删除。
4. 确认关键字段缺列或为空时是否必须报错。默认必须报错，不允许退回更宽范围删除。
5. 确认是否存在多个来源共用一张表。删除键必须包含能区分来源/数据类型的字段。

## 安全写法

```python
key_cols = ["期间", "公司", "数据类型"]
missing_keys = [col for col in key_cols if col not in data.columns]
if missing_keys:
    raise ValueError(f"新数据缺少关键字段 {missing_keys}，禁止删除数据库旧数据。")

invalid_key_mask = False
for col in key_cols:
    col_invalid = (
        data[col].isna()
        | data[col].astype(str).str.strip().isin(["", "nan", "None", "none", "NaN"])
    )
    invalid_key_mask = invalid_key_mask | col_invalid
if invalid_key_mask.any():
    raise ValueError(f"新数据存在 {int(invalid_key_mask.sum())} 行关键字段为空，禁止删除和入库。")

data = data.drop_duplicates(subset=key_cols, keep="last")

with engine.begin() as conn:
    deleted = delete_existing_by_key(conn, table_name, data, key_cols)
    data.to_sql(name=table_name, con=conn, if_exists="append", index=False, chunksize=5000)
```

## 禁止写法

```python
# 错误：按用户选择范围删除，可能删除没有新数据覆盖的旧数据
for period in selected_periods:
    for company in selected_companies:
        delete(period, company)

# 错误：分别提取期间和公司后做笛卡尔积，可能删除本次不存在的组合
for period in data["期间"].unique():
    for company in data["公司"].unique():
        delete(period, company)

# 错误：关键字段不全时退回宽范围删除
if not all_keys_present:
    delete_by_period_company()

# 错误：DELETE 与 INSERT 之间执行 MySQL DDL，会隐式提交
with engine.begin() as conn:
    delete_old_rows(conn)
    conn.execute(text("ALTER TABLE `table` AUTO_INCREMENT = 1"))
    insert_new_rows(conn)
```

## MySQL 事务注意事项

MySQL 的 `ALTER TABLE`、`TRUNCATE`、`DROP TABLE`、`CREATE TABLE` 等 DDL 会产生隐式提交。覆盖更新事务中禁止穿插这些语句。

自增序号不连续不影响业务。不要为了让序号从 1 开始，在删除旧数据和插入新数据之间执行 `ALTER TABLE ... AUTO_INCREMENT = 1`。

## 索引迁移注意事项

当业务粒度变化时，不要只改 Python。必须同步检查：

- 旧唯一索引是否仍会阻止新粒度多行入库；
- 新唯一索引口径下是否已有重复数据；
- 查询/编辑界面的 `key_columns` 是否仍能唯一定位行；
- 迁移 SQL 是否只调整索引，不删表、不删数据。

推荐 SQL 迁移顺序：

1. 查询新唯一键口径下是否已有重复数据；
2. 删除旧唯一索引；
3. 新增新唯一索引；
4. 查询当前索引确认结果。
