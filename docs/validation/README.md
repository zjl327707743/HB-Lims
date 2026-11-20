# 验证与证据

当前状态：NOT_RUN（正式业务/现场验证）。现有治理CI不是GMP验证，原型采用记录不是本厂生产放行。

当前项目骨架见 [SIA / VP / 初始风险与资料索引](lifecycle/README.md)。[LC 生命周期规则](../standards/sdlc-validation/LIFECYCLE_STANDARD.md)与[测试策略](../standards/sdlc-validation/TEST_STRATEGY.md)规定实施方式；[8 类模板](../templates/validation/README.md)用于编制具体文件。模板和规划均未执行/未批准。

按风险和适用性由QA批准验证策略，保留URS→FS/DS→风险→用例→结果→偏差关闭的RTM。URS-2107–2109中提及的计划、设计确认、FAT、IQ/OQ/PQ、总结、运行维护及知识转移按实际实施模式裁剪并批准，不能仅生成空模板后宣布通过。

## 必须覆盖的验收族

- 主流程与异常：撤回、退回、终止、非指定人员、越序、异常未处置、复测来源和批准后修改。
- 数据完整性：原始值与修订、标准/公式/方法/流程版本、签名绑定、审计前后值/原因、校时、原始文件与报告可读性。
- 身份与隔离：列表/详情/搜索/导出/附件权限一致；管理员职责边界、过期资格、双人确认、单终端策略、错密/锁定。
- 并发：重复提交/签名、库存超扣、双人签署同人冒用、状态冲突、部分失败事务回滚、外部重试幂等。
- 集成和运维：真实设备回执、原始数据保留、备份恢复核对、升级/迁移/回退、性能及打印边界。

证据记录环境、浏览器/设备、应用提交和制品摘要、测试身份、前置数据、步骤、预期/实际、失败截图或日志。使用合成数据提交公共仓库；真实验证证据放公司受控系统，仓库只登记不泄密的引用。

标准至少保留5年业务数据是URS原要求，不等于5年后自动删除；具体保留期、法律保留、备份、RPO/RTO及销毁审批由QA/IT确定。

法规资料需确认适用性和现行版本，不把厂商宣传当法规证明：
- 21 CFR Part11官方文本：https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11
- FDA Data Integrity指导：https://www.fda.gov/regulatory-information/search-fda-guidance-documents/data-integrity-and-compliance-drug-cgmp-questions-and-answers
- FDA OOS指导：https://www.fda.gov/regulatory-information/search-fda-guidance-documents/investigating-out-specification-oos-test-results-pharmaceutical-production-level-2-revision

本文件是工程验证规划，不是QA批准、法律结论或认证声明。
