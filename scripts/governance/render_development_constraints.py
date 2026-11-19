"""Render/check the human view of DEV constraints. No runtime/compliance claim."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = Path("docs/standards/validation-readiness")
TOP = {"schema_version", "id", "date", "timezone", "status", "source_head",
       "normative_scope", "application_implementation", "application_validation",
       "qa_approval", "rules"}
FIELDS = {"id", "title", "level", "basis", "gates", "control_ids", "source_refs",
          "owner_roles", "must", "forbidden", "acceptance", "evidence"}

def unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("Duplicate key: " + key)
        out[key] = value
    return out

def render(data):
    if not isinstance(data, dict) or set(data) != TOP:
        raise ValueError("Unknown or missing catalog fields")
    if (data["schema_version"] != "1.0.0" or
        data["id"] != "HB-LIMS-DEVELOPMENT-CONSTRAINTS-V1" or
        data["status"] != "PROPOSED_IN_PR" or
        data["application_implementation"] != "NOT_IMPLEMENTED" or
        data["application_validation"] != "NOT_RUN" or data["qa_approval"] != "NOT_GRANTED"):
        raise ValueError("This planning catalog cannot claim application execution or approval")
    rows = data["rules"]
    if not isinstance(rows, list) or len(rows) != 28:
        raise ValueError("VR-DEV-V1 requires its 28 controlled rules")
    seen = set()
    lines = ["# 28 条开发约束", "",
        "由 [constraints.json](constraints.json) 生成。修改结构化文本后运行 "
        "`python3 scripts/governance/render_development_constraints.py`；CI 使用 `--check` 检查同步。",
        "", "这里的 MUST 表示本项目开发约束；法规效力及适用条件见 "
        "[法规依据](REGULATORY_BASIS.md)。实施阶段见 [G0–G5](GATES.md)。"
        "规则尚未代表应用已实现或验证通过。", "",
        "| 规则 | 主题 | 关口 | 既有控制 |",
        "| --- | --- | --- | --- |"]
    for row in rows:
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError("Unknown or missing rule fields")
        if row["id"] in seen or row["id"] not in {f"DEV-{n:03}" for n in range(1, 29)}:
            raise ValueError("Duplicate/unknown DEV rule")
        seen.add(row["id"])
        if row["level"] != "MUST" or row["basis"] != "PROJECT_ENGINEERING_CONSTRAINT_DERIVED_FROM_REFERENCED_CONTROL_OBJECTIVES":
            raise ValueError("Unsupported rule force/basis")
        if not isinstance(row["title"], str) or not row["title"].strip():
            raise ValueError("Missing title")
        for key in ("gates", "control_ids", "source_refs", "owner_roles",
                    "must", "forbidden", "acceptance", "evidence"):
            value = row[key]
            if not isinstance(value, list) or not value or any(
                not isinstance(x, str) or not x.strip() for x in value):
                raise ValueError("Missing/non-text rule list: " + key)
            if len(value) != len(set(value)):
                raise ValueError("Duplicate rule item: " + key)
        if not set(row["gates"]).issubset({f"G{n}" for n in range(6)}):
            raise ValueError("Unknown gate")
        if not set(row["control_ids"]).issubset({f"C{n:02}" for n in range(1, 15)}):
            raise ValueError("Unknown existing control")
        lines.append(f'| {row["id"]} | {row["title"]} | {"、".join(row["gates"])} | {"、".join(row["control_ids"])} |')
    for row in rows:
        lines += ["", f'## {row["id"]} {row["title"]}', "",
            f'责任角色：{"、".join(row["owner_roles"])}。关口：{"、".join(row["gates"])}。',
            f'依据定位：{"；".join(row["source_refs"])}。既有控制：{"、".join(row["control_ids"])}。']
        for key, label in (("must","必须"),("forbidden","禁止"),("acceptance","接受条件"),("evidence","交付证据")):
            lines += ["", f"### {label}", ""]
            lines += ["- " + item for item in row[key]]
    lines += ["", "## 变更和例外",
        "", "按 [入口的效力与例外规则](README.md) 进行受控变更。"
        "自动检查仅验证规则结构与便读版同步，不测试上述运行行为，也不认证法规适用、人员资格或批准真实性。", ""]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads((ROOT / BASE / "constraints.json").read_text(encoding="utf-8"),
                          object_pairs_hook=unique,
                          parse_constant=lambda v: (_ for _ in ()).throw(ValueError("Non-JSON number: "+v)))
        expected = render(data)
        output = ROOT / BASE / "DEVELOPMENT_CONSTRAINTS.md"
        if args.check:
            if not output.is_file() or output.read_text(encoding="utf-8") != expected:
                raise ValueError("Human constraint view is stale; regenerate it")
        else:
            output.write_text(expected, encoding="utf-8")
        print(json.dumps({"scope":"constraint schema/document synchronization only",
                          "rules":len(data["rules"]),"mode":"check" if args.check else "render","errors":[]}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"scope":"constraint schema/document synchronization only","errors":[str(exc)]}))
        return 1

if __name__ == "__main__":
    sys.exit(main())
