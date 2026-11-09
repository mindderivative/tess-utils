# Changelog

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
