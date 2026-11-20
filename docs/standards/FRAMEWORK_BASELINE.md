# FRAMEWORK-V1：HB-Lims 团队开发整体基线

日期：2026-11-16。Owner于2026-11-16T10:13:30Z认可扩展规划并授权整合至PR #1。

**状态：OWNER_ACCEPTED_PLANNING_BASELINE / PR_REVIEW_PENDING。** 主技术路线、控制要求和分期方法已收敛；PR合并、QA正式批准、精确依赖准入、软件实现和生产发布是不同事件。本文件不替代任何未完成的质量批准。

## 1. 唯一实施依据及冲突处理

1. 原始URS、经批准补充与变更记录确定业务需求；保留185条原编号、定位和类别，不自动将URS-1306改号，不擅自补3项空类别。
2. 新增功能清单保留28个编号项、原始选择值及说明；与URS存在不同范围时登记决策，不静默删除或覆盖任何一方。详见[范围映射](../requirements/FUNCTION_SCOPE.md)。
3. V3.1 ZIP/HTML是已采用视觉与交互基线；当前[前端V2](../LIMS独立前端开发规范.md)及[前端工程规范](FRONTEND.md)负责技术实现。更换技术不重新设计品牌和页面。
4. [TECH-V1](TECH_STACK.md)与本轮六份控制细则共同构成当前工程规则。旧ADR/RFC、上传的NestJS/Vite调研方案只作历史参考，不能同时成为另一实施栈。
5. Owner认可规划，不代表已替QA确定法规适用、签署策略、保存期限、产品放行或验证通过。发现冲突先记录影响；仅阻断相关正式业务/验证，不阻断合成数据环境的工程准备。

## 2. 固定的产品和技术边界

HB-Lims独立代码、构建、运行、域名、数据库/账户、文件、会话、业务权限、签名审计、备份和版本。HBOS只作入口或受控SSO；不共享业务表、Cookie、管理员权限或发布节奏。IdP、企业接口及仪器是明确的外部依赖，不因独立仓库而自动排除验证。

采用Next.js App Router/React/TypeScript、AntD及Registry、TanStack Query、AntD Form/Table、nuqs、Recharts；Zod/Zustand按需。API采用FastAPI/Pydantic、SQLAlchemy 2.0、Alembic、PostgreSQL；Celery和Redis按已定边界使用；S3接口、Docker Compose、Nginx、GitHub Actions。精确补丁、锁文件和镜像摘要由首个工程PR实际验证后锁定。

内部采用模块化单体。Web/API/worker可分进程；不默认引入微服务、Kafka、Kubernetes、另一套ORM或UI。跨域通过显式服务，关键命令在同一PG事务内写业务版本、签名（适用时）、质量审计和Outbox。文件存储采用受控分阶段提交，不假设参加PG事务。

## 3. 本轮纳入的六类控制细则

| 规范 | 覆盖控制ID | 阅读对象 |
| --- | --- | --- |
| [法规适用与记录主本](REGULATORY_SCOPE.md) | C01 | Owner、QC、QA、第三方 |
| [原始记录与审计复核](RECORDS_AUDIT.md) | C02、C03 | 后端、质量域、QA |
| [LES、版本、计算与异常](LES_CONFIG_CALC.md) | C04、C05、C06、C07、C11 | 前后端、QC、QA |
| [报告、仪器和企业接口](REPORTS_INTEGRATIONS.md) | C08、C09、C10 | 集成、报告、IT、QC |
| [恢复、运维和退役](RECOVERY_OPERATIONS.md) | C12、C14 | IT、研发、QA |
| [验证证据](VALIDATION_EVIDENCE.md) | C13 | 全体团队及验证服务商 |

[控制登记](controls.json)保留14项和原需求来源；[技术增补](EXTENSIONS.md)保留8项的不同准入级别。纳入规划不表示所有候选库都已安装或全部需在第一期交付。

## 4. 范围与先后顺序

先做一个实验室、一类样品、3–5个代表方法、2–3种报告和两类代表来源的窄范围试点。具体清单及替代流程仍须QC/QA批准。范围窄不等于控制弱：试点涉及的资质、校准、试剂/溶液/培养基/菌种、异常、签名、审计和原始数据必须完整。

保留功能表中已选完整LES和LIMS内OOS/OOT模式一。QMS结案边界、10/15数量单位、平板与采集代理的含义、DMS/TMS撤权与版本规则列入[待决事项](../requirements/decisions.md)。不把完整OOS默改为只上报，也不默认所有设备均已集成。

## 5. 什么已定、什么没有定

已定：主栈、独立边界、V3.1视觉保留、14项控制纳入、纵向交付及2–3人容量估算方法。

未完成：QA法规适用/主本/签署/保留/RPO/RTO批准；生产S3产品准入；精确依赖与真实兼容测试；成员与分支保护设置；实际应用、视觉、安全、性能、恢复及第三方验证。

本轮全部控制实现为NOT_IMPLEMENTED，业务测试为NOT_RUN；现有RTM不因Owner认可本文件而改为PASS。任何后续状态变更须链接真实实现、测试与批准证据。

## 6. 执行入口

[团队开发手册](../delivery/TEAM_PLAYBOOK.md) → [前四周任务](../delivery/FIRST_FOUR_WEEKS.md) → [依赖化任务表](../delivery/backlog.json) → [阶段与周期](../delivery/ROADMAP.md)。每个任务使用[任务模板](../templates/TASK_BRIEF.md)，每个候选发布使用[发布清单](../templates/RELEASE_MANIFEST.json)。

PR #1用于收口前期规范，不继续塞入业务代码。审查并明确批准合并后，以合并后的main为新代码基线；后续一个受控业务增量一个PR，禁止各团队永久分叉或另建一套签名/审计体系。
