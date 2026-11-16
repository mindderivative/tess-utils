"""Colour: the written forms of TDL and CSS to tre's ``(r, g, b, a)`` of 0 to 255 integers.

The reading follows ``tess_re`` (tre's own colour reading) so the Tesserae projects agree on every
string: the same forms, the same clipping and rounding, and the same error wording. ``tess_re``
itself is not imported.
"""

from __future__ import annotations

import colorsys
import re

from tess_utils.colornames import _CSS_NAMES
from tess_utils.gamut import parse_wide_gamut

Color = tuple[int, int, int, int]

_FUNCTION = re.compile(r"(rgba?|hsla?)\((.*)\)", re.IGNORECASE)
_WIDE_GAMUT = re.compile(r"(color|lab|lch|oklab|oklch|hwb)(?![a-z0-9_-])", re.IGNORECASE)
_NUMBER = re.compile(r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")
_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")


def parse_color(text: object) -> Color:
    """Read a colour written the way TDL and CSS write one; return tre's ``(r, g, b, a)``, each an
    integer 0 to 255.

    - Hex: ``#RGB``, ``#RGBA`` (each digit doubled), ``#RRGGBB``, ``#RRGGBBAA`` (alpha last).
    - A CSS colour name (``red``, ``RebeccaPurple``; the 148 of CSS Color 4, case-insensitive) or
      ``transparent``.
    - ``rgb()``, ``rgba()``, ``hsl()``, ``hsla()`` in CSS Color 4 syntax: spaces or commas, alpha
      as a fourth value or after a slash (``rgb(1 2 3 / 0.5)``), channels as numbers 0 to 255 or
      percentages, alpha as 0.0 to 1.0 or a percentage, hue in degrees with an optional ``deg``.
      A value out of range is clipped, as CSS does.
    - ``color(display-p3 ...)`` and the other ``color()`` spaces, ``lab()``, ``lch()``,
      ``oklab()``, ``oklch()`` and ``hwb()``, clipped into sRGB.
    - Whitespace around the text is ignored.

    Alpha 0.0 to 1.0 becomes 0 to 255 by rounding half up (``tess_re``'s rounding); channels round
    the same way.

    Raises :class:`ValueError` for anything else, also for a value that is not text. The wording is
    ``tess_re``'s: ``wrong number of hex digits``, ``unknown color identifier``, and
    ``invalid color 'text'`` for the rest (the wide-gamut forms add the reason after a colon). The
    parameter is typed ``object`` on purpose: a compiled build (mypyc) would raise ``TypeError`` for
    a wrongly typed argument, and the source and the compiled file must behave alike.
    """
    if not isinstance(text, str):
        raise ValueError(f"a colour is written as text, not {type(text).__name__}")
    written = text.strip()
    if written.lower() == "transparent":
        return (0, 0, 0, 0)
    if _WIDE_GAMUT.match(written):
        try:
            return parse_wide_gamut(written)
        except ValueError as reason:
            raise ValueError(f"invalid color {text!r}: {reason}") from None
    if match := _FUNCTION.fullmatch(written):
        try:
            return _function(match.group(1), match.group(2))
        except ValueError:
            raise ValueError(f"invalid color {text!r}") from None
    if written.startswith("#"):
        digits = written[1:]
        if len(digits) not in (3, 4, 6, 8):
            raise ValueError("wrong number of hex digits")
        if not _HEX_DIGITS.issuperset(digits):
            raise ValueError(f"invalid color {text!r}")
        return _hex(digits)
    if written.isidentifier() or written.replace("-", "").isalpha():
        packed = _CSS_NAMES.get(written.lower())
        if packed is None:
            raise ValueError("unknown color identifier")
        return ((packed >> 16) & 0xFF, (packed >> 8) & 0xFF, packed & 0xFF, 255)
    raise ValueError(f"invalid color {text!r}")


def _hex(digits: str) -> Color:
    if len(digits) in (3, 4):
        digits = "".join(c * 2 for c in digits)
    channels = [int(digits[i : i + 2], 16) for i in range(0, len(digits), 2)]
    if len(channels) == 3:
        channels.append(255)
    r, g, b, a = channels
    return (r, g, b, a)


def _limit(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _quantity(part: str, unit: str = "") -> tuple[float, bool]:
    """A number, or a percentage (the flag), as written; ``unit`` is an optional suffix."""
    word = part.strip()
    percent = word.endswith("%")
    if percent:
        word = word[:-1]
    elif unit and word.lower().endswith(unit):
        word = word[: -len(unit)]
    if not _NUMBER.fullmatch(word):
        raise ValueError(part)
    return (float(word), percent)


def _alpha(part: str) -> int:
    value, percent = _quantity(part)
    return int(_limit(value / 100 if percent else value, 0.0, 1.0) * 255 + 0.5)


def _function(name: str, body: str) -> Color:
    """``rgb()``, ``rgba()``, ``hsl()`` or ``hsla()``: comma or space syntax, alpha last or after
    a slash. Raises a bare :class:`ValueError`; the caller words it."""
    alpha_part: str | None = None
    if "/" in body:
        main, alpha_part = body.split("/", 1)
        parts = main.split()
    else:
        parts = [p.strip() for p in body.split(",")] if "," in body else body.split()
        if len(parts) == 4:
            alpha_part = parts.pop()
    if len(parts) != 3:
        raise ValueError(body)
    alpha = _alpha(alpha_part) if alpha_part is not None else 255
    if name.lower().startswith("rgb"):
        channels = []
        for part in parts:
            value, percent = _quantity(part)
            channels.append(int(_limit(value / 100 * 255 if percent else value, 0, 255) + 0.5))
        return (channels[0], channels[1], channels[2], alpha)
    hue = _quantity(parts[0], "deg")[0] % 360
    saturation = _limit(_quantity(parts[1])[0] / 100, 0, 1)
    lightness = _limit(_quantity(parts[2])[0] / 100, 0, 1)
    red, green, blue = colorsys.hls_to_rgb(hue / 360, lightness, saturation)
    return (int(red * 255 + 0.5), int(green * 255 + 0.5), int(blue * 255 + 0.5), alpha)
