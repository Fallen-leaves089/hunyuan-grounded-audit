from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "package_workbuddy.py"
SKILL_NAME = "project-health-audit"


def run_packager(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


class WorkBuddyPackageTests(unittest.TestCase):
    def test_package_has_one_workbuddy_root_and_runtime_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "skill.zip"
            result = run_packager("--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.is_file())
            with zipfile.ZipFile(output) as archive:
                names = archive.namelist()
                roots = {name.split("/", 1)[0] for name in names}
                self.assertEqual(roots, {SKILL_NAME})
                for relative in (
                    "SKILL.md",
                    "skill.json",
                    "hosts/workbuddy.md",
                    "hosts/codebuddy-code.md",
                    "models/hunyuan.md",
                    "README.md",
                    "README.en.md",
                    "LICENSE",
                ):
                    self.assertIn(f"{SKILL_NAME}/{relative}", names)
                self.assertFalse(any("/tests/" in name for name in names))
                self.assertFalse(any("/.git/" in name for name in names))
                skill = archive.read(f"{SKILL_NAME}/SKILL.md").decode("utf-8")
                self.assertIn("display_name:", skill)
                self.assertIn("display_name_en:", skill)
                self.assertNotIn("allowed-tools:", skill.split("---", 2)[1])

    def test_package_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first.zip"
            second = Path(temporary) / "second.zip"
            first_result = run_packager("--output", str(first))
            second_result = run_packager("--output", str(second))

            self.assertEqual(first_result.returncode, 0, first_result.stderr)
            self.assertEqual(second_result.returncode, 0, second_result.stderr)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_output_must_be_a_zip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "skill.txt"
            result = run_packager("--output", str(output))

            self.assertEqual(result.returncode, 2)
            self.assertIn("must end with .zip", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
