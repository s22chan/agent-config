from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "adapters/claude/scripts/audit-change"


class ClaudeAuditWrapperTest(unittest.TestCase):
    def test_applies_default_and_explicit_hard_budgets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "bin"
            binary.mkdir()
            captured = root / "arguments"
            claude = binary / "claude"
            claude.write_text(
                "#!/usr/bin/env bash\n"
                "printf '%s\\0' \"$@\" > \"$CAPTURED_ARGUMENTS\"\n"
            )
            claude.chmod(0o750)
            environment = {
                "CAPTURED_ARGUMENTS": str(captured),
                "PATH": f"{binary}:/usr/bin:/bin",
            }

            default = subprocess.run(
                [str(WRAPPER), "docs"],
                check=False,
                capture_output=True,
                env=environment,
                text=True,
            )
            self.assertEqual(default.returncode, 0, default.stderr)
            self.assertEqual(
                captured.read_bytes().split(b"\0")[:-1],
                [b"-p", b"--max-budget-usd", b"5", b"/audit docs"],
            )

            explicit = subprocess.run(
                [str(WRAPPER), "--budget-usd", "3.5", "docs", "full tracked tree"],
                check=False,
                capture_output=True,
                env=environment,
                text=True,
            )
            self.assertEqual(explicit.returncode, 0, explicit.stderr)
            self.assertEqual(
                captured.read_bytes().split(b"\0")[:-1],
                [b"-p", b"--max-budget-usd", b"3.5", b"/audit docs full tracked tree"],
            )


if __name__ == "__main__":
    unittest.main()
