# HB-Lims

**2026-11-16 技术选型更新：** 自研LIMS必须独立运行和接受第三方验证，HBOS只作为入口/可选SSO。前后端和数据库不预设Django、PostgreSQL或Vue；详见 [ADR-0002 技术重评](docs/architecture/adr/0002-independent-validation-architecture-evaluation.md)、[HBOS边界](docs/architecture/hbos-lims-trust-boundary.md)和[外部验证方案](docs/validation/external-validation-operating-model.md)。相关文档仍是 Proposed，不代表技术栈已经确定。

LIMS project — 海滨实验室信息管理系统独立开发仓库。

## 当前状态

**项目基础建设 / 尚无正式业务应用 / 未部署 / 未通过正式验证。**

已上传的 URS、V3.1 原型和开发规范是需求与界面依据，不是生产系统。本轮工程目录为团队协作分区，技术选型仍为 Proposed，不能把目录、原型或 CI 绿色视为业务已实现。

从 [团队入口](docs/START_HERE.md) 开始；查看 [资料审阅](docs/review/2026-11-16-source-review.md)、[竞品研究](docs/research/competitive-landscape.md)、[架构建议](docs/architecture/adr/0001-independent-modular-monolith.md)、[实施路线](docs/delivery/ROADMAP.md)。

## 权威资料

- [URS 原件](docs/六车间QC实验室信息管理系统用户需求说明.docx)
- [V3.1 已采用原型包](LIMS_V3.1_已采用交付包.zip)
- [独立前端开发规范](docs/LIMS独立前端开发规范.md)
- [原件哈希与使用边界](docs/sources/README.md)

三份原件保留原路径和字节；不覆盖、不重新编号、不把压缩包直接当生产源码。URS 适用主体与容量等差异见 [待决事项](docs/requirements/decisions.md)。

## 分区

| 路径 | 用途 |
| --- | --- |
| `apps/web/` | 保留 V3.1 体验的独立前端 |
| `apps/api/` | 模块化单体后端与领域边界 |
| `apps/worker/` | 可选异步任务进程；不等于另建微服务 |
| `packages/contracts/` | 前后端接口、命令、状态与错误约定 |
| `packages/ui/` | 经确认的共用组件与设计 Token |
| `docs/` | 需求、研究、设计、治理、验证、交付 |
| `tests/` | 集成、端到端、安全、性能验收 |
| `deploy/` | 环境隔离、发布与恢复方案 |
| `scripts/governance/` | 可运行的原件和需求追踪检查 |

## 本地治理检查

需要 Python 3.10+，当前治理脚本仅使用标准库，不安装应用依赖：

```sh
python3 scripts/governance/verify_sources.py
python3 scripts/governance/check_repository.py
python3 -m unittest discover -s scripts/governance -p 'test_*.py' -v
```

完整 185 条 RTM 由原件、编号索引及追踪状态生成到 `artifacts/governance/requirements-rtm.csv`；该文件是可重建输出，不能手工改它来改变完成状态。正式应用启动命令将在业务脚手架 PR 中提供，本轮没有可运行生产服务。

## 协作与边界

先读 [CONTRIBUTING](CONTRIBUTING.md)、[AGENTS](AGENTS.md) 和 [安全规则](SECURITY.md)。通过短分支和小 PR 协作，禁止擅自改 main、生产数据、原件或企业权限。当前分支保护、成员配置与独立评审人待 [Issue #3](https://github.com/zjl327707743/HB-Lims/issues/3) 收口。

本仓库为 Public：只提交已获公开授权的资料与合成测试数据。没有为本项目新增开源许可证；第三方代码和品牌权利按原有声明及后续授权决策处理。
