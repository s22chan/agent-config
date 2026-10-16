#!/usr/bin/env python3
"""PreToolUse guard: send Python symbol lookups to the LSP instead of text search.

Denies a Grep, Glob, or Bash grep/rg/git-grep call whose pattern is a Python
symbol (a name the LSP can resolve) and whose target can include Python files.
A symbol is a name with an underscore or an uppercase letter that the repository
defines as a `def` or `class`. Everything else passes: literals, phrases, config
and docs, non-Python globs, and names the repository does not define (keyword
arguments, library methods). Lexical, not a shell parser: a call it cannot parse
is allowed. Set LSP_FIRST_GUARD=off to disable.
"""

import json
import os
import re
import shlex
import subprocess
import sys

NON_CODE_EXT = (
    "md|txt|log|json|jsonl|yaml|yml|toml|ini|cfg|env|csv|tsv|sql|sh|css|html|xml|rst|lock"
)
NON_CODE_PATH = re.compile(
    r"(^|/)(\.claude|\.git|\.pixi|node_modules|docs?|logs?)(/|$)|\.(" + NON_CODE_EXT + r")$"
)
SEARCH_COMMANDS = {"grep", "egrep", "fgrep", "rg", "ag", "ack"}
FLAGS_WITH_VALUE = {
    "-e", "-f", "-g", "-t", "-T", "-m", "-A", "-B", "-C", "-d", "-D", "-j",
    "--glob", "--iglob", "--type", "--type-not", "--type-add", "--include",
    "--exclude", "--exclude-dir", "--max-count", "--context", "--after-context",
    "--before-context", "--max-depth", "--threads", "--color", "--colors",
    "--regexp", "--file", "--sort", "--sortr", "-M", "--max-columns",
}
GLOB_FLAGS = {"-g", "--glob", "--iglob", "--include"}
TYPE_FLAGS = {"-t", "--type"}
ALLOW_WORDS = {"TODO", "FIXME", "HACK", "NOTE", "XXX", "BUG"}
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DEFINE_PREFIX = re.compile(r"^(def|class)\s+")


def reduce_to_identifier(alternative):
    """Return (identifier, is_definition_lookup) or (None, False)."""
    text = alternative.strip().strip("'\"")
    text = re.sub(r"^(\^|\\b|\\<)+", "", text)
    text = re.sub(r"(\$|\\b|\\>)+$", "", text)
    is_definition = False
    match = DEFINE_PREFIX.match(text.replace("\\s+", " ").replace("\\s*", " "))
    if match:
        is_definition = True
        text = text.replace("\\s+", " ").replace("\\s*", " ")[match.end():]
    text = re.sub(r"^\\\.", "", text)
    text = re.sub(r"(\\\(|\(|\\s\*\(|\\s\*)+$", "", text)
    text = re.sub(r"^(\\b|\\<)+|(\\b|\\>)+$", "", text)
    return (text, is_definition) if IDENT.match(text) else (None, False)


def defined_in_repo(name, cwd):
    """True when the repository defines `name` as a Python function or class a few times."""
    try:
        out = subprocess.run(
            ["git", "grep", "-cE", rf"^\s*(def|class)\s+{name}\b", "--", "*.py"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        ).stdout
    except Exception:
        return False
    return 1 <= sum(int(line.rsplit(":", 1)[1]) for line in out.splitlines() if ":" in line) <= 8


def is_symbol(name, cwd):
    """A symbol the LSP can resolve: a defined name that is not an ordinary word or constant."""
    if len(name) < 5 or name in ALLOW_WORDS or re.fullmatch(r"[A-Z0-9_]+", name):
        return False
    return ("_" in name or any(c.isupper() for c in name)) and defined_in_repo(name, cwd)


def pattern_symbols(pattern, cwd):
    found = []
    for alternative in re.split(r"\\\||\|", pattern):
        name, is_definition = reduce_to_identifier(alternative)
        if name and is_symbol(name, cwd):
            found.append((name, is_definition))
    return found


def targets_non_python(glob, type_, paths):
    if type_ and type_.lower() not in {"py", "python", "pyi"}:
        return True
    if glob and re.search(r"\.(" + NON_CODE_EXT + r")\b", glob) and ".py" not in glob:
        return True
    paths = [p for p in paths if p]
    return bool(paths) and all(NON_CODE_PATH.search(p) for p in paths)


def deny(symbols):
    names = ", ".join(sorted({name for name, _ in symbols}))
    lookup = any(is_definition for _, is_definition in symbols)
    advice = (
        "Use the LSP tool: `workspaceSymbol` with the name to find its definition."
        if lookup
        else "Use the LSP tool: `findReferences` or `incomingCalls` (a call site gives `goToDefinition`)."
    )
    reason = (
        f"LSP-first: `{names}` is a Python symbol. {advice} Text search matches "
        "same-named functions, comments and strings, and truncates its output, so a "
        "caller list from it is incomplete. To search for the text itself, quote a "
        "phrase or restrict the search to non-Python files."
    )
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


def bash_searches(command):
    """Yield (pattern, glob, type, paths) for each grep-like segment."""
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return
    segments, current = [], []
    for token in tokens:
        if token in {"|", ";", "&&", "||", "&"}:
            segments.append(current)
            current = []
        else:
            current.append(token)
    segments.append(current)
    for words in segments:
        if words[:1] == ["git"] and "grep" in words[1:3]:
            words = words[words.index("grep"):]
        if not words or os.path.basename(words[0]) not in SEARCH_COMMANDS:
            continue
        pattern, glob, type_, positional, i = None, None, None, [], 1
        while i < len(words):
            word = words[i]
            flag, _, inline = word.partition("=") if word.startswith("--") else (word, "", "")
            if word.startswith("-") and len(word) > 1:
                value = inline if inline else (words[i + 1] if flag in FLAGS_WITH_VALUE and i + 1 < len(words) else None)
                if flag in {"-e", "--regexp"} and value is not None:
                    pattern = pattern or value
                if flag in GLOB_FLAGS:
                    glob = value
                if flag in TYPE_FLAGS:
                    type_ = value
                i += 2 if (flag in FLAGS_WITH_VALUE and not inline) else 1
            else:
                positional.append(word)
                i += 1
        if pattern is None and positional:
            pattern, positional = positional[0], positional[1:]
        if pattern:
            yield pattern, glob, type_, positional


def main():
    if os.environ.get("LSP_FIRST_GUARD", "").lower() == "off":
        return
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    cwd = data.get("cwd") or os.getcwd()
    tool, tool_input = data.get("tool_name"), data.get("tool_input") or {}
    searches = []
    if tool == "Grep":
        searches.append((str(tool_input.get("pattern", "")), tool_input.get("glob"),
                         tool_input.get("type"), [tool_input.get("path")]))
    elif tool == "Glob":
        glob = str(tool_input.get("pattern", ""))
        # A symbol-shaped filename search (`*create_submitit_executor*`) bypasses the Grep guard.
        for part in re.split(r"[*?/\\{},\[\]]+", glob):
            name = re.sub(r"\.py$", "", part)
            if name and is_symbol(name, cwd) and not targets_non_python(None, None, [part]):
                deny([(name, False)])
                return
        return
    elif tool == "Bash":
        searches.extend(bash_searches(str(tool_input.get("command", ""))))
    for pattern, glob, type_, paths in searches:
        if not pattern or targets_non_python(glob, type_, paths):
            continue
        symbols = pattern_symbols(pattern, cwd)
        if symbols:
            deny(symbols)
            return


if __name__ == "__main__":
    main()
