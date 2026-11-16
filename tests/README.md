# 测试分区

业务测试当前NOT_RUN；此目录README不是测试通过证据。实际治理单测位于scripts/governance/test_check_repository.py。

应用单元测试靠近实现；跨域/PostgreSQL测试放integration；浏览器主流程放e2e；授权/签名/数据隔离放security；代表性负载放performance。所有测试使用合成数据，真实验证材料进入公司受控系统。

每个业务PR提供至少正向及拒绝场景，并映射原URS。禁止跳过失败、降低断言或把静态语法检查计作业务回归。CI逐阶段增加实际测试，不预先添加空成功Job。
