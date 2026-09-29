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
            captured_evidence = root / "evidence"
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
                "printf '%s' \"$S22CHAN_AUDIT_EVIDENCE_DIR\" > \"$CAPTURED_EVIDENCE\"\n"
                "touch \"$S22CHAN_AUDIT_EVIDENCE_DIR/scope-index.md\"\n"
                "cat \"$CLAUDE_RESPONSE\"\n"
            )
            claude.chmod(0o750)
            environment = {
                "CAPTURED_ARGUMENTS": str(captured),
                "CAPTURED_EVIDENCE": str(captured_evidence),
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
            arguments = self.arguments(captured)
            self.assertEqual(
                arguments[:7],
                [
                    "-p", "--max-budget-usd", "5",
                    "--output-format", "json",
                    "--exclude-dynamic-system-prompt-sections", "--add-dir",
                ],
            )
            self.assertEqual(arguments[-2:], ["--", "/audit docs"])
            evidence = Path(captured_evidence.read_text())
            self.assertEqual(arguments[7], str(evidence))
            allowed = arguments[
                arguments.index("--allowedTools") + 1 : arguments.index("--disallowedTools")
            ]
            denied = arguments[arguments.index("--disallowedTools") + 1 : -2]
            self.assertIn(f"Write(/{evidence}/**)", allowed)
            self.assertIn("Bash(git diff:*)", allowed)
            self.assertNotIn("Bash(git branch:*)", allowed)
            self.assertNotIn("Bash(python3:*)", allowed)
            self.assertIn(f"Write(/{Path.cwd().resolve()}/**)", denied)
            self.assertFalse(evidence.exists(), "evidence is removed after success")

            explicit = subprocess.run(
                [str(WRAPPER), "--budget-usd", "3.5", "docs", "full tracked tree"],
                check=False,
                capture_output=True,
                env=environment,
                text=True,
            )
            self.assertEqual(explicit.returncode, 0, explicit.stderr)
            arguments = self.arguments(captured)
            self.assertEqual(arguments[:3], ["-p", "--max-budget-usd", "3.5"])
            self.assertEqual(arguments[-2:], ["--", "/audit docs full tracked tree"])

    def test_failed_run_keeps_evidence_for_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            uv = shutil.which("uv")
            self.assertIsNotNone(uv)
            binary = root / "bin"
            binary.mkdir()
            claude = binary / "claude"
            claude.write_text(
                "#!/usr/bin/env bash\n"
                "touch \"$S22CHAN_AUDIT_EVIDENCE_DIR/scope-index.md\"\n"
                "exit 3\n"
            )
            claude.chmod(0o750)
            failed = subprocess.run(
                [str(WRAPPER), "docs"],
                check=False,
                capture_output=True,
                env={"PATH": f"{binary}:{Path(uv).parent}:/usr/bin:/bin"},
                text=True,
            )
            self.assertEqual(failed.returncode, 3)
            kept = Path(failed.stderr.rsplit("audit evidence kept at ", 1)[1].strip())
            self.assertTrue((kept / "scope-index.md").exists())
            shutil.rmtree(kept)

    @staticmethod
    def arguments(captured: Path) -> list[str]:
        return [item.decode() for item in captured.read_bytes().split(b"\0")[:-1]]


if __name__ == "__main__":
    unittest.main()
