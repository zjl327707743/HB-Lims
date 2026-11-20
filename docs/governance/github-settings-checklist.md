# GitHub 服务端设置清单

状态：**待Owner配置与验证，不能视为已经启用。** 初始只读检查main protected=false；本轮未调用设置写接口。跟踪Issue #3。

## 启用顺序

1. 确认公开授权与真实协作者名单，最小权限邀请；先落实至少一位有资格的非作者评审人，再开启审批要求，避免Owner成为唯一代码所有者却无法自批。
2. 将治理PR审查合入main后，确认默认分支含CODEOWNERS和工作流；本PR自身不会因为head新增CODEOWNERS就自动具备base上的规则。
3. 在Settings/Rules或Branches配置main：要求PR、非作者批准、旧批准随新提交失效、讨论解决；禁止强推与删除；限制管理员绕过。
4. 在实际CI成功后选中唯一检查名称 `source-baseline` 和 `repository-governance`；确认更新基线/合成提交后的结果。不要配置从未出现的虚构检查。
5. 按真实成员调整CODEOWNERS，关键路径代码与QC/QA业务确认并行。CODEOWNERS不等于自动强制批准，必须开启对应规则。
6. 配置漏洞私密报告、依赖安全提示等可用功能；费用/套餐变化需Owner确认。不得在公开工单贴漏洞利用细节或密钥。
7. 用无审批PR、失败检查、强推/删除尝试的受控测试验证保护实际生效；保存证据，不破坏main数据。

## 当前未执行

未邀请成员、未创建Organization/Teams、未创建GitHub Projects看板、未设置Milestone/Label、未更改可见性、未配置保护或生产环境审批。目录、模板、脚本和Issue不是这些设置的替代品。

建议看板列Backlog/Ready/In progress/Review/Validation/Done，字段Domain/URS/Priority/Risk/Owner/Evidence；先用现有Issue工作，不为工具配置阻断需求澄清。

官方依据（访问2026-11-16）：
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
