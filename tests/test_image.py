import io
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from tess_utils import decode_image, decode_image_file


def _save(img: Image.Image, fmt: str, **kw: object) -> bytes:
    buf = io.BytesIO()
    img.save(buf, fmt, **kw)
    return buf.getvalue()


def _split(size: tuple[int, int], mode: str = "RGB") -> Image.Image:
    img = Image.new(mode, size)
    w, h = size
    for x in range(w):
        for y in range(h):
            img.putpixel(
                (x, y),
                (255, 0, 0, 255)[: len(mode)] if x < w // 2 else (0, 0, 255, 255)[: len(mode)],
            )
    return img


def _px(rgba: bytes, width: int, x: int, y: int) -> tuple[int, ...]:
    i = (y * width + x) * 4
    return tuple(rgba[i : i + 4])


def test_png_is_exact() -> None:
    w, h, rgba = decode_image(_save(_split((8, 6)), "PNG"))
    assert (w, h, len(rgba)) == (8, 6, 8 * 6 * 4)
    assert _px(rgba, w, 0, 0) == (255, 0, 0, 255)
    assert _px(rgba, w, 7, 5) == (0, 0, 255, 255)
    assert isinstance(rgba, bytes)


def test_png_alpha_is_kept_straight() -> None:
    img = Image.new("RGBA", (8, 6), (0, 255, 0, 255))
    img.putpixel((0, 0), (0, 0, 0, 0))
    img.putpixel((1, 0), (10, 20, 30, 128))
    w, _h, rgba = decode_image(_save(img, "PNG"))
    assert _px(rgba, w, 0, 0)[3] == 0
    assert _px(rgba, w, 1, 0) == (10, 20, 30, 128)
    assert _px(rgba, w, 2, 0) == (0, 255, 0, 255)


def test_jpeg_within_tolerance() -> None:
    w, h, rgba = decode_image(_save(_split((16, 16)), "JPEG", quality=95))
    assert (w, h) == (16, 16)
    left, right = _px(rgba, w, 1, 8), _px(rgba, w, 14, 8)
    assert left[0] > 230 and left[1] < 25 and left[2] < 25 and left[3] == 255
    assert right[2] > 230 and right[0] < 25 and right[3] == 255


def test_lossless_webp_is_exact() -> None:
    w, h, rgba = decode_image(_save(_split((8, 6)), "WEBP", lossless=True))
    assert (w, h) == (8, 6)
    assert _px(rgba, w, 0, 0) == (255, 0, 0, 255)
    assert _px(rgba, w, 7, 0) == (0, 0, 255, 255)


def test_lossy_webp_within_tolerance() -> None:
    w, _h, rgba = decode_image(_save(_split((16, 16)), "WEBP", quality=95))
    assert _px(rgba, w, 1, 8)[0] > 220


def test_palette_gif_keeps_transparency() -> None:
    img = Image.new("P", (4, 4), 0)
    img.putpalette([255, 0, 0, 0, 0, 255] + [0] * 250)
    img.putpixel((3, 3), 1)
    w, _h, rgba = decode_image(_save(img, "GIF", transparency=0))
    assert _px(rgba, w, 0, 0)[3] == 0
    assert _px(rgba, w, 3, 3) == (0, 0, 255, 255)


def test_animated_gif_gives_first_frame() -> None:
    first = _split((8, 6)).convert("P")
    second = Image.new("RGB", (8, 6), (0, 255, 0)).convert("P")
    data = _save(first, "GIF", save_all=True, append_images=[second], duration=50, loop=0)
    assert Image.open(io.BytesIO(data)).n_frames == 2
    w, _h, rgba = decode_image(data)
    assert _px(rgba, w, 0, 0) == (255, 0, 0, 255)
    assert _px(rgba, w, 7, 0) == (0, 0, 255, 255)


def test_one_pixel() -> None:
    assert decode_image(_save(Image.new("RGB", (1, 1), (1, 2, 3)), "PNG")) == (
        1,
        1,
        bytes([1, 2, 3, 255]),
    )


def test_exif_orientation_six_is_applied() -> None:
    img = Image.new("RGB", (8, 4), (255, 0, 0))
    for x in range(4, 8):
        for y in range(4):
            img.putpixel((x, y), (0, 0, 255))
    exif = Image.Exif()
    exif[0x0112] = 6  # rotate 90 clockwise to display
    w, h, rgba = decode_image(_save(img, "JPEG", quality=100, exif=exif))
    assert (w, h) == (4, 8)
    # clockwise rotation: the left (red) half ends on top, the right (blue) half at the bottom
    assert _px(rgba, w, 2, 1)[0] > 200
    assert _px(rgba, w, 2, 6)[2] > 200


def test_greyscale_and_16_bit_and_cmyk() -> None:
    w, _h, rgba = decode_image(_save(Image.new("L", (2, 2), 100), "PNG"))
    assert _px(rgba, w, 0, 0) == (100, 100, 100, 255)
    w, _h, rgba = decode_image(_save(Image.new("I;16", (2, 2), 256 * 100), "PNG"))
    assert _px(rgba, w, 0, 0) == (100, 100, 100, 255)
    w, h, rgba = decode_image(_save(Image.new("CMYK", (2, 2), (0, 0, 0, 0)), "JPEG"))
    assert (w, h, len(rgba)) == (2, 2, 16)


def test_bytearray_and_memoryview_are_accepted() -> None:
    data = _save(Image.new("RGB", (2, 2), (9, 9, 9)), "PNG")
    assert decode_image(bytearray(data)) == decode_image(memoryview(data)) == decode_image(data)


@pytest.mark.parametrize(
    "make",
    [
        lambda: _save(Image.new("RGB", (4, 4)), "BMP"),
        lambda: _save(Image.new("RGB", (4, 4)), "TIFF"),
        lambda: b"<svg xmlns='http://www.w3.org/2000/svg'/>",
        lambda: b"just some text",
        lambda: b"",
        lambda: _save(_split((8, 6)), "PNG")[:20],
        lambda: _save(_split((64, 64)), "PNG")[:-30],
        lambda: _save(_split((32, 32)), "JPEG")[:-200],
    ],
)
def test_bad_files_are_value_errors(make: object) -> None:
    with pytest.raises(ValueError):
        decode_image(make())  # type: ignore[operator]


def test_other_formats_say_what_is_accepted() -> None:
    with pytest.raises(ValueError, match="not a png, jpeg, gif or webp image"):
        decode_image(_save(Image.new("RGB", (4, 4)), "BMP"))


def test_unidentifiable_bytes_say_what_is_accepted() -> None:
    with pytest.raises(ValueError, match="not a png, jpeg, gif or webp image"):
        decode_image(b"just some text")


def test_over_max_side_fails_before_decoding() -> None:
    # 4097x1 greyscale compresses to a tiny file; the header is enough to refuse it
    data = _save(Image.new("L", (4097, 1)), "PNG")
    with pytest.raises(ValueError, match=r"4097x1.*limit of 4096"):
        decode_image(data)
    assert decode_image(data, 4097)[:2] == (4097, 1)
    with pytest.raises(ValueError, match="limit of 4"):
        decode_image(_save(Image.new("L", (3, 5)), "PNG"), 4)


def test_huge_dimensions_in_a_tiny_png_are_refused_without_decoding() -> None:
    data = bytearray(_save(Image.new("L", (1, 1)), "PNG"))
    # patch the IHDR width/height to 60000x60000 (CRC is not checked by the header read)
    data[16:24] = (60000).to_bytes(4, "big") * 2
    with pytest.raises(ValueError):
        decode_image(bytes(data))


@pytest.mark.parametrize("data", ["text", None, 5, 1.5, [1, 2], object()])
def test_wrong_data_type(data: object) -> None:
    with pytest.raises(ValueError, match="bytes"):
        decode_image(data)


@pytest.mark.parametrize("max_side", [True, 4096.0, "4096", 0, -1])
def test_wrong_max_side(max_side: object) -> None:
    with pytest.raises(ValueError, match="max_side"):
        decode_image(b"x", max_side)


def test_importing_the_package_does_not_import_pillow() -> None:
    code = "import sys, tess_utils; sys.exit(1 if 'PIL' in sys.modules else 0)"
    assert subprocess.run([sys.executable, "-c", code], check=False).returncode == 0


def test_no_max_side_sets_no_limit_of_ours() -> None:
    data = _save(Image.new("L", (4097, 1)), "PNG")
    assert decode_image(data, None)[:2] == (4097, 1)


def test_a_file_decodes_like_its_bytes(tmp_path: Path) -> None:
    data = _save(_split((8, 6)), "PNG")
    target = tmp_path / "split.png"
    target.write_bytes(data)
    assert decode_image_file(target) == decode_image(data)
    assert decode_image_file(str(target)) == decode_image(data)


def test_a_file_has_no_size_limit_unless_asked(tmp_path: Path) -> None:
    target = tmp_path / "wide.png"
    target.write_bytes(_save(Image.new("L", (4097, 1)), "PNG"))
    assert decode_image_file(target)[:2] == (4097, 1)
    with pytest.raises(OSError, match=r"wide\.png.*4097x1.*limit of 4096"):
        decode_image_file(target, 4096)


@pytest.mark.parametrize("content", [None, b"x", b"", b"\x89PNG\r\n\x1a\n"])
def test_an_unreadable_file_is_an_oserror_naming_the_path(
    tmp_path: Path, content: bytes | None
) -> None:
    target = tmp_path / "broken.png"
    if content is not None:
        target.write_bytes(content)
    with pytest.raises(OSError, match="cannot decode image .*broken.png"):
        decode_image_file(target)


def test_a_file_in_another_format_is_refused(tmp_path: Path) -> None:
    target = tmp_path / "x.bmp"
    target.write_bytes(_save(Image.new("RGB", (4, 4)), "BMP"))
    with pytest.raises(OSError, match="not a png, jpeg, gif or webp image"):
        decode_image_file(target)


@pytest.mark.parametrize("path", [None, 5, b"x.png", ["x.png"], object()])
def test_a_wrong_path_type_is_a_value_error(path: object) -> None:
    with pytest.raises(ValueError, match="path"):
        decode_image_file(path)


@pytest.mark.parametrize("max_side", [True, 4096.0, "4096", 0, -1])
def test_a_wrong_max_side_for_a_file_is_a_value_error(max_side: object) -> None:
    with pytest.raises(ValueError, match="max_side"):
        decode_image_file("x.png", max_side)
