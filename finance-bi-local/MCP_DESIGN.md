# MCP 数据读取设计草案

目标：让 Codex 只能读取你允许开放的数据，并且默认读取汇总结果，不暴露全量明细。

## 推荐能力

- `list_sources()`：列出允许访问的数据源。
- `get_schema(source)`：返回允许表和字段说明。
- `run_named_query(name, params)`：运行预设只读查询。
- `preview_dataset(dataset_id, limit)`：预览少量脱敏数据。
- `export_aggregate(dataset_id, dimensions, metrics, filters)`：导出汇总数据给报告生成器。

## 安全限制

- 只读账号。
- 白名单库、表、字段。
- 默认禁止返回原始金额，金额在服务端先转成指数、占比或汇总。
- 客户、供应商、员工、项目名在服务端先脱敏。
- 禁止 `INSERT`、`UPDATE`、`DELETE`、`DROP`、`ALTER`。
- 禁止无条件全表扫描和无限制导出。
- 所有查询写日志：时间、数据源、字段、行数、调用人。

## 第一阶段不做

- 不直接接生产库。
- 不开放任意 SQL。
- 不把数据库凭据写入 Skill 或报告项目。
