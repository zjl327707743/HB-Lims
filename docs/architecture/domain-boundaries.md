# 领域分区与共同合同

这些是同一个模块化单体内的责任域，不是已经实现的微服务。真实人员尚未指派。

| 模块路径 apps/api/modules/ | 负责对象 | 不允许另造/直接改 |
| --- | --- | --- |
| identity | 账号映射、角色/数据范围、资格检查、会话 | 不把管理员等同所有业务权限 |
| masterdata | 标准/方法/公式/模板版本、单位、物料、供应商 | 不覆盖已被执行引用的批准版本 |
| samples | 请验、取样、标签、接收、分样、分配、交接 | 不直接替检验员写结果或放行 |
| testing | 检验执行、电子记录、原始/计算结果、修订 | 不直接批准自己的检验 |
| quality | 工作流、独立复核、签名、异常处置、审计 | 不把签名降格为页面上的姓名图片 |
| resources | 仪器、试剂、标准品、库存流水、菌种谱系 | 不绕过统一资质/签署/审计接口 |
| retention | 留样位置/数量/观察/出入/销毁 | 不直接改资源或样品历史 |
| stability | 稳定性条件/时间点/取样与交接 | 0月结果引用保留来源，不变成无来源复制 |
| environment | 厂房图纸点位、区域状态、采样培养计数、趋势 | 不另造结果、审计和身份体系 |
| reporting | 报告版本、生成、预览/打印请求、重印记录 | 浏览器print成功调用不等于物理打印成功 |
| integrations | 仪器/SDMS/HBOS/ERP/WMS/DMS/TMS适配与回执 | 不跨系统直接写数据库 |

共同合同由 packages/contracts 维护；各域通过显式业务服务调用，禁止跨域任意改表。允许同一数据库事务协调；用代码依赖检查和模块测试保证边界，不用网络调用制造初期复杂度。

关键记录：TestRequest、Sample/Aliquot、CustodyEvent、TestExecution、ResultRevision、SpecificationVersion、WorkflowVersion、Signature、AuditEvent、ReportVersion、InventoryMovement、IntegrationOutbox。命名仅为设计候选，不代表已有模型代码。
