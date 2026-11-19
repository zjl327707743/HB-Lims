# 验证准备与开发约束增补

版本 VR-DEV-V1，编制日期 2026-11-19。状态：随 PR #1 提交审查，未代表 QA 批准、应用验证或生产放行。

本增补把两份 2026-11-17 技术报告中的有效建议转化为可执行开发约束。保留 TECH-V1 / FRAMEWORK-V1、Next.js + Ant Design + FastAPI + PostgreSQL、独立 LIMS 与 V3.1 风格。28 条 DEV 规则细化既有 C01–C14，不增加或删减原 185 条 URS，也不把新增规范数量当需求完成率。

## 阅读顺序

| 对象 | 先看 | 再看 |
| --- | --- | --- |
| Owner 和 QC/QA | [阶段与质量门槛](GATES.md)、[17 类待决参数](DECISIONS.md) | [法规依据与报告纠偏](REGULATORY_BASIS.md) |
| 开发者 | [28 条开发约束](DEVELOPMENT_CONSTRAINTS.md) | 当前领域原规范及[工程证据契约](../../validation/ENGINEERING_EVIDENCE.md) |
| Agent | 根 [AGENTS.md](../../../AGENTS.md)、[Agent 工作流程](AGENT_WORKFLOW.md) | [结构化规则](constraints.json)、[任务影响模板](../../templates/DEVELOPMENT_CHANGE.md) |
| 评审与验证人员 | [报告采纳记录](../../review/2026-11-19-reports-adoption.md) | [质量状态模板](../../templates/QUALITY_STATUS.json)、[阶段门槛](GATES.md) |

## 规则效力与例外

DEV-001 至 DEV-028 是本项目拟纳入基线的 MUST 工程约束。其法规控制目标、条件适用性和工程实现分别说明：法规不点名要求 Next.js、WORM、哈希链或微服务。合并后团队按本规范开发；合并本身不关闭企业适用性、参数批准或运行验证。

规范变更须记录旧规则、新规则、原因、风险、受影响 URS/历史记录/在途任务/签名/接口/验证范围及测试，经过相应非作者评审。涉及质量解释、接受标准或质量风险的决定由 QC/QA 按受控职责批准；Owner 的工程授权不冒充该批准。合法例外必须有范围、期限、补偿控制、责任人及复核；不得豁免适用法律、伪造批准或以例外绕过用途必需控制。

[constraints.json](constraints.json) 是逐条规则的结构化文本；[DEVELOPMENT_CONSTRAINTS.md](DEVELOPMENT_CONSTRAINTS.md) 是同内容便读版。两者通过生成器同步并由 CI 校验，校验只证明规则结构和便读版同步；另由资料检查核对相对链接可解析，不证明运行行为符合规范或来源语义已获批准。

## 已实现检查与待实现能力

当前可运行的是源件/资料治理及工程证据一致性检查。业务权限、审计、签署、文件隔离、性能、恢复等仍须随应用逐项开发和实际测试。登记中的应用状态保持 NOT_IMPLEMENTED / NOT_RUN；正式验证与 QA 批准分别记录。

证据登记支持本地合成/获准脱敏材料；外部受控证据适配器尚未实现。不得为通过公开仓库 CI 上传真实质量记录、人员签名或生产秘密。外部证据不可核验时阻断本次晋升，保留历史事实。
