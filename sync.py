#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
INSTRUCTIONS = ROOT / "instructions"
INCLUDE = re.compile(r'^<!-- include: ([^/][^>]*) -->$')
GENERATED_HEADER = (
    "<!-- Generated from ~/agent-config; edit the source templates there. -->\n"
)
TARGETS = {
    Path(".codex/AGENTS.md"): INSTRUCTIONS / "codex.md.in",
    Path(".claude/CLAUDE.md"): INSTRUCTIONS / "claude.md.in",
}
SHARED_FILES = {
    Path("skills/design-diagnostic-visualizations/SKILL.md"): (
        ROOT / "shared/skills/design-diagnostic-visualizations/SKILL.md"
    ),
    Path(
        "skills/run-slurm-wandb-experiments/references/evorun-environment.md"
    ): (
        ROOT
        / "shared/skills/run-slurm-wandb-experiments/references/evorun-environment.md"
    ),
}


def render(template: Path) -> str:
    rendered = [GENERATED_HEADER]
    for line in template.read_text().splitlines(keepends=True):
        match = INCLUDE.fullmatch(line.rstrip("\n"))
        if match is None:
            rendered.append(line)
            continue
        include = (INSTRUCTIONS / match.group(1)).resolve()
        if include.parent != INSTRUCTIONS.resolve():
            raise ValueError(f"include escapes instructions directory: {include}")
        text = include.read_text()
        rendered.append(text if text.endswith("\n") else text + "\n")
    return "".join(rendered)


def replace_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, delete=False, prefix=f".{path.name}.",
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    os.chmod(temporary_path, 0o640)
    os.replace(temporary_path, path)


def expected_links(home: Path) -> dict[Path, Path]:
    links = {}
    for relative, source in SHARED_FILES.items():
        links[home / ".codex" / relative] = source
        links[home / ".claude" / relative] = source
    return links


def check(home: Path) -> list[str]:
    errors = []
    for relative, template in TARGETS.items():
        target = home / relative
        if not target.is_file() or target.read_text() != render(template):
            errors.append(f"out of date: {target}")
    for target, source in expected_links(home).items():
        relative_source = os.path.relpath(source, start=target.parent)
        if not target.is_symlink() or os.readlink(target) != relative_source:
            errors.append(f"out of date: {target}")
    return errors


def sync(home: Path) -> None:
    for relative, template in TARGETS.items():
        replace_file(home / relative, render(template))
    for target, source in expected_links(home).items():
        target.parent.mkdir(parents=True, exist_ok=True)
        relative_source = os.path.relpath(source, start=target.parent)
        if target.is_symlink() and os.readlink(target) == relative_source:
            continue
        if target.exists() or target.is_symlink():
            target.unlink()
        target.symlink_to(relative_source)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--home", type=Path, default=Path.home())
    args = parser.parse_args()
    if args.check:
        errors = check(args.home)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        return 0
    sync(args.home)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
