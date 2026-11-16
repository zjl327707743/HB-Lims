# ADR-0002：独立LIMS、第三方验证与技术选型重评估

状态：**PROPOSED，未批准、未冻结依赖**。日期：2026-11-16。依据Owner新指示：自研LIMS，第三方提供验证服务；HBOS仅为入口和可选SSO。早期ADR-0001的Django/PostgreSQL是方案，不是已批准架构。

## 1. 固定的独立性边界

LIMS必须拥有自己的独立GitHub代码库、构建和发布版本、域名/反向代理、应用/worker、关系数据库及账户、文件与报告存储、日志审计、签名和资格规则、配置与密钥、环境、备份/恢复及SOP。禁止跨系统共享业务表、通过Frappe会话或数据库直接控制LIMS的质量记录。系统可采用模块化单体：业务模块共享受控事务，Web/API/worker可以分进程部署。

HBOS只做导航链接；可选择统一IdP来完成SSO。LIMS必须拥有直接URL，不经Portal也可访问。IdP需要实际支持的协议：优先验证OIDC授权码/PKCE或SAML，不得把普通OAuth2或Portal登录态直接视作OIDC。LIMS对认证结果做校验，建立自己的会话与角色/厂区/实验室/组/任务范围、资质和职责分离。若HBOS本身承担认证代理，其SSO接口属于关键外部依赖，须纳入风险和接口验证。SSO不能代替具体业务记录的电子签名再鉴别。IdP故障连续性、受控应急访问需经QA/IT批准而非设置免审后门。

## 2. 主要后端候选（工程相对评价，非跑分）

| 框架 | 可取之处 | 不足/实施条件 | 结论 |
| --- | --- | --- | --- |
| FastAPI/Python + Pydantic + SQLAlchemy/Alembic | OpenAPI、强输入模型、接口开发、计算/解析生态；可连MySQL或PostgreSQL | 人员/资质、后台、状态/事务、签名审计与模块规范需要主动建立 | 决赛A |
| Spring Boot/Java + Spring Modulith + JPA/Flyway | 事务、复杂领域、严格模块边界与模块测试，长期交接 | 工程组织成本、Java团队能力 | 决赛B |
| ASP.NET Core .NET10/C# + EF Core | 强类型、工具链、企业身份和数据库生态 | C#与部署维护能力、版本升级管理 | 决赛C |
| Django/DRF | ORM、迁移、Admin、认证与后台效率 | Admin对受控记录的绕过风险；业务权限/审计仍需自建 | 合格备选D |
| NestJS/TypeScript | 同语言、模块/DI、集成测试 | 复杂精密计算和事务/审计约束需统一 | 合格备选E |
| Go Gin/Echo | 轻量运行、适合仪器边缘服务 | 大量业务台账和工作流基建成本 | 不首选核心 |

不允许单靠框架性能排行榜选型。开发者/运维/验证人员实际能力、缺陷暴露、可追溯测试、变更影响和恢复才是关键。三条决赛路线需要用同一套PoC比较，并记录未完成项。

## 3. 数据库候选

| 系统 | 优势 | 需验证 |
| --- | --- | --- |
| MySQL 8.4 LTS/InnoDB | ACID、事务隔离、行锁、备份复制成熟，团队常见；可用 | 应用层数据范围、严格模式、并发约束、迁移与DDL回滚差异 |
| PostgreSQL 17/18 | 丰富约束/类型、JSONB、原生RLS（可作附加防线） | RLS特权绕过、实际DBA/恢复能力，不能当合规认证 |
| SQL Server 2025 | 审计、加密、RLS、微软运维生态 | 授权成本、企业现有DBA与运行环境 |
| Oracle | 企业高级管理生态 | 商业授权、运维人才及退出成本 |
| MongoDB/分布式NewSQL | 特定场景可用 | 结构化检验记录主库初期无明显必要，不默认采用 |

**MySQL和PostgreSQL都不排除。** PostgreSQL技术特性有吸引力；如果企业已有成熟MySQL DBA/恢复体系，MySQL可优先。MySQL原子DDL不等于DDL参与业务事务回滚；两个产品均要单独验证业务审计、签名、备份恢复。不要断言数据库自动满足GMP。

## 4. 前端不必沿用旧技术

React+TypeScript+Ant Design、Vue3+TypeScript+Ant Design Vue、Angular+TypeScript并列候选。React适合丰富企业表格和组件生态；Vue适合易读的模块化页面；Angular适合有成熟团队维护的强约定和复杂表单。看已采用V3.1的界面/操作接受标准，而不锁死其原型HTML实现或HBOS之前使用的前端框架。前端不承担可信身份、签名与最终计算。

## 5. 架构模式与验证负担

初期推荐独立部署的模块化单体，数据事务和批准的记录链便于保持一致；不默认跨服务拆分、Kafka或Kubernetes。微服务需要额外验证分布式事务、事件重放、跨服务签名/审计、故障恢复和组合版本，当前规模没有足够理由。商业/低代码可做TCO参照，不变更已明确的自研目标。

## 6. 用相同真实业务题目做技术PoC

PoC对A/B/C候选使用同一组合成样品与验收阈值：
- 主流程请验→取样/收样→检验→OOS/复测→独立复核→签名→报告归档；新旧标准/方法版本并存；
- 列表/详情/搜索/附件/导出按实验室/岗位/资质范围拒绝，禁止本人复核本人与管理员代签；
- 两人同时扣减试剂、重复签名、状态越序、幂等重试及事务失败回滚；
- 结果修订保留原始值、原因和签署记录，审计与记录关联；报告冻结后可重印但不得覆盖；
- 身份供应方故障、撤销、过期、停用和签名再鉴别；Portal不可用时独立URL表现；
- 受控数据库迁移、备份恢复、文件/数据库一致性及原始数据可追溯；
- 用确认的数据量与并发测试URS-103/104，不以“报表已入队”代替生成完成；
- 固定代码SHA、制品摘要、配置和依赖清单，生成可交给第三方的设计/测试/证据链。

结论评定主要按：风险与正确性、工程与验证证据复现成本、人才与运维、接口/SSO、授权与长期升级总成本。禁止用编造跑分/“天然合规”定胜负。

## 7. 自研/验证分工

公司QC/QA/Owner批准预期用途、风险接受、URS和最终使用；研发提供设计、代码、可重复构建、开发测试及缺陷整改；第三方按合同设计/执行/见证风险驱动的验证并交付独立记录与偏差报告；IT负责环境资格、恢复及运行SOP。第三方不得擅自改受控代码或替企业完成最终质量批准。固定验证版本必须含commit、容器摘要、数据库迁移、配置与依赖。真实验证证据存公司受控系统，公共仓库只存脱敏摘要及引用。

另见 [第三方验证工作模式](../../validation/external-validation-operating-model.md) 与 [HBOS集成边界](../hbos-lims-trust-boundary.md)。

## 待Owner/QA审定

技术负责人技能与可维护能力、前端框架、FastAPI/Spring/.NET实测结论、MySQL/PG DBA能力、身份供应方协议和电子签名策略、URS主体补充、实际负载、仪器、合同验证范围、保留期及RPO/RTO。当前没有冻结选型，也没有部署应用。

## 可核查官方依据

- https://fastapi.tiangolo.com/features/ ; https://fastapi.tiangolo.com/tutorial/sql-databases/
- https://docs.djangoproject.com/en/5.2/topics/auth/ ; https://spring.io/projects/spring-modulith/
- https://dotnet.microsoft.com/en-us/platform/support/policy ; https://docs.nestjs.com/fundamentals/testing
- https://dev.mysql.com/doc/refman/8.4/en/mysql-acid.html ; https://dev.mysql.com/doc/refman/8.4/en/atomic-ddl.html
- https://www.postgresql.org/docs/current/ddl-rowsecurity.html ; https://www.postgresql.org/support/versioning/
- https://openid.net/specs/openid-connect-core-1_0.html
- https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11
- https://health.ec.europa.eu/medicinal-products/eudralex/eudralex-volume-4_en
- https://www.fda.gov/regulatory-information/search-fda-guidance-documents/data-integrity-and-compliance-drug-cgmp-questions-and-answers
