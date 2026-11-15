# tess-utils

Shared converters for the Tesserae projects (`tess-shell`, Tesserae UI). It is on PyPI as
`tesserae-utils` (the repository is `tess-utils`), and its converters have no dependencies (only
`decode_image` needs Pillow, see below): tre stays a rendering engine with one entry form, and
the forms a TDL file writes (colours, four-sided values, corner radii, enum words) are turned into
that form here, once.

Import name `tess_utils`. Python 3.14 or later. MIT.

```python
from tess_utils import expand_radius, expand_sides, parse_color, to_tre_order, to_tre_word

parse_color("#89b4fa80")                 # (137, 180, 250, 128)
parse_color("RebeccaPurple")             # (102, 51, 153, 255)
parse_color("oklch(0.7 0.1 200 / 50%)")  # (64, 177, 183, 128)
to_tre_order(expand_sides({"Left": 24})) # (0.0, 0.0, 0.0, 24.0)
expand_radius([0, 0, 8, 8])              # (0.0, 0.0, 8.0, 8.0)
to_tre_word("SPACE_BETWEEN")             # "space_between"
```

`parse_color` reads the colour the way `tess_re` does, so the Tesserae projects agree on every
string: hex (`#RGB`, `#RGBA`, `#RRGGBB`, `#RRGGBBAA`), the 148 CSS colour names and `transparent`,
`rgb()`/`rgba()`/`hsl()`/`hsla()` in CSS Color 4 syntax (comma or space, alpha after a slash,
percentages, out-of-range values clipped), and the wide-gamut functions `color()`, `lab()`, `lch()`,
`oklab()`, `oklch()` and `hwb()`, clipped into sRGB. Errors use `tess_re`'s wording.

`decode_image(data, max_side=4096)` turns the bytes of a PNG, JPEG, GIF or WebP file into
`(width, height, rgba)` (straight-alpha RGBA8, top row first: tre's `image` node), and
`decode_image_file(path)` does the same for a file. Pillow is imported inside the functions, so
`import tess_utils` never loads it, and it is not in the compiled file: the caller installs it
(`pip install tesserae-utils[image]`, `Pillow>=11`). `decode_image` refuses a side over `max_side`
from the header, before any pixel is decoded; `max_side=None` sets no limit, and
`decode_image_file` has none unless given one: the consumer decides what is too large. Every
`decode_image` failure is a `ValueError`; `decode_image_file` raises an `OSError` naming the path
for a file it cannot read or decode.

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

Versions are git tags (`v0.1.0`) and `CHANGELOG.md`. A release is published to PyPI as
`tesserae-utils` by `.github/workflows/release.yml` (Trusted Publishing, on a `vX.Y.Z` tag, with an
approval in the `pypi` environment). Separately, the Tesserae consumers carry a compiled copy
(maintainer, 2026-11-08): one `.so` (`mypyc`), a file on a GitHub release, which each consumer
downloads, checks against its SHA-256 and carries in `_vendor/` with a stamp. See `tools/build_so.py`.

The sync script that copies a release into a consumer (`vendor.json` manifest plus a short script in
each consumer, the vault's recommendation C) is not written yet: it is open question 3 of the
tess-utils Brief, and the first consumer, `tess-shell`, writes it when it takes the file. The build
tool's stamp (`build/so/tess_utils.stamp.json`: version, Python tag, platform, SHA-256) is what that
script checks.

A compiled file raises `TypeError` for a wrongly typed argument, which the source would not, so the
public functions take `object` and validate: the source and the `.so` raise the same `ValueError`
(the tests run against both: `uv run python tools/build_so.py --test`).

