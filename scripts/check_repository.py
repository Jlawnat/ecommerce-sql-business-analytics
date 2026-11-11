"""Dependency-free repository documentation, privacy, and CI checks."""

from __future__ import annotations

import re
import struct
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_LINK_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
FENCED_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)


def markdown_files(root: Path) -> list[Path]:
    excluded = {".git", ".venv", "node_modules", ".next"}
    return sorted(path for path in root.rglob("*.md") if not excluded.intersection(path.parts))


def _strip_link_title(value: str) -> str:
    value = value.strip()
    if value.startswith("<") and ">" in value:
        return value[1:value.index(">")]
    return value.split(maxsplit=1)[0]


def _github_slug(value: str) -> str:
    value = re.sub(r"!?\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[`*_~]", "", value).strip().lower()
    value = re.sub(r"[^\w\- ]", "", value, flags=re.UNICODE)
    return re.sub(r"-+", "-", value.replace(" ", "-")).strip("-")


def _anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for heading in HEADING_RE.findall(path.read_text(encoding="utf-8")):
        base = _github_slug(heading)
        index = counts.get(base, 0)
        counts[base] = index + 1
        anchors.add(base if index == 0 else f"{base}-{index}")
    return anchors


def check_markdown_links(root: Path, files: list[Path] | None = None) -> list[str]:
    errors: list[str] = []
    files = files or markdown_files(root)
    anchor_cache: dict[Path, set[str]] = {}
    for document in files:
        text = document.read_text(encoding="utf-8")
        searchable = FENCED_BLOCK_RE.sub("", text)
        targets = LINK_RE.findall(searchable) + REFERENCE_LINK_RE.findall(searchable)
        for raw_target in targets:
            target = unquote(_strip_link_title(raw_target))
            if not target or target.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            path_text, separator, anchor = target.partition("#")
            resolved = document if not path_text else (document.parent / path_text).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{document.relative_to(root)}: link escapes repository: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{document.relative_to(root)}: missing target: {target}")
                continue
            if separator and anchor and resolved.suffix.lower() == ".md":
                anchors = anchor_cache.setdefault(resolved, _anchors(resolved))
                if anchor.lower() not in anchors:
                    errors.append(f"{document.relative_to(root)}: missing heading anchor: {target}")
    return errors


def check_mermaid_blocks(files: list[Path]) -> list[str]:
    errors: list[str] = []
    valid_headers = ("flowchart LR", "flowchart TD", "flowchart TB", "flowchart RL", "sequenceDiagram", "erDiagram", "stateDiagram", "gantt")
    for document in files:
        text = document.read_text(encoding="utf-8")
        starts = text.count("```mermaid")
        blocks = MERMAID_RE.findall(text)
        if starts != len(blocks):
            errors.append(f"{document}: unclosed Mermaid block")
        for index, block in enumerate(blocks, start=1):
            source = block.strip()
            if not source.startswith(valid_headers):
                errors.append(f"{document}: Mermaid block {index} has unsupported or missing header")
            if "\\n" in source:
                errors.append(f"{document}: Mermaid block {index} contains a literal \\n")
            if re.search(r"<\/?[a-zA-Z][^>]*>", source):
                errors.append(f"{document}: Mermaid block {index} contains HTML")
            subgraphs = len(re.findall(r"^\s*subgraph\b", source, re.MULTILINE))
            endings = len(re.findall(r"^\s*end\s*$", source, re.MULTILINE))
            if subgraphs != endings:
                errors.append(f"{document}: Mermaid block {index} has unbalanced subgraphs")
    return errors


def check_markdown_structure(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for document in files:
        text = document.read_text(encoding="utf-8")
        if text.count("```") % 2:
            errors.append(f"{document}: unclosed fenced code block")
        level_one = re.findall(r"^#\s+\S", FENCED_BLOCK_RE.sub("", text), re.MULTILINE)
        if len(level_one) != 1:
            errors.append(f"{document}: expected exactly one level-one heading, found {len(level_one)}")
    return errors


def check_privacy_paths(paths: list[str]) -> list[str]:
    errors: list[str] = []
    forbidden_extensions = {".db", ".sqlite", ".sqlite3", ".db-journal", ".db-wal", ".db-shm"}
    secret_names = {"kaggle.json", "id_rsa", "id_ed25519", ".npmrc"}
    for raw_path in paths:
        normalized = raw_path.replace("\\", "/")
        if normalized.startswith("./"):
            normalized = normalized[2:]
        parts = tuple(part for part in normalized.split("/") if part)
        name = parts[-1] if parts else normalized
        suffix = Path(name).suffix.lower()
        reason = None
        if "node_modules" in parts or ".next" in parts or name.endswith(".tsbuildinfo"):
            reason = "generated frontend artifact"
        elif normalized.startswith("data/raw/") and name != ".gitkeep":
            reason = "licensed raw data"
        elif normalized.startswith("data/processed/") and name != ".gitkeep":
            reason = "generated database or processed data"
        elif suffix in forbidden_extensions:
            reason = "database file"
        elif name == ".env" or (name.startswith(".env.") and name != ".env.example"):
            reason = "environment secret file"
        elif name.lower() in secret_names or normalized.startswith("secrets/"):
            reason = "credential file"
        elif normalized.startswith(".taste-skill/"):
            reason = "local design cache"
        if reason:
            errors.append(f"{raw_path}: {reason}")
    return errors


def _candidate_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    )
    return [item.decode() for item in result.stdout.split(b"\0") if item]


def _tracked_paths(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "-z"],
        check=True,
        capture_output=True,
    )
    return {item.decode() for item in result.stdout.split(b"\0") if item}


def check_sensitive_content(root: Path, paths: list[str]) -> list[str]:
    errors: list[str] = []
    secret_patterns = {
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "GitHub token": re.compile(r"\bgh[oprsu]_[A-Za-z0-9_]{30,}\b"),
    }
    frontend_identifier = re.compile(r"\b(?:customer_id|order_id|seller_id|review_id)\b", re.IGNORECASE)
    for relative in paths:
        path = root / relative
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for label, pattern in secret_patterns.items():
            if pattern.search(text):
                errors.append(f"{relative}: possible {label}")
        if (relative.startswith("web/public/") or relative.startswith("web/app/") or relative.startswith("web/components/")) and frontend_identifier.search(text):
            errors.append(f"{relative}: row-level identifier referenced by public frontend")
    return errors


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as source:
        header = source.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", header[16:24])


def check_readme_screenshots(root: Path, tracked_paths: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    readme = root / "README.md"
    if not readme.is_file():
        return ["README.md is missing"]
    for raw_target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme.read_text(encoding="utf-8")):
        target = _strip_link_title(raw_target).partition("#")[0]
        if not target.startswith("visualizations/screenshots/v2/") or not target.endswith(".png"):
            continue
        path = root / target
        if not path.is_file():
            errors.append(f"README.md: missing screenshot: {target}")
            continue
        if tracked_paths is not None and target not in tracked_paths:
            errors.append(f"README.md: screenshot is not tracked by Git: {target}")
        dimensions = _png_dimensions(path)
        if dimensions is None:
            errors.append(f"README.md: invalid PNG screenshot: {target}")
        elif dimensions[0] < 768 or dimensions[1] < 600:
            errors.append(f"README.md: screenshot is too small for portfolio use: {target} {dimensions[0]}x{dimensions[1]}")
    return errors


def check_ci_definition(root: Path) -> list[str]:
    workflow = root / ".github/workflows/ci.yml"
    if not workflow.is_file():
        return [".github/workflows/ci.yml is missing"]
    text = workflow.read_text(encoding="utf-8")
    required = (
        "permissions:",
        "contents: read",
        "scripts/check_repository.py",
        "tests.test_repository_hygiene",
        "npm ci",
        "npm run typecheck",
        "npm run lint",
        "npm run build",
    )
    return [f".github/workflows/ci.yml: missing required command or policy: {token}" for token in required if token not in text]


def run(root: Path = PROJECT_ROOT) -> list[str]:
    files = markdown_files(root)
    paths = _candidate_paths(root)
    tracked_paths = _tracked_paths(root)
    errors = []
    errors.extend(check_markdown_links(root, files))
    errors.extend(check_markdown_structure(files))
    errors.extend(check_mermaid_blocks(files))
    errors.extend(check_privacy_paths(paths))
    errors.extend(check_sensitive_content(root, paths))
    errors.extend(check_readme_screenshots(root, tracked_paths))
    errors.extend(check_ci_definition(root))
    if errors:
        return errors
    print(f"Repository checks passed: {len(files)} Markdown files, {sum(path.read_text(encoding='utf-8').count('```mermaid') for path in files)} Mermaid blocks, {len(paths)} visible files.")
    return []


if __name__ == "__main__":
    failures = run()
    for failure in failures:
        print(f"ERROR: {failure}", file=sys.stderr)
    raise SystemExit(1 if failures else 0)
