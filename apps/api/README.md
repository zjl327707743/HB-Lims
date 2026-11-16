# 后端开发分区

**技术栈待选：** FastAPI/Python、Spring Boot/Java、ASP.NET Core/C#作为决赛候选，Django/DRF与NestJS是备选；数据库MySQL与PostgreSQL都保留。见 [ADR-0002](../../docs/architecture/adr/0002-independent-validation-architecture-evaluation.md)。下方Django建议是历史初始方案，不是冻结决定。

状态：仅领域边界，尚未实现API。推荐Django/DRF模块化单体；先批准ADR、合同与业务规则，再创建settings、migrations、服务层和测试。

`modules/`各域使用显式服务协调。跨域变更经过合同评审；禁止互相随意改表。业务写命令集中鉴权、状态、资格、版本与事务校验，不能仅靠前端禁用按钮。

正式集成测试使用PostgreSQL。账号、标准快照、结果修订、签名、审计与Outbox不能交给客户端作为可信来源。关联Issue #5。
