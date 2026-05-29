#!/usr/bin/env python3
"""Convert GitHub-flavored markdown links back to Obsidian wikilinks.

Reverse of obsidian_to_github.py. Transforms:

  [Heading](#slug)                -> [[#Heading]]               (when text == heading)
  [Alias](#slug)                  -> [[#Heading|Alias]]
  [File](File.md)                 -> [[File]]                   (when text == file stem)
  [Alias](File.md)                -> [[File|Alias]]
  [File > Heading](File.md#slug)  -> [[File#Heading]]           (when text == "File > Heading")
  [Alias](File.md#slug)           -> [[File#Heading|Alias]]

Only local markdown links are touched:
  - same-file anchor links (#...)
  - relative paths ending in .md (with optional anchor)
External links (http(s)://, mailto:, ftp://, //) and non-.md paths pass through.

Usage:
  cat file.md | github_to_obsidian.py               # stdin -> stdout
  github_to_obsidian.py file.md                     # rewrite in place
  github_to_obsidian.py --check file.md             # exit 1 if would change
  github_to_obsidian.py --repo-root . file.md       # override repo root
"""

import argparse
import re
import sys
import urllib.parse
from pathlib import Path

MD_LINK_RE = re.compile(r"\[([^\]\n]+?)\]\(([^)\n]+?)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)

EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "ftp://", "ftps://", "//")


def slugify(text: str) -> str:
    """Match GitHub's heading-anchor slug rules.

    Mirrors scripts/obsidian_to_github.py so that round-tripping is stable.
    """
    text = text.lower()
    text = re.sub(r"[^\w\- ]+", "", text, flags=re.UNICODE)
    text = text.replace(" ", "-")
    return text


def extract_slug_map(content: str) -> dict[str, str]:
    """Return {slug: heading_text} for every markdown heading in content.

    Duplicate slugs keep the first heading (matches how forward conversion picks).
    """
    out: dict[str, str] = {}
    for m in HEADING_RE.finditer(content):
        text = m.group(1)
        out.setdefault(slugify(text), text)
    return out


def find_repo_md_files(repo_root: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for p in repo_root.rglob("*.md"):
        if ".git" in p.parts:
            continue
        out.setdefault(p.stem, p)
    return out


def _read_text(path: Path) -> str | None:
    try:
        return path.read_bytes().decode("utf-8")
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        return None


def make_converter(content: str, repo_root: Path | None):
    same_file_slugs = extract_slug_map(content)
    md_index: dict[str, Path] = find_repo_md_files(repo_root) if repo_root else {}
    cross_cache: dict[str, dict[str, str]] = {}

    def cross_file_slugs(stem: str) -> dict[str, str]:
        if stem not in cross_cache:
            target = md_index.get(stem)
            if target is None:
                cross_cache[stem] = {}
            else:
                text = _read_text(target) or ""
                cross_cache[stem] = extract_slug_map(text)
        return cross_cache[stem]

    def convert(match: re.Match) -> str:
        text = match.group(1)
        url = match.group(2).strip()

        # External or absolute - leave alone.
        if url.startswith(EXTERNAL_PREFIXES):
            return match.group(0)

        # Same-file anchor.
        if url.startswith("#"):
            slug = url[1:]
            heading = same_file_slugs.get(slug)
            if heading is None:
                return match.group(0)
            if text == heading:
                return f"[[#{heading}]]"
            return f"[[#{heading}|{text}]]"

        # File link (with or without anchor).
        if "#" in url:
            file_part, slug = url.split("#", 1)
        else:
            file_part, slug = url, None

        file_decoded = urllib.parse.unquote(file_part)
        if not file_decoded.endswith(".md"):
            return match.group(0)

        stem = Path(file_decoded).stem

        if slug:
            heading = cross_file_slugs(stem).get(slug)
            if heading:
                expected_text = f"{stem} > {heading}"
                if text == expected_text:
                    return f"[[{stem}#{heading}]]"
                return f"[[{stem}#{heading}|{text}]]"
            # Slug couldn't be resolved - fall through to file-only link.

        if text == stem:
            return f"[[{stem}]]"
        return f"[[{stem}|{text}]]"

    return convert


def convert_text(content: str, repo_root: Path | None = None) -> str:
    return MD_LINK_RE.sub(make_converter(content, repo_root), content)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", nargs="?", help="File to rewrite in place (default: stdin -> stdout)")
    ap.add_argument("--source-path", help="Accepted for symmetry with obsidian_to_github.py; unused here")
    ap.add_argument("--repo-root", help="Repo root for cross-file resolution (default: git toplevel or CWD)")
    ap.add_argument("--check", action="store_true", help="Exit non-zero if conversion would change content")
    args = ap.parse_args(argv)

    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        import subprocess

        try:
            top = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                stderr=subprocess.DEVNULL,
            ).decode().strip()
            repo_root = Path(top)
        except Exception:
            repo_root = Path.cwd()

    if args.file:
        path = Path(args.file).resolve()
        original = path.read_bytes().decode("utf-8")
    else:
        original = sys.stdin.buffer.read().decode("utf-8")

    converted = convert_text(original, repo_root=repo_root)

    if args.check:
        return 0 if converted == original else 1

    if args.file:
        if converted != original:
            Path(args.file).write_bytes(converted.encode("utf-8"))
    else:
        sys.stdout.buffer.write(converted.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
