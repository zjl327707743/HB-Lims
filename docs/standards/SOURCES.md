# 官方来源与证据边界

查阅日期：2026-11-16。以下证明产品文档/维护状态或法规原文，不证明本项目已实现或已合规。版本状态会变化，安装和发布时再次核查。规范中的禁止乐观质量写入、分层职责、测试场景等为本项目风险控制决策，不冒充官方原句。

| ID | 来源 | 本轮使用的事实 |
| --- | --- | --- |
| S01 | https://nextjs.org/docs/app/getting-started/proxy | Proxy/Middleware不应作为完整授权方案 |
| S02 | https://nextjs.org/docs/app/guides/authentication | 服务端授权、会话及Cookie控制 |
| S03 | https://nextjs.org/docs/app/guides/backend-for-frontend | BFF与后端边界 |
| S04 | https://nextjs.org/support-policy | 受支持系列及升级策略，不推荐canary生产 |
| S05 | https://ant.design/docs/react/use-with-next/ | App Router AntdRegistry样式集成 |
| S06 | https://ant.design/components/table/ | Table筛选/树/虚拟化等能力，需按场景测试 |
| S07 | https://nuqs.dev/docs/adapters | Next App Router适配器；敏感URL限制为本项目要求 |
| S08 | https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates | 提供乐观更新机制，不等于适合质量批准 |
| S09 | https://recharts.github.io/en-US/guide/getting-started/ | 图表组件，非已验证质量算法 |
| S10 | https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html | 并发任务分别使用AsyncSession |
| S11 | https://docs.celeryq.dev/en/stable/userguide/tasks.html | 幂等、ack及重复执行条件 |
| S12 | https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html | visibility timeout和broker局限 |
| S13 | https://github.com/python-arq/arq | README声明maintenance-only |
| S14 | https://github.com/minio/minio | 2026-04-25归档只读；不对其他商业产品作停运推断 |
| S15 | https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html | Object Lock与版本保留；不推断任意S3兼容产品都实现 |
| S16 | https://redis.io/legal/licenses/ | 版本相关许可；本轮未完成法律准入 |
| S17 | https://www.postgresql.org/support/versioning/ | 主版本支持与补丁策略 |
| S18 | https://docs.docker.com/compose/how-tos/production/ | Compose生产配置与单机部署可能性，不保证HA |
| S19 | https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11 | 11.10控制、11.50/70签名关联、11.200鉴别组件等；适用性由QA确认 |
| S20 | https://www.fda.gov/regulatory-information/search-fda-guidance-documents/data-integrity-and-compliance-drug-cgmp-questions-and-answers | 药品CGMP数据完整性指导，区别法规与指导 |
| S21 | https://health.ec.europa.eu/medicinal-products/eudralex/eudralex-volume-4_en | 官方Annex11入口仍标2011修订；后续修订须核对生效，不以草案代替 |
| S22 | https://fastapi.tiangolo.com/deployment/docker/ | 官方不再建议已弃用的旧专用FastAPI基础镜像 |

未在本轮实测：前端组件兼容、任何数据库性能、登录/签名、真实存储、恢复、仪器、监管符合性。第三方验证报告也不是监管机构认证。
