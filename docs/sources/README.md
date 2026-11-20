# 原件、存档与当前规范

原资料基线b25ef012955b35ba894408316f80f29652f4d4f2。URS和V3.1 ZIP保持原路径/字节。Owner本轮明确授权修改旧前端规范，因此原路径升级V2，V1原字节归档；不是静默修改验收依据。

| 资料 | 当前角色 |
| --- | --- |
| [URS](../六车间QC实验室信息管理系统用户需求说明.docx) | 冻结业务原件；编号/类别不变 |
| [V3.1 ZIP](../../LIMS_V3.1_已采用交付包.zip) | 冻结视觉/交互依据，HTML哈希不变 |
| [前端V1原字节存档](../archive/frontend/LIMS独立前端开发规范.v1.20261116.md) | 保留历史权威，blob仍17eda331335a73fe8e0fea9b8ad49eb5ae68cde2 |
| [前端V2](../LIMS独立前端开发规范.md) | 当前工程入口；界面/业务/验收章节完整保留 |
| [团队技术规范](../standards/README.md) | 新栈实施与验证要求 |

manifest.json列冻结字节与V2指向；verify_sources.py检查URS、ZIP、V1存档和HTML，check_technical_baseline.py比较三个保留章节并校验入口。没有移除或降低原件检查。

V1存档保留原文相对链接以确保字节一致，阅读原件请使用本索引；归档内链接不按新目录重写。提取表号/行号不是Word页码，hash/文本检查不是运行时视觉或合规验证。变更依据见 [记录](../governance/changes/CHANGE-20261116-TECH-V1.md)。
