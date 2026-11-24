#!/usr/bin/env python3
"""Knowledge Wiki provenance, frontmatter schema, and privacy leak validator for Mythos Clio."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_FRONTMATTER_KEYS = ("title", "created", "curator", "tags")
SOURCES_HEADING_RE = re.compile(r"^##\s+(Sources & References|References)\s*$", re.MULTILINE)
MARKDOWN_URL_RE = re.compile(r"\[[^\]]+\]\(https?://[^)\s]+\)")
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

PRIVACY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_ipv4_192_168", re.compile(r"\b192\.168\.\d{1,3}\.\d{1,3}\b")),
    ("private_ipv4_10", re.compile(r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")),
    ("tailscale_cgnat_ip", re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}\b")),
    ("windows_user_path", re.compile(r"[A-Za-z]:\\Users\\[^\s`\"']+")),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{16,}\b")),
    ("api_secret_prefix", re.compile(r"\b(?:sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
)


def _extract_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return None

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])
    meta: dict[str, str] = {}
    current_key: str | None = None
    for raw_line in fm_lines:
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        if ":" in raw_line and not raw_line.startswith((" ", "\t", "-")):
            key, val = raw_line.split(":", 1)
            current_key = key.strip()
            meta[current_key] = val.strip()
        elif current_key and raw_line.lstrip().startswith("-"):
            existing = meta.get(current_key, "")
            item = raw_line.lstrip()[1:].strip()
            meta[current_key] = f"{existing}, {item}".strip(", ")
    return meta, body


def _extract_sources_section(body: str) -> str | None:
    match = SOURCES_HEADING_RE.search(body)
    if not match:
        return None
    rest = body[match.end() :]
    next_h2 = re.search(r"^##\s+", rest, re.MULTILINE)
    return rest[: next_h2.start()] if next_h2 else rest


def validate_file(path: Path, strict: bool = False) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    errors: list[str] = []
    warnings: list[str] = []

    parsed = _extract_frontmatter(text)
    if parsed is None:
        errors.append("Missing or unclosed YAML frontmatter ('---').")
        body = text
    else:
        meta, body = parsed
        for key in REQUIRED_FRONTMATTER_KEYS:
            if not meta.get(key):
                errors.append(f"Missing required frontmatter key '{key}'.")
        if strict and meta.get("language") and meta.get("language") != "en-US":
            warnings.append(f"Frontmatter language is '{meta['language']}' (expected 'en-US').")

    sources_block = _extract_sources_section(body)
    if sources_block is None:
        errors.append("Missing '## Sources & References' (or '## References') section.")
    else:
        if not MARKDOWN_URL_RE.search(sources_block):
            errors.append("Sources section must include at least one '[Title](https://...)' hyperlink.")
        if not ISO_DATE_RE.search(sources_block):
            msg = "Sources section does not include an ISO YYYY-MM-DD date."
            if strict:
                errors.append(msg)
            else:
                warnings.append(msg)

    for label, pattern in PRIVACY_PATTERNS:
        if pattern.search(text):
            errors.append(f"Privacy/security check failed ({label}).")

    return {
        "file": str(path),
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def _collect_markdown_files(raw_paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in raw_paths:
        target = Path(raw)
        if not target.exists():
            raise FileNotFoundError(f"Path not found: {raw}")
        if target.is_file():
            files.append(target)
        else:
            files.extend(sorted(p for p in target.rglob("*.md") if p.is_file()))
    return files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Mythos Knowledge Wiki Markdown notes for frontmatter, source provenance, and privacy hygiene."
    )
    parser.add_argument("paths", nargs="+", help="Markdown file(s) or directory(ies) to validate.")
    parser.add_argument("--strict", action="store_true", help="Require ISO dates in Sources section and check language tag.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        files = _collect_markdown_files(args.paths)
        if not files:
            raise ValueError("No Markdown (.md) files found in the specified path(s).")
        results = [validate_file(path, strict=args.strict) for path in files]
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    passed = sum(1 for item in results if item["valid"])
    failed = len(results) - passed
    payload = {"total": len(results), "passed": passed, "failed": failed, "results": results}

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for item in results:
            status = "PASS" if item["valid"] else "FAIL"
            print(f"[{status}] {item['file']}")
            for err in item["errors"]:
                print(f"  - ERROR: {err}")
            for warn in item["warnings"]:
                print(f"  - WARN:  {warn}")
        print(f"Summary: {passed}/{len(results)} passed, {failed} failed.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
