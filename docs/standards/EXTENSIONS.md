# EXT-V1 已纳入规划的8项技术增补

Owner认可规划；不等于组件已安装、精确版本已锁或生产能力已获准。主栈维持[TECH-V1](TECH_STACK.md)，V3.1风格不变。以下级别解决此前“全部候选”与“全部必装”的混淆。

| ID | 方向 | 本轮地位 | 时点与准入证据 |
| --- | --- | --- | --- |
| T01 | openapi-typescript + openapi-fetch | 工程方向采用，版本待测试 | S1：从受控OpenAPI生成TS，CI检查契约差异；生成类型不替代运行时授权/校验 |
| T02 | pytest + Hypothesis，保留Vitest/Playwright | 测试方向采用，版本待测试 | S1：QC固定金标准+性质测试，保存反例；随机测试不替代业务预期，自动化不自动等于OQ |
| T03 | docxtpl + 固定LibreOffice headless | 报告PoC/产品准入候选 | S0探测复杂模板，S3按批准模板落地；隔离worker、禁宏/外链、限制资源与模板表达式，失败再评估其他渲染器 |
| T04 | pgBackRest + WAL归档 | 恢复PoC/运维准入候选 | S1恢复实验/S3目标准入；同时恢复对象版本，实测RPO/RTO，不只检查备份日志 |
| T05 | pySerial + 文件适配器 + 有界持久缓冲 | 按设备需要采用的采集方向 | S0盘点/S3两类代表源；断线、重复、乱序、截断、重启和缓冲满测试 |
| T06 | PG版本定义 + Pydantic + 受限状态机 | 产品能力纳入，不是新框架 | S1/S2：批准后生效、旧执行快照不变；不执行用户Python/JS/SQL |
| T07 | 结构化日志/健康检查/基础告警；按需OpenTelemetry | 基础可观测性必需，额外平台不必装 | S1基础/S3告警；优先已有IT设施；遥测不是质量审计 |
| T08 | 中文检索/化学结构与复杂编辑器专项 | 需求保留，组件/阶段待专项确认 | S0边界/S5专项；不得默认PG英文全文配置满足URS-623，也不得静默删除URS-601/602 |

不得把ProComponents、AG Grid、其他图表库、另一个后端、Kubernetes/Kafka/完整BPMN平台作为自动新增项。确需引入时提交ADR、样例、许可证、安全、维护及验证影响评估。

技术组件不是法规要求本身。先证明能实现原始记录、受控版本、签名审计、正确计算和恢复，再批准产品和精确版本；不以热门程度或未运行的基准排名选型。

官方文档入口（安装日重新核查版本和许可）：
- https://openapi-ts.dev/openapi-fetch/
- https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html
- https://docxtpl.readthedocs.io/en/latest/
- https://help.libreoffice.org/latest/en-US/text/shared/guide/pdf_params.html
- https://pgbackrest.org/user-guide.html
- https://pyserial.readthedocs.io/en/latest/shortintro.html
- https://opentelemetry.io/docs/concepts/observability-primer/
