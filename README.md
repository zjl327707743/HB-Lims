# HB-Lims

新乡海滨LIMS独立开发仓库。当前交付为**团队开发整体框架**，不是已运行或已验证的业务系统。

## 团队从这里开始

[团队规范V1.1](docs/standards/README.md) → [整体基线](docs/standards/FRAMEWORK_BASELINE.md) → [开发手册](docs/delivery/TEAM_PLAYBOOK.md) → [前四周任务](docs/delivery/FIRST_FOUR_WEEKS.md)。

Owner已认可主技术路线、14项控制增补及2–3人分期方法。PR审查与合并、QA正式批准、依赖精确锁定、生产存储准入、应用实现和验证仍是独立门禁；不由规划认可自动完成。

采用Next/React/TypeScript/AntD、TanStack Query、nuqs、Recharts；FastAPI/SQLAlchemy 2.0/Alembic/PostgreSQL；Celery/Redis；S3接口；Compose/Nginx/GitHub Actions。独立LIMS，HBOS只入口/受控SSO，不共享业务库、质量权限或发布节奏。

[前端V2](docs/LIMS独立前端开发规范.md)保留V3.1视觉与操作，旧版原字节[归档](docs/archive/frontend/LIMS独立前端开发规范.v1.20261116.md)。[URS原件](docs/六车间QC实验室信息管理系统用户需求说明.docx)和[V3.1包](LIMS_V3.1_已采用交付包.zip)未改变；185条原编号保持。[28项功能范围](docs/requirements/FUNCTION_SCOPE.md)、[14控制/8技术登记](docs/standards/controls.json)和[周期模型](docs/delivery/ROADMAP.md)已经归入统一规划。

## 工程分区

| 路径 | 责任 |
| --- | --- |
| apps/web | Next Web与薄BFF、V3.1主题与交互 |
| apps/api/modules | FastAPI领域服务；统一权限/版本/事务/签名/审计 |
| apps/worker | 后台报告/采集处理/通知，不另造质量规则 |
| packages/contracts / packages/ui | 受控OpenAPI和经确认的共用组件 |
| docs/standards / docs/requirements | 规范、控制、范围、URS和待决事项 |
| docs/delivery / docs/templates | 路线、依赖、团队流程和交付模板 |
| tests / deploy | 正式实现后的测试与隔离运行配置 |
| scripts/governance | 当前可执行的资料/规划检查 |

这些分区仍以规范和README为主，没有把目录当成已实现应用。

## 当前可执行检查

```sh
python3 scripts/governance/verify_sources.py
python3 scripts/governance/check_repository.py
python3 scripts/governance/check_technical_baseline.py
python3 scripts/governance/check_framework.py
python3 scripts/governance/estimate_delivery.py
python3 -m unittest discover -s scripts/governance -p 'test_*.py' -v
```

治理通过不等于业务或GMP通过。正式测试仍NOT_RUN；不新增空成功Job。原始证据/正式批准存公司受控系统，公共仓库只存合成样例和脱敏引用。

先核实[GitHub保护与人员清单](docs/governance/github-settings-checklist.md)，不把CODEOWNERS文件当成保护已生效。参阅[CONTRIBUTING](CONTRIBUTING.md)、[AGENTS](AGENTS.md)、[输入来源](docs/sources/PLANNING_INPUTS.md)和[本轮变更](docs/governance/changes/CHANGE-20261116-FRAMEWORK-V1.md)。
