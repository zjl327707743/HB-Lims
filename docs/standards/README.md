# HB-Lims 团队技术规范 V1.0

状态：**DEVELOPMENT_BASELINE_FOR_REVIEW**。依据Owner于2026-11-16 07:18:31 UTC提出的技术方向及修改规范授权编制；代码审查、QA批准、依赖兼容测试及生产验证尚未完成。本文是开发规范，不是已通过验证的产品声明。

## 一、当前唯一实施入口

| 文档 | 内容 |
| --- | --- |
| [技术栈与架构](TECH_STACK.md) | 固定主技术路线、模块化单体、HBOS边界、版本策略 |
| [原路径前端规范 V2](../LIMS独立前端开发规范.md) | 保留V3.1外观/业务/验收条款，更新技术实施要求 |
| [前端工程规范](FRONTEND.md) | Next/AntD、缓存、表单/表格、URL、视觉回归 |
| [后端与数据规范](BACKEND_DATA.md) | FastAPI/SQLAlchemy/PG、命令、事务、版本及计算 |
| [身份、签名与审计](SECURITY_SIGNATURE.md) | 登录/授权/签名区别、隔离和拒绝路径 |
| [存储、队列与恢复](STORAGE_TASKS.md) | S3准入、MinIO风险、Celery、Redis与恢复 |
| [交付和验证门禁](DELIVERY_VALIDATION.md) | 开发顺序、CI、环境、第三方验证证据 |
| [外部依据](SOURCES.md) | 官方来源、查阅日期、结论边界 |
| [本轮变更记录](../governance/changes/CHANGE-20261116-TECH-V1.md) | 旧版存档、权威关系、未决事项及回退 |

规则层级：URS及批准补充决定业务；V3.1 ZIP决定已采用视觉与交互；本规范决定工程实现。技术文件不得删除或暗改URS。原URI保留的前端规范V2和本目录相互引用，旧ADR/RFC仅用于历史比较，不再要求并行实现多框架。

## 二、主选项与限制

采用 Next.js App Router + React + TypeScript、Ant Design及Registry、TanStack Query、AntD Form/Table、nuqs；Zod/Zustand按需；图表统一Recharts。后端采用FastAPI、SQLAlchemy 2.0、Alembic、PostgreSQL；任务采用Celery；Redis仅作短期状态/缓存/消息设施。部署使用Docker Compose和Nginx，CI使用GitHub Actions。没有引入Vue、Django、SQLModel、ARQ或第二套UI作为默认实现。

S3兼容接口采用；**生产存储产品尚未准入，MinIO社区版不再作为默认生产选型**。依赖精确版本、身份提供方、签名再鉴别策略、保留期/RPO/RTO、容量及QA适用规则仍需专项收口。此处的“采用”只表明本轮开发规范方向，不能解释为软件已运行、依赖已测或已获质量放行。

## 三、可执行的当前检查

```sh
python3 scripts/governance/verify_sources.py
python3 scripts/governance/check_repository.py
python3 scripts/governance/check_technical_baseline.py
python3 -m unittest discover -s scripts/governance -p 'test_*.py' -v
```

这些命令仅检查源文件、需求索引和规范一致性；正式应用、性能、浏览器视觉、签名、恢复及第三方验证均为NOT_RUN。团队不能把治理CI通过当成业务已实现。
