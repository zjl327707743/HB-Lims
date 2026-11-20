# 前后端业务合同

[当前技术规范](../../docs/standards/README.md) 下，FastAPI OpenAPI定义请求/响应并生成TS客户端类型；浏览器校验、Pydantic及DB约束各负其责。Mock与真实HTTP共享批准的合同。

必须定义稳定ID、对象版本、UTC时间/展示时区、Decimal字符串及单位、可操作状态、范围过滤、分页排序白名单、结构化错误/request_id、expected_version、Idempotency-Key和签署授权绑定。

受控动作submit/receive/record-result/correct/review/approve/retest须显式命令；actor/可信时间/批准权限不能由客户端任意填。相同幂等键不同payload冲突，超时可按命令ID查状态。

不在前端复制质量规则；不以ORM表模型直接暴露可写签名/角色字段。破坏性变更需版本策略和兼容测试；接口回执不是仅有“已连接”图标。当前尚无完整批准的OpenAPI实现。
