# 需求基线与追踪矩阵

`urs-index.csv` 是185条原编号、DOCX表号/行号和原I/C/Q类别索引；没有重新编号。`traceability.json` 保存正式开发的默认状态及逐条覆盖。所有未登记项明确为NOT_IMPLEMENTED / NOT_RUN，不把缺省解释成完成。

运行 `python3 scripts/governance/check_repository.py`，从原始DOCX重新提取全文，与索引逐条比对，生成 `artifacts/governance/requirements-rtm.csv`。输出包括原编号、原文、分组、定位、类别、实现、测试、责任人、设计、用例、证据和决策引用。它是工程RTM，不是已批准的验证记录。

逐条更新示例（仅格式，不代表已完成）：

```json
{"URS-100": {"implementation": "IN_PROGRESS", "test_status": "NOT_RUN", "owner": "待指派", "design_ref": "docs/architecture/adr/0001-independent-modular-monolith.md"}}
```

实现状态：NOT_IMPLEMENTED / IN_PROGRESS / IMPLEMENTED / BLOCKED / DEFERRED。测试状态：NOT_RUN / PASS / FAIL / BLOCKED。PASS必须有已实现状态、设计、用例、证据；DEFERRED必须有批准决策引用。检查器只验证结构和引用存在与否的字段约束，不能判定证据内容真实或QA批准有效，仍必须人工审查。

一条复杂URS需拆多个子用例，但原条目保留；只有所有适用子用例及必要外部条件满足后才能标PASS。原件分类与风险评级/优先级分开管理。编号勘误、阶段调整、暂缓需求都走 [待决事项](decisions.md)，不删除难做的条款。
