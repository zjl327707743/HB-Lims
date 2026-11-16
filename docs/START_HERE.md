# HB-Lims 团队入口

**架构更新：** Owner明确自研LIMS并由第三方提供验证服务，HBOS只做入口或可选SSO。请优先阅读 [ADR-0002 技术对比](architecture/adr/0002-independent-validation-architecture-evaluation.md)、[系统与认证边界](architecture/hbos-lims-trust-boundary.md)、[第三方验证工作模式](validation/external-validation-operating-model.md)。此前ADR-0001仍作为早期提案留档，不代表决定技术框架。

状态：基础治理候选；架构未批准、业务应用未实现、未部署。

## 建议阅读顺序

1. [原始资料索引](sources/README.md) 与 [审阅结果](review/2026-11-16-source-review.md)。
2. [需求编号和追踪](requirements/README.md)、[待决事项](requirements/decisions.md)。
3. [竞品借鉴](research/competitive-landscape.md)、[技术ADR](architecture/adr/0001-independent-modular-monolith.md)、[领域边界](architecture/domain-boundaries.md)。
4. [开发规范](../CONTRIBUTING.md)、[Agent规则](../AGENTS.md)、[GitHub设置清单](governance/github-settings-checklist.md)。
5. [分阶段路线和任务](delivery/ROADMAP.md)、[验证要求](validation/README.md)。

## 先认清三个边界

- URS原件是业务需求来源；V3.1是已采用的前端体验，不是可信后端。
- 本轮的架构建议、测试设计和目录不是已经实现的业务功能。
- 仓库CI通过不是合规认证；写入CODEOWNERS也不会自动开启分支保护。

正式业务页面不增加开发报告、URS矩阵或项目交付入口。所有工程材料保留在仓库docs内。
