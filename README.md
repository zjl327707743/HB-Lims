# HB-Lims

新乡海滨 LIMS 独立开发仓库。当前为**技术规范与治理阶段**，尚无正式业务应用、未部署、未完成第三方验证。

## 团队现在从这里开始

[技术规范 V1.0](docs/standards/README.md) 是唯一当前工程入口；[前端规范 V2](docs/LIMS独立前端开发规范.md) 已在原路径更新，保留V3.1视觉和业务交互。旧ADR/RFC仅为历史研究，不再据其同时选择多个框架。

本轮方向：Next.js App Router / React / TypeScript / Ant Design / TanStack Query / nuqs；FastAPI / SQLAlchemy 2.0 / Alembic / PostgreSQL；Celery / Redis；Docker Compose / Nginx / GitHub Actions。图表统一Recharts，Zod/Zustand按需。HBOS仅入口或受控SSO，不共享质量数据与发布节奏。

S3接口采用，但**生产存储产品待准入**，社区MinIO不作为默认生产选择。精确版本锁、容量、身份签署策略、质量适用规则和恢复目标仍需证据与批准。规范落库不代表兼容测试或GMP验证已通过。

## 原始依据与变化

[URS](docs/六车间QC实验室信息管理系统用户需求说明.docx) 与 [V3.1 ZIP](LIMS_V3.1_已采用交付包.zip) 字节不变。旧前端规范原字节归档至 [V1](docs/archive/frontend/LIMS独立前端开发规范.v1.20261116.md)，当前原路径为V2；见 [变更记录](docs/governance/changes/CHANGE-20261116-TECH-V1.md) 和 [源清单](docs/sources/README.md)。185条正式业务仍默认NOT_IMPLEMENTED / NOT_RUN。

## 项目分区

| 路径 | 职责 |
| --- | --- |
| apps/web | Next前端及薄BFF |
| apps/api/modules | FastAPI各业务域 |
| apps/worker | Celery后台任务，不另造质量规则 |
| packages/contracts | OpenAPI、命令、状态、错误和生成客户端合同 |
| packages/ui | 被证实复用的组件与V3.1主题 |
| docs/standards | 当前团队技术规范 |
| docs/requirements | 原URS索引、状态、待决项 |
| docs/validation | 第三方验证策略与受控证据规则 |
| tests | 集成、E2E、安全、性能、视觉与可访问性 |
| deploy | 隔离环境、版本化发布和恢复 |
| scripts/governance | 原件/需求/规范的可执行检查 |

这些分区目前主要是README和规范，不是已实现的服务。

## 当前可运行检查

```sh
python3 scripts/governance/verify_sources.py
python3 scripts/governance/check_repository.py
python3 scripts/governance/check_technical_baseline.py
python3 -m unittest discover -s scripts/governance -p 'test_*.py' -v
```

只验证仓库材料与规范一致性，不验证业务正确性、浏览器像素、安全或合规。详见 [团队入口](docs/START_HERE.md)、[CONTRIBUTING](CONTRIBUTING.md)、[AGENTS](AGENTS.md)、[实施路线](docs/delivery/ROADMAP.md)。

公共仓库只允许合成数据与获授权材料。成员/独立评审/main保护待Issue #3落实；不新增整体开源许可，不推断已开启分支保护，不自动生产部署。
