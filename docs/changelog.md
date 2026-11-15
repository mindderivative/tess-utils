# Changelog

The changelog is `CHANGELOG.md` in the repository root; this page is a copy kept for the site
(MkDocs only builds pages under `docs/`). Edit `CHANGELOG.md`, then run
`python3 tools/sync_changelog.py`.

## 0.2.2

Additive: every colour and image call that worked in 0.2.1 still works, with the two exceptions named
under "Changed results".

- `parse_color` now reads what `tess_re` reads (the reading written in tess-ui, so the Tesserae
  projects give the same bytes for the same string): the 148 CSS colour names, case-insensitive
  (`red`, `RebeccaPurple`); `hsl()` and `hsla()`; `rgb()` with percentages, fractions and an alpha
  after a slash (`rgb(1 2 3 / 0.5)`); hue with `deg`; and the wide-gamut functions `color()`
  (`srgb`, `srgb-linear`, `display-p3`, `a98-rgb`, `prophoto-rgb`, `rec2020`, `xyz`, `xyz-d50`,
  `xyz-d65`), `lab()`, `lch()`, `oklab()`, `oklch()` and `hwb()`, clipped into sRGB. On the 346
  colour strings of tess-ui's tests, views and docs the source and the compiled file give the same
  result and the same error text as tess-ui's own `parse_color`.
- New modules `colornames` (the name table) and `gamut` (the wide-gamut functions, `f32`
  arithmetic as the Rust crate's; from tess-ui's `_wide_gamut.py`). `tools/build_so.py` now lets a
  module import an earlier one in `MODULES` (the import is dropped in the merged file) and stops
  the build if two modules define the same top-level name.
- New `decode_image_file(path, max_side=None)`: the same result as `decode_image` of the file's
  bytes. No size limit unless asked; a file that cannot be read or decoded is an `OSError` that
  names the path (`cannot decode image '<path>': <reason>`). `decode_image` also takes
  `max_side=None` (no limit of ours); its default stays 4096. The size limit is the consumer's
  call, not this package's.

Changed results (the same strings, a different outcome):

- Error wording is `tess_re`'s: `wrong number of hex digits`, `unknown color identifier`,
  `invalid color '<text>'`, with the reason after a colon for the wide-gamut forms. Before, the
  messages began `not a colour:` and named the bad part. A consumer that shows or matches the text
  sees the new wording; the exception type is still `ValueError`.
- A channel or alpha out of range, and a fraction, no longer raise: they are clipped and rounded
  (`rgb(300 0 0)` is `(255, 0, 0, 255)`, `rgba(0 0 0 1.5)` has alpha 255, `rgb(1.5 2.5 3.5)` is
  `(2, 3, 4, 255)`), as CSS and `tess_re` do. Alpha rounds half up, so `rgba(0 0 0 0.3)` is alpha 77
  and `0.7` is 179; 0.2.1 rounded to the even neighbour and gave 76 and 178.

## 0.2.1

- The package is published to PyPI as `tesserae-utils` (the import name stays `tess_utils`; the repository stays `tess-utils`). The classifier `Private :: Do Not Upload` is gone; the project metadata is otherwise unchanged.
- `.github/workflows/release.yml` publishes a `vX.Y.Z` tag to PyPI with Trusted Publishing and attaches the compiled single file (`tess_utils.<soabi>.so`, `tess_utils.pyi`, `tess_utils.stamp.json`) to the GitHub release; CI (`ci.yml`) runs the tests, lint and types, the wheel smoke test, the compiled build against the suite, and the docs build; the docs deploy to GitHub Pages.
- `tools/sync_changelog.py` keeps the docs site's changelog page a copy of this file.
- No change to any converter: results are the same as 0.2.0.

## 0.2.0

- New `tess_utils.image` with `decode_image(data, max_side=4096)`: the bytes of a PNG, JPEG, GIF or WebP image to `(width, height, rgba)`, straight-alpha RGBA8 with rows from top to bottom (what tre's `image` node takes). First frame of an animated GIF or WebP; EXIF orientation applied; palette, greyscale, CMYK and 16-bit images converted to RGBA (palette transparency kept). The header size is checked against `max_side` before any pixel is decoded; Pillow's decompression-bomb warning is an error for the call only (no global state changed).
- Every failure is a `ValueError` (wrong argument types, empty/corrupt/truncated data, another format, zero size, over the limit); no Pillow exception escapes, in the source and in the `.so`.
- Pillow is imported inside the function, never at import time, and stays outside the compiled `.so`: it is the optional extra `image` (`Pillow>=11`) and a dev dependency. `tests/test_no_imports.py` now allows Pillow only inside `image.py`'s function.
- `tools/build_so.py` merges `image` too and lists `decode_image` among the public names.

## 0.1.1

- The release now carries a type stub, `tess_utils.pyi`, beside the `.so` (made by `mypy.stubgen` from the merged module) so a consumer's mypy can read the compiled file. The stamp lists the SHA-256 of both files.
- `vendor.json`: the manifest a consumer's sync script reads (package, repository, stamp and the files to copy; `{soabi}` is the consumer's Python tag). The sync script itself lives in each consumer.
- No change to the converters.

## 0.1.0 (unreleased)

The first slice (tess-utils Brief). Pure functions; the 0.1 modules import only the standard library.

- `parse_color(text)`: `#RRGGBB`, `#RRGGBBAA` (alpha last), `#RGB`, `#RGBA`, `rgb(...)` and `rgba(...)`
  with spaces or commas (red to blue 0 to 255, alpha 0.0 to 1.0) and `transparent`, to tre's
  `(r, g, b, a)` of 0 to 255 integers. `ValueError` names the bad part. The brief's list had no
  `#RGB`, `#RGBA` or commas; the shell already reads them, so they are in from the start.
- `expand_sides(value)`: one number, four numbers or named sides (any case, unnamed sides 0) to
  `(left, top, right, bottom)`; a list of 2 or 3 is an error (ADR-0014 D72). A negative number is
  allowed: whether a side may be negative is the caller's rule.
- `to_tre_order(sides)`: `(left, top, right, bottom)` to tre's `(top, right, bottom, left)`.
- `expand_radius(value)`: one number or four from the top-left corner clockwise; never negative.
- `to_tre_word(name)`: `SPACE_BETWEEN` to `space_between`.
