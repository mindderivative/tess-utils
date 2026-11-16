# Reference

Every public name of `tess_utils`, as `tess_utils.__all__` lists them. The text is taken from the
functions' docstrings: change both together. Every failure is a `ValueError`, in the source and in
the compiled file, because the parameters are typed `object` and validated (a compiled build would
otherwise raise `TypeError` for a wrongly typed argument).

## Colour

`parse_color(text) -> (r, g, b, a)`

Reads a colour the way `tess_re` does, so every Tesserae project gives the same bytes for the same
string, and returns tre's `(r, g, b, a)`, each an integer 0 to 255. Whitespace around the text is
ignored.

- Hex: `#RGB`, `#RGBA` (each digit doubled), `#RRGGBB`, `#RRGGBBAA` (alpha last).
- A CSS colour name (the 148 of CSS Color 4, any case: `red`, `RebeccaPurple`) or `transparent`.
- `rgb()`, `rgba()`, `hsl()`, `hsla()` in CSS Color 4 syntax: spaces or commas, alpha as a fourth
  value or after a slash (`rgb(1 2 3 / 0.5)`), channels as numbers 0 to 255 or percentages, alpha
  0.0 to 1.0 or a percentage, hue in degrees with an optional `deg`. A value out of range is
  clipped, as CSS does.
- `color(display-p3 ...)` and the other `color()` spaces (`srgb`, `srgb-linear`, `display-p3`,
  `a98-rgb`, `prophoto-rgb`, `rec2020`, `xyz`, `xyz-d50`, `xyz-d65`), `lab()`, `lch()`, `oklab()`,
  `oklch()` and `hwb()`, clipped into sRGB. They are computed in `f32` step for step as `tess_re`'s
  colour crate does, so the bytes match.

An alpha of 0.0 to 1.0 becomes 0 to 255 by rounding half up, as `tess_re` does (`0.3` is 77, not
76).

A colour it cannot read is a `ValueError` worded as `tess_re` words it: `wrong number of hex
digits`, `unknown color identifier`, and `invalid color '<text>'` for the rest (the wide-gamut
forms add the reason after a colon, such as `unknown color space`). A value that is not text is a
`ValueError` too.

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
  Pillow's global limit is not touched. `max_side=None` sets no limit of ours (Pillow's own checks
  stay): the consumer decides what is too large.
- Another format (BMP, TIFF, SVG, text), empty, corrupt or truncated data, a zero-sized image and
  a wrong argument type are all `ValueError`; no Pillow exception escapes.

`decode_image_file(path, max_side=None) -> (width, height, rgba)`

The same for a file, given as text or a path object: the result is that of `decode_image` of the
file's bytes. There is no size limit unless the caller passes `max_side` (Pillow's own
decompression-bomb error still applies above about 179 million pixels). A file that cannot be read
or decoded (missing, unreadable, corrupt, truncated, another format, over `max_side`) is an
`OSError` whose message names the path: `cannot decode image '<path>': <reason>`. A `path` that is
neither text nor a path object, or a bad `max_side`, is a `ValueError`.

Pillow is imported inside the functions, so `import tess_utils` never loads it. It is not in the
compiled file: the caller installs it (`Pillow>=11`, the extra `image` of the source package).
