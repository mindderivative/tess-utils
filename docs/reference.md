# Reference

Every public name of `tess_utils`, as `tess_utils.__all__` lists them. The text is taken from the
functions' docstrings: change both together. Every failure is a `ValueError`, in the source and in
the compiled file, because the parameters are typed `object` and validated (a compiled build would
otherwise raise `TypeError` for a wrongly typed argument).

## Colour

`parse_color(text) -> (r, g, b, a)`

Reads `#RRGGBB`, `#RRGGBBAA` (alpha last), `#RGB`, `#RGBA`, `rgb(r g b)`, `rgba(r g b a)` (spaces
or commas; red to blue 0 to 255, alpha 0.0 to 1.0) and `transparent`. Returns tre's `(r, g, b, a)`,
each an integer 0 to 255. The `ValueError` names the bad part, also for a value that is not text.

## Four-sided values

`expand_sides(value) -> (left, top, right, bottom)`

One number (every side), four numbers, or named sides. A mapping names `left`, `top`, `right` and
`bottom` in any case; a side it does not name is 0. A list of two or three numbers is an error
(ADR-0014 D72), as is an unknown side name. A negative number is allowed: whether a side may be
negative is the caller's rule.

`to_tre_order(sides) -> (top, right, bottom, left)`

Turns `(left, top, right, bottom)` into the order tre's margins use.

## Corner radii

`expand_radius(value) -> (top_left, top_right, bottom_right, bottom_left)`

One number (every corner) or four numbers from the top-left corner clockwise. A radius is never
negative; a list of other than four numbers is an error.

## Enum words

`to_tre_word(name) -> str`

`SPACE_BETWEEN` becomes `space_between`, `HORIZONTAL` becomes `horizontal`. A name is letters,
digits and single underscores, starting with a letter; anything else is an error.

## Images

`decode_image(data, max_side=4096) -> (width, height, rgba)`

Decodes the bytes of a PNG, JPEG, GIF or WebP image. `rgba` is straight-alpha RGBA8 with
`len(rgba) == width * height * 4` and rows from top to bottom: what tre's `image` node takes as
`rgba`, `pixel_width` and `pixel_height`.

- An animated GIF or WebP gives its first frame only.
- EXIF orientation is applied, so a rotated JPEG is upright.
- Palette, greyscale, CMYK and 16-bit images are converted to RGBA; a palette transparency is kept
  as alpha.
- The header size is read first: a width or height over `max_side` is an error before any pixel is
  decoded. Pillow's decompression-bomb warning is turned into an error for the call only, and
  Pillow's global limit is not touched.
- Another format (BMP, TIFF, SVG, text), empty, corrupt or truncated data, a zero-sized image and
  a wrong argument type are all `ValueError`; no Pillow exception escapes.

Pillow is imported inside the function, so `import tess_utils` never loads it. It is not in the
compiled file: the caller installs it (`Pillow>=11`, the extra `image` of the source package).
