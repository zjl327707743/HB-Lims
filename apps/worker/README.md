# Celery worker 分区

采用Celery，任务/Outbox台账以PG为准；见 [存储与任务规范](../../docs/standards/STORAGE_TASKS.md)。ARQ不是当前选型。

默认同步worker任务用独立同步SQLAlchemy会话/受控服务，不能直接假设async函数被自动await，不复用API事件循环或会话。任务幂等、可重试、可对账；不要重复生成多份有效报告或重复外发放行，不代签。

Redis broker与缓存隔离并有持久化/容量控制，丢队列可以从PG未完成台账恢复。远期稳定性计划保存在PG。本轮只有分区规范，没有worker应用。
