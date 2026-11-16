# TECH-V1 技术栈与独立架构

日期：2026-11-16。开发规范基线，待PR审查；不代表QA或生产批准。依据及版本信息见 [SOURCES](SOURCES.md)。

## 选型收敛

| 层 | 实施选择 | 限制与责任 |
| --- | --- | --- |
| Web | React + Next.js App Router + TypeScript strict | Next仅Web和薄BFF，不访问质量数据库写业务 |
| UI | antd + @ant-design/nextjs-registry | 主题映射V3.1；不用默认后台模板替换已采用设计 |
| 查询 | TanStack Query | 仅用户隔离的服务端状态；关键业务写入不乐观成功 |
| 表单/表格 | AntD Form / Table | Zod按需做边界校验；不重复引入第二套表单状态 |
| 图表 | Recharts | 固定一种主库；统计规则和判定由后端版本化计算 |
| 本地/URL状态 | Zustand按需；nuqs | 不保存可信结果或长期令牌；URL参数采用非敏感白名单 |
| API | FastAPI + Pydantic | 明确命令、授权、版本和错误合同，不能仅开发通用CRUD |
| ORM | SQLAlchemy 2.0 | API使用AsyncSession；不同时使用SQLModel作为第二套模型 |
| 迁移 | Alembic | 人工审查迁移；部署时单独执行，不在每个API进程启动时自动迁移 |
| 数据库 | PostgreSQL | 独立DB/账号；精确numeric、约束、事务、备份恢复 |
| 临时设施 | Redis | 缓存/会话/限流与broker分离；质量记录以PG为准 |
| 任务 | Celery | 幂等重试、任务台账、Outbox与失败对账；不是自动exactly-once |
| 文件 | S3兼容存储接口 | 生产产品待准入；社区MinIO不可作为无条件生产默认 |
| 部署 | Docker + Compose + Nginx | 开发/验证/生产隔离，单机不是高可用，版本化配置 |
| CI/CD | GitHub Actions | 自动构建/测试；生产部署需受控批准，不随合并自动上线 |

ProComponents、AG Grid、@ant-design/charts、ECharts、shadcn、MUI、ARQ、Traefik、GitLab CI不是首版必装依赖。后续确有需求，通过ADR说明收益、测试和许可再增加，避免各组自行选择。

## 服务边界

浏览器 → 独立LIMS域名/Nginx → Next Web/薄BFF → FastAPI → 独立PostgreSQL；FastAPI通过明确适配器连接S3、Redis和Celery。worker使用相同受控产品版本，仪器/ERP/WMS/DMS走明确接口与回执。Web/API/worker分进程，不等于微服务，也不要求同一台主机。

HBOS只作入口链接；统一身份是可选外部依赖。LIMS有直接URL、独立会话、QC授权、资质、签名与审计。禁止共享HBOS业务数据库、管理员权限、Cookie或在HBOS升级时顺带更新LIMS。若SSO由HBOS代理，该接口必须列入依赖和影响评估，不能以“独立仓库”宣称无依赖。

## 版本与能力准入

本轮不安装应用依赖、不写虚假的lockfile。首个工程PR必须交付精确的Node/Python/Next/React/antd/FastAPI/SQLAlchemy/PG/Celery/Redis版本、包管理器、lockfile、镜像digest、兼容测试、许可证及漏洞审查。按查阅时官方支持策略，Next 16.x和antd 6.x可作为起测系列，SQLAlchemy 2.0为指定系列；PostgreSQL选择受支持主版本并固定补丁。稳定支持状态须在实际安装日再次核查，禁止使用latest/canary/RC作为生产基线，不能把宽范围或“系列”冒充精确冻结版本。

Redis不同版本许可不同，商业组件也须逐项审核；不得因仓库公开就擅自为所有内容套用开源许可证。已有数据保持期不能作为冻结旧软件多年不打补丁的理由。

## 性能与范围

数百注册账号不等于数百并发。收集峰值在线/活跃、每日样品/结果/附件、仪器流量、报表以及增长数据，再确定硬件及压测。URS-103/104接受标准不得被p95或任务入队耗时替换。前端采用现代浏览器，原URS的IE条款须由Owner/QA批准差异。

关键质量操作仍包含请验/取样/接收/检验/复核/异常处置/报告归档和打印；“样品、订单、结果CRUD”只是基础数据能力，业务术语使用已有“请验/检验任务”，不得自行改为销售订单模型。
