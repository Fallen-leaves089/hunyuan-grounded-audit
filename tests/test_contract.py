from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class ContractTests(unittest.TestCase):
    def test_manifest_identity(self) -> None:
        self.assertEqual(MANIFEST["name"], "project-health-audit")
        self.assertEqual(MANIFEST["package_name"], "hunyuan-grounded-audit")
        self.assertEqual(MANIFEST["license"], "Apache-2.0")
        self.assertEqual(MANIFEST["first_host"], "codebuddy-code")
        self.assertEqual(MANIFEST["supported_hosts"], ["codebuddy-code", "workbuddy"])
        self.assertEqual(MANIFEST["host_adapter"], "hosts/codebuddy-code.md")
        self.assertEqual(
            MANIFEST["host_adapters"],
            {
                "codebuddy-code": "hosts/codebuddy-code.md",
                "workbuddy": "hosts/workbuddy.md",
            },
        )
        self.assertEqual(MANIFEST["model_profile"], "models/hunyuan.md")
        self.assertEqual(MANIFEST["target_instruction_file"], "CODEBUDDY.md")
        self.assertEqual(MANIFEST["installer"], "scripts/install_codebuddy_code.py")
        self.assertEqual(MANIFEST["packager"], "scripts/package_workbuddy.py")

    def test_frontmatter_uses_only_documented_fields(self) -> None:
        text = read("SKILL.md")
        lines = text.splitlines()
        self.assertEqual(lines[0].strip(), "---")
        self.assertIn("name: project-health-audit", lines)
        self.assertEqual(
            MANIFEST["skill_frontmatter_fields"],
            [
                "name",
                "display_name",
                "display_name_en",
                "description",
                "description_zh",
                "description_en",
                "version",
                "author",
            ],
        )
        parts = text.split("---", 2)
        self.assertEqual(len(parts), 3)
        frontmatter = parts[1]
        for forbidden in (
            "when-to-use:",
            "license:",
            "allowed-tools:",
            "disable-model-invocation:",
            "user-invocable:",
            "context:",
            "agent:",
            "model:",
            "hooks:",
            "metadata:",
        ):
            self.assertNotIn(forbidden, frontmatter)
        self.assertNotIn("allowedTools:", text)

    def test_skill_has_no_inline_command_execution_or_privileged_fork(self) -> None:
        text = read("SKILL.md")
        self.assertIsNone(re.search(r"!`[^`\r\n]+`", text))
        self.assertNotIn("context: fork", text)

    def test_skill_name_follows_codebuddy_conventions(self) -> None:
        name = MANIFEST["name"]
        self.assertRegex(name, r"^[a-z0-9-]+$")
        self.assertLessEqual(len(name), 64)
        self.assertRegex(name, r"^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$")
        self.assertIn("显式调用：`/project-health-audit`", read("SKILL.md"))

    def test_host_adapter_contract(self) -> None:
        for relative in MANIFEST["host_adapters"].values():
            text = read(relative)
            for heading in (
                "## 识别",
                "## 安装位置",
                "## 调用与生命周期",
                "## 工具映射",
                "## 权限边界",
                "## 上下文",
                "## 目标文件",
                "## 网络与写入",
                "## 记忆标签",
                "## 未验证项",
                "## 自检清单",
            ):
                self.assertIn(heading, text, relative)
            for marker in (
                "不可信",
                "不是独立的完全只读模式",
                "才阻断",
                "项目级技能优先",
                "未验证",
            ):
                self.assertIn(marker, text, relative)

    def test_model_profile_contract(self) -> None:
        text = read(MANIFEST["model_profile"])
        for heading in (
            "## 风险分层",
            "## 需要重点测试的风险",
            "### 最优先失败模式",
            "## 强制补偿控制",
            "## 行为评测用例",
        ):
            self.assertIn(heading, text)
        self.assertIn("### HY1", text)
        self.assertIn("### HY10", text)
        self.assertIn("### HY11", text)
        self.assertIn("CodeBuddy Plan", text)
        self.assertIn("目标技能", text)
        self.assertIn("Hy4 preview", text)
        self.assertIn("hy4-preview", text)
        self.assertIn("1M", text)
        self.assertIn("过度自我验证", text)
        self.assertIn("HY4 官方已知限制", text)
        self.assertIn("通用审计风险（非 HY4 版本缺陷）", text)
        self.assertIn("不得自动继承", text)
        self.assertIn("不是 HY3 版本号", text)
        self.assertIn("HY3", text)
        self.assertNotIn("192K", text)

    def test_feedback_address_is_documented(self) -> None:
        address = "chenshuidelaye@qq.com"
        self.assertIn(address, read("README.md"))
        self.assertIn(address, read(MANIFEST["model_profile"]))
        feedback = read(MANIFEST["model_profile"]).split("## 反馈", 1)[1]
        for marker in ("你遇到的问题", "使用的模型", "使用的壳/宿主"):
            self.assertIn(marker, feedback)

    def test_validation_boundary_is_explicit(self) -> None:
        for relative in ("README.md", "README.en.md"):
            readme = read(relative)
            for marker in (
                "## 验证边界与适配状态" if relative == "README.md" else "## Validation boundary and adaptation status",
                "确定性检查" if relative == "README.md" else "deterministic checks",
                "不调用真实模型" if relative == "README.md" else "without calling a real model",
                "不等于模型行为已验证" if relative == "README.md" else "does not mean model behavior has been validated",
                "tests/model-evals/README.md",
                "WorkBuddy",
                "hy4-preview" if relative == "README.en.md" else "Hy4 preview",
            ):
                self.assertIn(marker, readme, relative)
        evals = read("tests/model-evals/README.md")
        for marker in (
            "## 验证等级",
            "deterministic",
            "documented",
            "observed",
            "validated",
            "宿主版本",
            "权限/沙箱模式",
            "未覆盖项",
        ):
            self.assertIn(marker, evals)

    def test_runtime_required_files_are_subset_of_required_files(self) -> None:
        required = set(MANIFEST["required_files"])
        runtime = set(MANIFEST["runtime_required_files"])
        self.assertTrue(runtime.issubset(required))

    def test_no_seeded_memory_or_legacy_corpus(self) -> None:
        self.assertFalse((ROOT / "PITFALLS.md").exists())
        self.assertFalse((ROOT / "PITFALLS.local.md").exists())
        for marker in (
            "windows-" + "pitfalls",
            "macos-" + "pitfalls",
            "linux-server-" + "pitfalls",
            "platform-" + "commands",
        ):
            self.assertFalse(any(ROOT.rglob(marker + "*")))

    def test_no_previous_project_identity(self) -> None:
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.name == "LICENSE":
                continue
            if ".git" in path.parts or "__pycache__" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            lowered = text.casefold()
            markers = (
                "grok-" + "grounded-audit",
                "grok-" + "build",
                "audit-" + "project-health",
            )
            for marker in markers:
                self.assertNotIn(marker, lowered, str(path.relative_to(ROOT)))

    def test_skill_references_exist(self) -> None:
        text = read("SKILL.md")
        references = set(re.findall(r"`((?:references|hosts|models|scripts)/[^`]+)`", text))
        for relative in references:
            if "<" in relative or ">" in relative:
                continue
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_no_absolute_user_paths_in_docs(self) -> None:
        patterns = (re.compile(r"[A-Za-z]:\\Users\\"), re.compile(r"/home/"))
        for path in ROOT.rglob("*.md"):
            if "tests" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in patterns:
                self.assertIsNone(pattern.search(text), str(path.relative_to(ROOT)))


if __name__ == "__main__":
    unittest.main()
