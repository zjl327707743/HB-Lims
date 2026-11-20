# 测试分区

正式业务/浏览器/性能/恢复目前NOT_RUN。当前可运行的只是scripts/governance的文档和源基线检查；这些不证明LIMS合规。

应用单元测试近源码，跨域及真实PG测试放integration，浏览器放e2e，权限/签名放security，负载恢复放performance，V3.1截图放visual，键盘/读屏放accessibility。测试策略见 [VAL-V1](../docs/standards/DELIVERY_VALIDATION.md)。

每次执行记录URS/风险/用例/构建/配置/环境/操作者/预期和实际/证据/缺陷。Mock与真实API分开，不能把测试定义当执行结果。第三方验证证据在受控存储，公共仓库只有合成数据和脱敏引用。
