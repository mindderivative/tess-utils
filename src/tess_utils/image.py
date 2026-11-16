"""Image files and bytes to the pixels tre's ``image`` node takes (RGBA8).

Pillow is imported inside :func:`decode_image` and :func:`decode_image_file`, never at module import
time, so a consumer that only needs colours never loads it. Pillow is not part of the compiled
release either: it is a normal runtime dependency of whoever calls the functions (the ``image``
extra).
"""

from __future__ import annotations

import io
import os
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
      ``ValueError`` before any pixel is decoded, and Pillow's decompression-bomb warning is turned
      into an error for the duration of the call only (``warnings.catch_warnings``); Pillow's
      global ``MAX_IMAGE_PIXELS`` is not touched. ``max_side=None`` sets no limit of ours (Pillow's
      own checks stay): the consumer decides what is too large.
    - Every failure is a ``ValueError``: wrong argument types, empty or corrupt or truncated data,
      another format (BMP, TIFF, SVG, text), a zero-sized image, a size over the limit. No Pillow
      exception type escapes. The parameters are typed ``object`` so a compiled build behaves
      like the source.
    """
    if not isinstance(data, bytes | bytearray | memoryview):
        raise ValueError(f"image data is bytes, not {type(data).__name__}")
    limit = _checked_max_side(max_side)
    raw = bytes(data)
    if not raw:
        raise ValueError("image data is empty")
    return _decode(io.BytesIO(raw), limit)


def decode_image_file(path: object, max_side: object = None) -> tuple[int, int, bytes]:
    """Decode the PNG, JPEG, GIF or WebP file at ``path`` (text or a path object) to
    ``(width, height, rgba)``, the same result as :func:`decode_image` of the file's bytes.

    Unlike :func:`decode_image` there is no size limit unless the caller gives ``max_side``: the
    consumer decides what is too large (Pillow's own decompression-bomb error still applies above
    about 179 million pixels).

    A file that cannot be read or decoded (missing, unreadable, corrupt, truncated, another format,
    over ``max_side``) is an :class:`OSError` whose message names the path:
    ``cannot decode image '<path>': <reason>``. A ``path`` that is neither text nor a path object,
    or a bad ``max_side``, is a ``ValueError``, as everywhere else in this package.
    """
    if not isinstance(path, str | os.PathLike):
        raise ValueError(f"an image path is text or a path, not {type(path).__name__}")
    name = os.fspath(path)
    if not isinstance(name, str):
        raise ValueError("an image path is text or a path, not bytes")
    limit = _checked_max_side(max_side)
    try:
        return _decode(name, limit)
    except ValueError as error:
        raise OSError(f"cannot decode image {name!r}: {error}") from None


def _checked_max_side(max_side: object) -> int | None:
    if max_side is None:
        return None
    if isinstance(max_side, bool) or not isinstance(max_side, int):
        raise ValueError(f"max_side is a whole number of pixels, not {max_side!r}")
    if max_side < 1:
        raise ValueError(f"max_side is at least 1, not {max_side}")
    return max_side


def _decode(source: io.BytesIO | str, max_side: int | None) -> tuple[int, int, bytes]:
    """Decode a file name or an open byte stream; every failure is a ``ValueError``."""
    from PIL import Image, ImageOps, UnidentifiedImageError  # lazy: see the module docstring

    try:
        with warnings.catch_warnings():
            if max_side is not None:
                warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(source) as img:
                if img.format not in _FORMATS:
                    raise ValueError("not a png, jpeg, gif or webp image")
                width, height = img.size
                if width < 1 or height < 1:
                    raise ValueError(f"the image has no pixels ({width}x{height})")
                if max_side is not None and (width > max_side or height > max_side):
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
    except UnidentifiedImageError:
        raise ValueError("not a png, jpeg, gif or webp image") from None
    except Exception as error:  # OSError, SyntaxError, EOFError, struct.error, warnings as errors
        raise ValueError(f"cannot read the image: {type(error).__name__}: {error}") from None
    return (out_w, out_h, pixels)
