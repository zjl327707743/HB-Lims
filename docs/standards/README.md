# HB-Lims 团队规范 V1.1：整体开发框架

**FRAMEWORK-V1 / OWNER_ACCEPTED_PLANNING_BASELINE。** Owner于2026-11-16T10:13:30Z认可前轮扩展规划并授权整合PR #1。技术主线、14项控制与小团队方法已收敛；PR审查/合并、QA批准、精确版本准入、应用验证和生产发布尚未完成。不要把“规范定下来”理解成这些事项已通过。

## 一、团队唯一入口

首先阅读[整体基线](FRAMEWORK_BASELINE.md)，再按岗位阅读下表。TECH-V1仍是技术组件基线，FRAMEWORK-V1在其上纳入已认可的控制和交付规则；历史研究不再作为并列实现方案。

| 分区 | 规范 |
| --- | --- |
| 技术基础 | [技术栈](TECH_STACK.md)、[前端V2](../LIMS独立前端开发规范.md)、[前端工程](FRONTEND.md)、[后端数据](BACKEND_DATA.md) |
| 公共控制 | [身份签名](SECURITY_SIGNATURE.md)、[存储队列](STORAGE_TASKS.md)、[交付门禁](DELIVERY_VALIDATION.md) |
| 扩展控制1 | [法规/记录主本](REGULATORY_SCOPE.md)、[原始记录/审计复核](RECORDS_AUDIT.md) |
| 扩展控制2 | [LES/配置/计算/异常](LES_CONFIG_CALC.md)、[报告/采集/接口](REPORTS_INTEGRATIONS.md) |
| 扩展控制3 | [恢复/运行/退役](RECOVERY_OPERATIONS.md)、[验证证据](VALIDATION_EVIDENCE.md) |
| 范围与登记 | [28项功能映射](../requirements/FUNCTION_SCOPE.md)、[14控制/8技术登记](controls.json)、[技术增补准入](EXTENSIONS.md)、[待决事项](../requirements/decisions.md) |
| 团队执行 | [开发手册](../delivery/TEAM_PLAYBOOK.md)、[前四周](../delivery/FIRST_FOUR_WEEKS.md)、[任务依赖](../delivery/backlog.json)、[路线/周期](../delivery/ROADMAP.md) |
| 模板与追溯 | [任务](../templates/TASK_BRIEF.md)、[交接](../templates/HANDOFF.md)、[证据](../templates/VALIDATION_EVIDENCE.json)、[发布清单](../templates/RELEASE_MANIFEST.json) |
| 来源与变更 | [技术依据](SOURCES.md)、[输入登记](../sources/PLANNING_INPUTS.md)、[TECH-V1变更](../governance/changes/CHANGE-20261116-TECH-V1.md)、[FRAMEWORK-V1变更](../governance/changes/CHANGE-20261116-FRAMEWORK-V1.md) |

## 二、不会再次摇摆的主路线

Next.js/React/TypeScript、AntD/Registry、TanStack Query、AntD Form/Table、nuqs、Recharts；Zod/Zustand按需。FastAPI/Pydantic、SQLAlchemy 2.0、Alembic、PostgreSQL；Celery/Redis；S3接口；Docker Compose/Nginx/GitHub Actions。独立LIMS模块化单体；HBOS仅入口或受控SSO。

14项控制纳入开发；8项增补区分工具方向、PoC准入和按需专项，不是所有库全部必装。具体产品/版本、许可证、身份/签署、保留/RPO/RTO和QA适用性仍需证据。S3生产产品仍待准入。V3.1品牌、玻璃顶栏、圆角侧栏、紫色主操作、报告和业务交互不因本轮改变。

## 三、可执行的治理检查

```sh
python3 scripts/governance/verify_sources.py
python3 scripts/governance/check_repository.py
python3 scripts/governance/check_technical_baseline.py
python3 scripts/governance/check_framework.py
python3 scripts/governance/estimate_delivery.py
python3 -m unittest discover -s scripts/governance -p 'test_*.py' -v
```

只验证原件/索引/规范/规划结构，不验证LIMS业务、视觉像素、安全、性能、恢复或GMP符合性。原185条RTM仍默认NOT_IMPLEMENTED/NOT_RUN。模板、计划和源码审阅不能替代实际证据与QA放行。
