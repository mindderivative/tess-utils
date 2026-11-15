# Changelog

The changelog is `CHANGELOG.md` in the repository root; this page is a copy kept for the site
(MkDocs only builds pages under `docs/`). Edit `CHANGELOG.md` and copy it here.


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
