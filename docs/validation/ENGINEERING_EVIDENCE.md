# 工程证据引用与状态门禁

## 作用与结论边界

本契约补充 EVD-V1，修复治理检查把任意非空字符串当成证据或范围批准的缺口。`traceability.json` 的 `test_status` **仅表示工程测试结果**。`PASS` 不代表验证协议执行通过、独立复核通过、QA 批准或生产放行；这四种事实使用各自受控执行和批准记录，不能由本检查器生成。空登记是当前真实状态，不包含任何应用通过证据。

执行 `python3 scripts/governance/check_repository.py` 时，检查器读取 `engineering-evidence.json`，解析实际设计、用例和执行记录，并核对本地材料的 SHA-256、URS、责任人、结果及版本关系。输出会明确 `ENGINEERING_TEST_ONLY`，验证执行、独立复核、QA 放行为 `NOT_ASSESSED`。这些是本检查器的能力边界，不是对历史质量状态的改写。

机器只能检查材料存在、字节完整和登记关系一致。它不能证明人没有伪造日志、声明身份真实、脱敏已获批准、批准者有资格或批准签署有效。合格非作者仍需审查工程证据；范围批准和质量决定须由授权人员在企业受控系统核对，不以一个 JSON 的 `APPROVED` 字符串替代授权。软件门禁与人审缺一不可。

## 公开仓库和外部证据

公开仓库只放合成测试资料或获准脱敏材料。文件登记的 `classification` 只能是 `SYNTHETIC` 或 `APPROVED_REDACTED`；范围批准摘录只能用后者。此标签是需要评审的声明，检查器不具备自动识别真实敏感数据或核实脱敏批准的能力。

真实质量记录、人员签名、生产凭据与完整敏感证据留在企业受控库，不为通过本门禁上传公开仓库。当前检查器为离线实现，不请求网络、不读取凭据；`controlled://`、HTTPS 等外部原始证据路径无法由它核验，会阻断本次登记核验和状态晋升。未来需为受控证据库单独建设经审查的只读适配器，校验授权访问、有效记录及完整性后再扩展契约；不能把外部 URI 改成一个任意本地文本蒙混通过。

核验受阻时保留既往原始执行事实、失败、复测和批准历史；只清理本次不可信或过时的 RTM 导出，并写明错误。维护者不能为了让 CI 绿色删除真实失败记录或改写历史 `PASS`。正式证据保存期限按获批策略执行，GitHub Actions 的短期制品不承担长期保存。

## 登记格式

`engineering-evidence.json` 使用严格字段白名单，`schema_version` 为整数 `1`；不接受未知字段或重复 JSON 键。登记中无有效证据时，数组为空、`target` 与 `scope_id` 为 `null`。

| 字段 | 含义 |
| --- | --- |
| `kind` | 固定 `ENGINEERING_REFERENCES_NOT_QUALITY_APPROVAL` |
| `target` | 本次欲声明工程通过的目标，含完整 40 位 `source_commit`、非空 `artifact_digests` 名称与 `sha256:` 摘要映射、`config_digest` |
| `scope_id` | 本次范围决定的稳定范围 ID；用于防止把另一试点的延期决定挪用 |
| `designs` | 每条为唯一 `id`、非空 `urs_ids`、`artifact` |
| `cases` | 每条同上，另含 `design_ref`，必须指向匹配 URS 的设计 |
| `executions` | 每条为唯一 `id`、非空 `urs_ids`、执行 JSON 的 `artifact` |
| `scope_decisions` | 每条为唯一 `id`、非空 `urs_ids`、批准范围摘录 JSON 的 `artifact` |

每个 `artifact` 仅含 `path`、64 位小写十六进制 `sha256`、`classification`。路径须是仓库内实际文件，禁止绝对路径、父目录跳转、逃逸软链接和外部 URI；登记文件自身、来源清单、RTM 状态和规划 JSON 的加载也检查仓库边界。软链接循环及错误根类型必须形成失败结果，不能留下前次绿色报告。单件离线检查上限 20 MB，此大小是检查器工程限制，不是法规限度。大文件或外部证据另走受控适配器准入，不能截断原证据。

### 工程执行 JSON

必需且仅允许：`kind`、`evidence_id`、`urs_ids`、`design_ref`、`design_sha256`、`case_ref`、`case_sha256`、`owner`、`executor`、`executed_at`、`target`、`result`、`raw_evidence`、`retest_of`、`retest_disposition`。

`kind` 固定 `ENGINEERING_TEST_EXECUTION`；`evidence_id` 与登记 ID 相同；`result` 为实际 `PASS`、`FAIL` 或 `BLOCKED`。时间含时区，不能晚于评估时刻。责任人与执行者不可空白或使用 `UNASSIGNED` 等占位值。`raw_evidence` 是至少一个实际本地原始测试输出的 `artifact`；只填摘要、文件名或 URL 不足以通过。执行 `target` 使用上述目标结构；同一登记可保留历史目标的执行，不得把历史执行改写成新版本。

执行记录的 `design_sha256` 与 `case_sha256` 必须是本次执行所依据的设计和用例文件摘要，并与登记中实际材料一致。不能只绑定可变的设计/用例 ID：修改定义内容并更新登记摘要，不得使旧执行自动继承新含义。换版须使用新 ID 或等价不可变版本键，保留旧定义和旧执行。

要把某条 RTM 的工程结果更新为 `PASS`，其 `implementation` 为 `IMPLEMENTED`；`owner` 与执行责任人相同；`design_ref`、`case_ref`、`evidence_ref` 可解析且均覆盖该 URS；执行实际结果为 `PASS`，源码、制品与配置和登记的当前 `target` 一致。文件存在或 hash 匹配不证明语义正确，仍需独立评审设计、断言与原始输出。

### 失败与复测

同一 URS、用例与目标存在比所选 `PASS` 更晚的 `FAIL/BLOCKED` 时，不能通过挑选旧绿色结果晋升。绝对时间相同、无法证明先后顺序的冲突也阻断；不按日期字符串排序，统一转换成带时区的时间比较。

同一目标存在较早失败时，后续 `PASS` 必须通过 `retest_of` 列出所有对应失败/受阻执行 ID，并在 `retest_disposition` 提供实际工程处置 JSON 的 `artifact`。没有复测关系时这两项为 `[]` 与 `null`。历史失败保留原状态；处置只解释后续复测，不改写原 `FAIL`。

处置 JSON 仅含 `kind=ENGINEERING_RETEST_DISPOSITION`、`disposition_id`、`related_execution_ids`、`retest_execution_id`、`reason`、`reviewer`、`reviewed_at`。引用须与复测记录一致，原因非空，声明复核人与执行者/责任人不同，复核时间不早于复测且不晚于评估时刻。此前失败须真实存在且时间早于复测。此处只核工程元数据一致性，不自动关闭正式验证偏差或授予 QA 放行；复核人的真实身份、独立性和授权仍需人审或受控系统核验。

不同目标的历史失败可以保留；不能将其旧 `PASS` 移用于新目标。本门禁只处理当前 URS/用例/目标内的结果选择，不替代跨版本缺陷、风险和再验证影响评估。

### 延期范围决定 JSON

必需且仅允许：`kind`、`decision_id`、`urs_ids`、`scope`、`decision`、`status`、`approved_by`、`approved_at`、`valid_until`、`no_expiry_reason`、`revoked`、`controlled_record_locator`。

`kind` 固定 `REDACTED_SCOPE_DECISION`；`decision` 固定 `DEFERRED`；批准者、带时区批准时间和原受控记录定位均有值，批准时间不得晚于本次评估。当前使用需 `status=APPROVED` 且 `revoked=false`；撤销历史可以 `status=REVOKED`、`revoked=true` 保留，但不能支持新的延期晋升。

批准有期限时填写 `valid_until`，必须晚于批准时间且本次评估严格早于到期时刻，同时 `no_expiry_reason=null`。无固定到期日时填写 `valid_until=null` 及明确 `no_expiry_reason`，例如受控范围在变更或撤销前持续有效；不强迫所有历史批准新增固定到期日，也不得凭空补期限或批准。

`scope` 必须与登记的当前 `scope_id` 相同；RTM 的 `decision_ref` 指向这条登记并覆盖该 URS，责任人不能空白。该一致性检查没有认证批准真实性，非作者和 QA 必须核对原受控记录及权限，不得以合成测试中的批准 fixture 充当真实批准。

评估使用实际当前 UTC 时间并写入 `check-result.json` 的 `evaluated_at`。内部函数允许注入带时区的 `as_of` 以执行确定性测试；正式命令没有回拨评估时刻参数。时间同步及可信时钟由运行环境控制，本检查器不能认证系统时钟来源。到期或证据暂不可核时阻断本次晋升，不删除历史批准和原始执行事实。

本版不新增 `NA` 状态，也不自动把范围外视为满足。若新增不适用或其他范围决定，需评审其适用条件、结构、测试和输出语义后升级契约。

## 规划快照与实际进展分开

`framework.json`、`controls.json`、`function-scope.json`、`backlog.json` 是前期规划快照，拒绝未知字段、错误类型、行级伪造 `PASS/APPROVED` 等执行状态。B01 至 B14 已有 URS、控制、功能和依赖关系不得在无变更时删除；原本无依赖的起始任务仍允许空数组。该检查不等于已经分解全部 185 条 URS。

合法的需求分解、阶段调整和基线更新通过单独受控变更记录与非作者 PR 审查；同步更新对应快照、约束和负向测试，说明受影响范围及批准依据。实际执行、验证和质量进展保存在自己的登记中，不通过增加规划快照行级字段或修改固定 `NOT_RUN` 断言伪报。检查器不自动认证变更记录审批。

## 验收与维护

保留原有治理测试，新增用例包括不存在引用、错 URS/责任人/设计/用例/版本、定义改写并重算摘要、失败证据冒充通过、挑选旧 PASS、合法复测与失败保留、未来/过期/撤销批准、原始字节修改、外部证据不可核、登记根文件逃逸、软链接循环、缺失或错误批准范围、未知字段、错误类型、重复 JSON 键、删除关联及坏 JSON 清理旧导出。有效的合成工程证据应能通过；合成批准 fixture 只验证元数据规则，不是实际批准。

本门禁尚不检查软件真实业务行为、审批系统签名、第三方验证协议、受控库可用性、人员资格、实际制品来源真实性或最终质量结论。后续集成这些能力需要独立需求、设计和正反测试，不能扩大当前绿色 CI 的含义。
