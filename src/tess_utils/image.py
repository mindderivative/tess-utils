"""Image file bytes to the pixels tre's ``image`` node takes (RGBA8).

Pillow is imported inside :func:`decode_image`, never at module import time, so a consumer that
only needs colours never loads it. Pillow is not part of the compiled release either: it is a
normal runtime dependency of whoever calls the function (the ``image`` extra).
"""

from __future__ import annotations

import io
import warnings

_FORMATS = {"PNG", "JPEG", "GIF", "WEBP"}


def decode_image(data: object, max_side: object = 4096) -> tuple[int, int, bytes]:
    """Decode the bytes of a PNG, JPEG, GIF or WebP image to ``(width, height, rgba)``.

    ``rgba`` is straight-alpha RGBA8, ``len(rgba) == width * height * 4``, rows from top to bottom:
    what tre's ``image`` node takes as ``rgba``, ``pixel_width`` and ``pixel_height``.

    - An animated GIF or WebP gives its first frame only.
    - EXIF orientation is applied (``ImageOps.exif_transpose``), so a rotated JPEG is upright.
    - Palette, greyscale, CMYK and 16-bit images are converted to RGBA; a palette transparency is
      kept as alpha.
    - The header size is read first: a width or height over ``max_side`` (default 4096) is a
      ``ValueError`` before any pixel is decoded. Pillow's decompression-bomb warning is turned
      into an error for the duration of the call only (``warnings.catch_warnings``); Pillow's
      global ``MAX_IMAGE_PIXELS`` is not touched.
    - Every failure is a ``ValueError``: wrong argument types, empty or corrupt or truncated data,
      another format (BMP, TIFF, SVG, text), a zero-sized image, a size over the limit. No Pillow
      exception type escapes. The parameters are typed ``object`` so a compiled build behaves
      like the source.
    """
    if not isinstance(data, bytes | bytearray | memoryview):
        raise ValueError(f"image data is bytes, not {type(data).__name__}")
    if isinstance(max_side, bool) or not isinstance(max_side, int):
        raise ValueError(f"max_side is a whole number of pixels, not {max_side!r}")
    if max_side < 1:
        raise ValueError(f"max_side is at least 1, not {max_side}")
    raw = bytes(data)
    if not raw:
        raise ValueError("image data is empty")

    from PIL import Image, ImageOps  # lazy: see the module docstring

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as img:
                if img.format not in _FORMATS:
                    raise ValueError("not a png, jpeg, gif or webp image")
                width, height = img.size
                if width < 1 or height < 1:
                    raise ValueError(f"the image has no pixels ({width}x{height})")
                if width > max_side or height > max_side:
                    raise ValueError(
                        f"the image is {width}x{height} pixels, over the limit of {max_side}"
                    )
                img.load()
                upright = ImageOps.exif_transpose(img)
                if upright.mode in ("I;16", "I;16L", "I;16B", "I;16N", "I"):
                    upright = upright.point(lambda v: v / 256).convert("L")
                rgba = upright.convert("RGBA")
                out_w, out_h = rgba.size
                pixels = rgba.tobytes()
    except ValueError as error:
        # Pillow's own errors (UnidentifiedImageError, DecompressionBombError) are ValueError
        # subclasses; ours carry a clear message already.
        if type(error) is ValueError:
            raise
        raise ValueError(f"cannot read the image: {error}") from None
    except Exception as error:  # OSError, SyntaxError, EOFError, struct.error, warnings as errors
        raise ValueError(f"cannot read the image: {type(error).__name__}: {error}") from None
    return (out_w, out_h, pixels)
