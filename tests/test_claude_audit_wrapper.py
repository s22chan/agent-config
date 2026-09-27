import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "adapters/claude/scripts/audit-change"


class ClaudeAuditWrapperTest(unittest.TestCase):
    def test_applies_default_and_explicit_hard_budgets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            uv = shutil.which("uv")
            self.assertIsNotNone(uv)
            binary = root / "bin"
            binary.mkdir()
            captured = root / "arguments"
            response = root / "response.json"
            response.write_text(
                json.dumps(
                    {
                        "result": "verified audit result",
                        "total_cost_usd": 1.25,
                        "usage": {
                            "input_tokens": 0,
                            "cache_creation_input_tokens": 0,
                            "cache_read_input_tokens": 0,
                            "output_tokens": 0,
                        },
                        "modelUsage": {
                            "claude-opus": {
                                "inputTokens": 10,
                                "cacheCreationInputTokens": 20,
                                "cacheReadInputTokens": 70,
                                "outputTokens": 5,
                                "costUSD": 1.0,
                            }
                        },
                    }
                )
            )
            claude = binary / "claude"
            claude.write_text(
                "#!/usr/bin/env bash\n"
                "printf '%s\\0' \"$@\" > \"$CAPTURED_ARGUMENTS\"\n"
                "cat \"$CLAUDE_RESPONSE\"\n"
            )
            claude.chmod(0o750)
            environment = {
                "CAPTURED_ARGUMENTS": str(captured),
                "CLAUDE_RESPONSE": str(response),
                "PATH": f"{binary}:{Path(uv).parent}:/usr/bin:/bin",
            }

            default = subprocess.run(
                [str(WRAPPER), "docs"],
                check=False,
                capture_output=True,
                env=environment,
                text=True,
            )
            self.assertEqual(default.returncode, 0, default.stderr)
            self.assertEqual(default.stdout, "verified audit result\n")
            self.assertIn(
                "audit usage: input=10 cache_write=20 cache_read=70 "
                "cache_read_share=70.0% output=5 cost=$1.2500",
                default.stderr,
            )
            self.assertIn("audit usage [claude-opus]", default.stderr)
            self.assertEqual(
                captured.read_bytes().split(b"\0")[:-1],
                [
                    b"-p", b"--max-budget-usd", b"5",
                    b"--output-format", b"json",
                    b"--exclude-dynamic-system-prompt-sections", b"/audit docs",
                ],
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
                [
                    b"-p", b"--max-budget-usd", b"3.5",
                    b"--output-format", b"json",
                    b"--exclude-dynamic-system-prompt-sections",
                    b"/audit docs full tracked tree",
                ],
            )


if __name__ == "__main__":
    unittest.main()
