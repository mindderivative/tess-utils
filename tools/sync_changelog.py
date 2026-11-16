"""Keep ``docs/changelog.md`` in step with ``CHANGELOG.md``.

MkDocs builds only what is under ``docs/``, so the site's changelog page is a copy of the
repository's ``CHANGELOG.md`` with a short header.

    python3 tools/sync_changelog.py           # rewrite docs/changelog.md
    python3 tools/sync_changelog.py --check   # exit 1 if it is out of date (CI runs this)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CHANGELOG.md"
TARGET = ROOT / "docs" / "changelog.md"

HEADER = """# Changelog

The changelog is `CHANGELOG.md` in the repository root; this page is a copy kept for the site
(MkDocs only builds pages under `docs/`). Edit `CHANGELOG.md`, then run
`python3 tools/sync_changelog.py`.

"""


def expected() -> str:
    body = SOURCE.read_text(encoding="utf-8")
    lines = body.splitlines(keepends=True)
    if not lines or lines[0].strip() != "# Changelog":
        raise SystemExit("CHANGELOG.md must start with '# Changelog'")
    return HEADER + "".join(lines[1:]).lstrip("\n")


def main() -> int:
    want = expected()
    have = TARGET.read_text(encoding="utf-8") if TARGET.is_file() else ""
    if "--check" in sys.argv[1:]:
        if have != want:
            print("docs/changelog.md is out of date: run python3 tools/sync_changelog.py")
            return 1
        print("docs/changelog.md is current")
        return 0
    if have != want:
        TARGET.write_text(want, encoding="utf-8")
        print("docs/changelog.md updated")
    else:
        print("docs/changelog.md is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
