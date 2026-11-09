# tess-utils

Shared converters for the Tesserae projects (`tess-shell`, Tesserae UI). It is private, it is not
released on PyPI, and it has no dependencies: tre stays a rendering engine with one entry form, and
the forms a TDL file writes (colours, four-sided values, corner radii, enum words) are turned into
that form here, once.

Import name `tess_utils`. Python 3.14 or later. MIT.

```python
from tess_utils import expand_radius, expand_sides, parse_color, to_tre_order, to_tre_word

parse_color("#89b4fa80")                 # (137, 180, 250, 128)
to_tre_order(expand_sides({"Left": 24})) # (0.0, 0.0, 0.0, 24.0)
expand_radius([0, 0, 8, 8])              # (0.0, 0.0, 8.0, 8.0)
to_tre_word("SPACE_BETWEEN")             # "space_between"
```

## What belongs here

A function is added when at least two projects use it, it is a few lines of our own code (a mapped
library only for work that would be a project of its own, ADR-0019), it imports no Tesserae package,
it has no dependency and no UI or schema meaning, and it has tests. Schema, typing and UI meaning
stay in the projects.

## Development

```
UV_PROJECT_ENVIRONMENT=~/Projects/pyDev/pyEnvs/tess-utils uv sync
uv run ruff check src tests && uv run mypy && uv run pytest -q
```

Versions are git tags (`v0.1.0`) and `CHANGELOG.md`. Distribution (maintainer, 2026-11-08): a release
is one compiled `.so` (`mypyc`), a file on a GitHub release of the private repository, which each
consumer downloads, checks against its SHA-256 and carries in `_vendor/` with a stamp. See
`tools/build_so.py`.

The sync script that copies a release into a consumer (`vendor.json` manifest plus a short script in
each consumer, the vault's recommendation C) is not written yet: it is open question 3 of the
tess-utils Brief, and the first consumer, `tess-shell`, writes it when it takes the file. The build
tool's stamp (`build/so/tess_utils.stamp.json`: version, Python tag, platform, SHA-256) is what that
script checks.

A compiled file raises `TypeError` for a wrongly typed argument, which the source would not, so the
public functions take `object` and validate: the source and the `.so` raise the same `ValueError`
(the tests run against both: `uv run python tools/build_so.py --test`).

