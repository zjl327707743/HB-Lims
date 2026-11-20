# 部署与运行分区

当前方向Docker Compose + Nginx + GitHub Actions；见 [交付门禁](../docs/standards/DELIVERY_VALIDATION.md) 和 [存储恢复](../docs/standards/STORAGE_TASKS.md)。这不是已部署环境。

DEV/TEST/验证(UAT)/PROD隔离身份、数据、密钥与配置。生产不挂载可变源码，镜像与配置有摘要；单机Compose不是HA，RPO/RTO未批准不得承诺可用性。数据库迁移单独执行，恢复需PG与对象版本一致。

MinIO社区版不作为生产默认；S3产品准入尚未完成。真实密钥、现场记录和备份不能进仓库或公共CI。构建/测试可自动，生产发布必须批准，不默认GitHub合并即上线。
