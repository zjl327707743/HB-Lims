# ADR-0003 Next/AntD/FastAPI/PG实施基线

日期2026-11-16。状态DEVELOPMENT_BASELINE_FOR_REVIEW；依据Owner技术方向及修改规范授权，不代表QA/生产批准。替代ADR-0001/0002的开放式技术候选，保留历史。

决定：独立LIMS模块化单体；Next/React/TS/AntD、TanStack Query、Form/Table、nuqs，Recharts；FastAPI、SQLAlchemy 2.0、Alembic、PG；Celery、Redis；S3接口、Nginx、Compose、GitHub Actions。Zod/Zustand按需。

关键修正：Proxy不是授权终点；关键写入不乐观成功；JWT/RBAC补充范围、资质、职责和真实签署；社区MinIO归档及ARQ维护模式影响产品准入；数据库与文件/消息一致性需显式设计。

唯一细则入口 [TECH-V1](../../standards/README.md)，待决与证据见 [变更记录](../../governance/changes/CHANGE-20261116-TECH-V1.md)。没有安装依赖、应用代码、正式验证或生产部署。替代供应商不自动采购，精确版本和存储产品未锁定。
