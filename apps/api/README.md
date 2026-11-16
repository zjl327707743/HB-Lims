# LIMS API 开发分区

采用FastAPI + Pydantic、SQLAlchemy 2.0、Alembic及PostgreSQL；见 [BE-V1](../../docs/standards/BACKEND_DATA.md) 和 [SEC-V1](../../docs/standards/SECURITY_SIGNATURE.md)。Django/Java/.NET/SQLModel仅保留历史研究，不作为同时实施路线。

modules保持既有业务责任域，每域以router/schema/service/repository/models/tests分层。明确命令控制身份、资质、范围、状态、版本与事务，不允许PATCH status绕过审核。

每请求/任务独立AsyncSession，结果/签名/审计/Outbox原子提交；复杂计算用Decimal、版本规则和金标准。实际PG集成、并发、迁移及恢复是交付要求。本轮没有API代码或数据库环境，不宣称能力已实现。
