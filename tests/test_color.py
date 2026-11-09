import pytest

from tess_utils import parse_color


@pytest.mark.parametrize(
    ("written", "expected"),
    [
        ("#ffffff", (255, 255, 255, 255)),
        ("#000000", (0, 0, 0, 255)),
        ("#89b4fa", (0x89, 0xB4, 0xFA, 255)),
        ("#89B4FA", (0x89, 0xB4, 0xFA, 255)),
        ("#ffffff10", (255, 255, 255, 0x10)),  # alpha is last
        ("#00000066", (0, 0, 0, 0x66)),
        ("#fff", (255, 255, 255, 255)),
        ("#f008", (255, 0, 0, 0x88)),
        ("rgba(0 0 0 0.5)", (0, 0, 0, 128)),
        ("rgba(255 128 0 1.0)", (255, 128, 0, 255)),
        ("rgba(255 128 0 0)", (255, 128, 0, 0)),
        ("rgba(10, 20, 30, 0.25)", (10, 20, 30, 64)),
        ("rgba(  1   2   3   1  )", (1, 2, 3, 255)),
        ("rgb(1 2 3)", (1, 2, 3, 255)),
        ("RGBA(1 2 3 1)", (1, 2, 3, 255)),
        ("transparent", (0, 0, 0, 0)),
        ("  Transparent ", (0, 0, 0, 0)),
        ("  #ffffff  ", (255, 255, 255, 255)),
    ],
)
def test_the_written_forms_become_trees_integers(written: str, expected: tuple[int, ...]) -> None:
    assert parse_color(written) == expected


@pytest.mark.parametrize(
    ("written", "part"),
    [
        ("", "not a colour"),
        ("red", "not a colour"),
        ("#gg0000", "'g' is not a hex digit"),
        ("#12345", "3, 4, 6 or 8 digits, not 5"),
        ("#1234567", "not 7"),
        ("#", "not 0"),
        ("ffffff", "not a colour"),
        ("rgba(1 2)", "3 or 4 numbers, not 2"),
        ("rgba(1 2 3 4 5)", "not 5"),
        ("rgba(256 0 0 1)", "red is 256"),
        ("rgba(0 -1 0 1)", "green is -1"),
        ("rgba(0 0 999 1)", "blue is 999"),
        ("rgba(0 0 0 1.5)", "alpha is 1.5"),
        ("rgba(0 0 0 -0.1)", "alpha is -0.1"),
        ("rgba(0 0 0 nan)", "alpha is nan"),
        ("rgba(1.5 0 0 1)", "whole numbers"),
        ("rgba(a b c 1)", "whole numbers"),
        ("rgba(0 0 0 half)", "alpha is a number"),
        ("rgba(0 0 0 1", "not a colour"),
    ],
)
def test_a_bad_colour_raises_and_names_the_bad_part(written: str, part: str) -> None:
    with pytest.raises(ValueError, match="not a colour") as exc:
        parse_color(written)
    assert part in str(exc.value)
    assert repr(written) in str(exc.value)


def test_a_non_string_is_refused() -> None:
    with pytest.raises(ValueError, match="written as text"):
        parse_color(0xFFFFFF)
