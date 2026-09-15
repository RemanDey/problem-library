#!/usr/bin/env python3
"""Sync papers/*.html into the `papers` array in index.html.

One-shot usage (run from the library root)::

    python3 tools/sync_papers.py
    python3 tools/sync_papers.py --dry-run
    python3 tools/sync_papers.py --include-template
    python3 tools/sync_papers.py --root /path/to/problem-library

Behavior:
  - Scans papers/*.html (skips example_paper.html by default).
  - Compares against `file` values in the `const papers = [...]` array.
  - For each NEW file, prompts for ALL metadata fields interactively,
    showing auto-extracted suggestions (title, description, problem count)
    that you accept with Enter or override by typing.
  - Inserts new entries (sorted by filename) into index.html, preserving
    the rest of the file byte-for-byte. Idempotent: re-runs add nothing.
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

SKIP_DEFAULT = {"example_paper.html"}
ARRAY_RE = re.compile(r"const\s+papers\s*=\s*\[", re.DOTALL)
FILE_RE = re.compile(r"""file\s*:\s*["']([^"']+)["']""")


def find_array_bounds(text):
    """Return (open_bracket_idx, close_bracket_idx) for `const papers = [...]`."""
    m = ARRAY_RE.search(text)
    if not m:
        raise SystemExit("ERROR: `const papers = [` not found in index.html")
    open_idx = m.end() - 1  # the '[' character
    depth = 0
    in_str = None
    escape = False
    for i in range(open_idx, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_str:
                in_str = None
            continue
        if ch in ("'", '"', "`"):
            in_str = ch
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return open_idx, i
    raise SystemExit("ERROR: unterminated `papers` array in index.html")


def suggest_title(html):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    title = re.sub(r"\s+", " ", m.group(1)).strip()
    # unescape common entities without importing html for speed of reading
    import html as _html

    return _html.unescape(title)


def suggest_description(html):
    import html as _html

    # <meta name="description" content="..."> in either attribute order
    patterns = [
        re.compile(
            r'<meta[^>]*\bname\s*=\s*["\']description["\'][^>]*\bcontent\s*=\s*["\'](.*?)["\']',
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r'<meta[^>]*\bcontent\s*=\s*["\'](.*?)["\']\s*[^>]*\bname\s*=\s*["\']description["\']',
            re.IGNORECASE | re.DOTALL,
        ),
    ]
    for pat in patterns:
        m = pat.search(html)
        if m:
            return _html.unescape(re.sub(r"\s+", " ", m.group(1)).strip())
    return ""


def suggest_problems(html):
    """Count distinct 'Problem N' headings; fall back to class-token count."""
    nums = re.findall(r"Problem\s+(\d+)", html)
    if nums:
        try:
            # distinct numbers is robust against solutions re-mentioning problems
            return str(len(set(int(n) for n in nums)))
        except ValueError:
            pass
    # fallback: elements whose class attribute contains the exact token `problem`
    count = 0
    for m in re.finditer(r"""class\s*=\s*["']([^"']*)["']""", html, re.IGNORECASE):
        if "problem" in m.group(1).split():
            # exclude header/body wrappers like problem-header/problem-body
            count += 1
    return str(count) if count else ""


def ask(field, suggestion=""):
    if suggestion:
        try:
            ans = input(f"  {field} [{suggestion}]: ").strip()
        except EOFError:
            ans = ""
        return ans if ans else suggestion
    try:
        return input(f"  {field}: ").strip()
    except EOFError:
        return ""


def js_str(value):
    return json.dumps(value, ensure_ascii=False)


def format_entry(meta):
    lines = [
        "      {",
        f'        title: {js_str(meta["title"])},',
        f'        file: {js_str(meta["file"])},',
        f'        category: {js_str(meta["category"])},',
        f'        level: {js_str(meta["level"])},',
        f'        difficulty: {js_str(meta["difficulty"])},',
        f'        problems: {meta["problems"]},',
        f'        year: {js_str(meta["year"])},',
        f'        description: {js_str(meta["description"])}',
        "      }",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="library root (contains index.html and papers/)")
    ap.add_argument("--dry-run", action="store_true", help="report new files without prompting or writing")
    ap.add_argument(
        "--include-template",
        action="store_true",
        help="also consider example_paper.html (skipped by default)",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    index_path = root / "index.html"
    papers_dir = root / "papers"
    if not index_path.is_file():
        raise SystemExit(f"ERROR: {index_path} not found (wrong --root?)")
    if not papers_dir.is_dir():
        raise SystemExit(f"ERROR: {papers_dir}/ not found")

    skip = set() if args.include_template else set(SKIP_DEFAULT)
    html_files = sorted(p for p in papers_dir.glob("*.html") if p.name not in skip)
    if not html_files:
        print("No paper files found in papers/ (everything skipped).")
        return 0

    text = index_path.read_text(encoding="utf-8")
    open_idx, close_idx = find_array_bounds(text)
    array_body = text[open_idx + 1 : close_idx]
    known_files = set(FILE_RE.findall(array_body))

    new_files = [p for p in html_files if f"papers/{p.name}" not in known_files]
    print(f"Found {len(html_files)} paper(s), {len(known_files)} registered, {len(new_files)} new.")
    if not new_files:
        print("Already in sync — nothing to do.")
        return 0

    print("New file(s): " + ", ".join(f"papers/{p.name}" for p in new_files))
    if args.dry_run:
        print("Dry run — index.html not modified. Run without --dry-run to add them.")
        return 0

    today_year = str(datetime.date.today().year)
    entries = []
    try:
        for path in new_files:
            html = path.read_text(encoding="utf-8", errors="replace")
            rel = f"papers/{path.name}"
            print(f"\n--- {rel} ---")
            title = ask("title", suggest_title(html))
            while not title:
                print("  title is required.")
                title = ask("title", suggest_title(html))
            category = ask("category", "")
            while not category:
                print("  category is required (e.g. Physics, Mathematics / Machine Learning, Other).")
                category = ask("category", "")
            level = ask("level", "")
            difficulty = ask("difficulty", "")
            problems_raw = ask("problems (integer)", suggest_problems(html) or "")
            while not problems_raw.isdigit():
                print("  problems must be a non-negative integer.")
                problems_raw = ask("problems (integer)", suggest_problems(html) or "")
            year = ask("year", today_year)
            description = ask("description", suggest_description(html))
            entries.append(
                {
                    "title": title,
                    "file": rel,
                    "category": category,
                    "level": level,
                    "difficulty": difficulty,
                    "problems": problems_raw,
                    "year": year,
                    "description": description,
                }
            )
    except KeyboardInterrupt:
        print("\nCancelled — index.html not modified.")
        return 130

    # Insert before the closing ']'. Ensure the previous last entry ends with ','.
    body = array_body
    block = "\n".join(format_entry(e) for e in entries)
    if body.strip():
        # add trailing comma to previous last entry if missing
        stripped = body.rstrip()
        if stripped.endswith("}"):
            body = stripped + ",\n" + block + "\n"
        else:
            # previous content already ends with ',' (or is unusual) — just append
            sep = "" if stripped.endswith(",") else ","
            body = stripped + sep + "\n" + block + "\n"
    else:
        body = "\n" + block + "\n"

    new_text = text[: open_idx + 1] + body + text[close_idx:]
    index_path.write_text(new_text, encoding="utf-8")
    print(f"\nAdded {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} to {index_path}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
