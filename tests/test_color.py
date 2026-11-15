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
        ("#ABCD", (0xAA, 0xBB, 0xCC, 0xDD)),
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
def test_the_forms_of_0_2_1_still_read_the_same(written: str, expected: tuple[int, ...]) -> None:
    assert parse_color(written) == expected


@pytest.mark.parametrize(
    ("written", "expected"),
    [
        ("red", (255, 0, 0, 255)),
        ("Red", (255, 0, 0, 255)),
        ("  RED ", (255, 0, 0, 255)),
        ("rebeccapurple", (102, 51, 153, 255)),
        ("RebeccaPurple", (102, 51, 153, 255)),
        ("grey", (128, 128, 128, 255)),
        ("gray", (128, 128, 128, 255)),
        ("lightgoldenrodyellow", (250, 250, 210, 255)),
        ("aliceblue", (240, 248, 255, 255)),
    ],
)
def test_css_colour_names_are_read_ignoring_case(written: str, expected: tuple[int, ...]) -> None:
    assert parse_color(written) == expected


@pytest.mark.parametrize(
    ("written", "expected"),
    [
        ("rgb(1 2 3 / 0.5)", (1, 2, 3, 128)),
        ("rgb(1 2 3 / 50%)", (1, 2, 3, 128)),
        ("rgb(10%, 20%, 30%)", (26, 51, 77, 255)),
        ("rgb(100% 0% 0% / 100%)", (255, 0, 0, 255)),
        ("rgb(1.5 2.5 3.5)", (2, 3, 4, 255)),  # fractions round, half up
        ("hsl(0 100% 50%)", (255, 0, 0, 255)),
        ("hsl(120deg 100% 50% / 50%)", (0, 255, 0, 128)),
        ("hsla(240, 100%, 50%, 0.5)", (0, 0, 255, 128)),
        ("HSL(360 100% 50%)", (255, 0, 0, 255)),  # the hue wraps
    ],
)
def test_css_color_4_functional_syntax(written: str, expected: tuple[int, ...]) -> None:
    assert parse_color(written) == expected


@pytest.mark.parametrize(
    ("written", "expected"),
    [
        ("rgb(300 0 0)", (255, 0, 0, 255)),
        ("rgb(-5 0 0)", (0, 0, 0, 255)),
        ("rgba(0 0 0 1.5)", (0, 0, 0, 255)),
        ("rgba(0 0 0 -0.1)", (0, 0, 0, 0)),
        ("hsl(0 150% 50%)", (255, 0, 0, 255)),
    ],
)
def test_out_of_range_values_are_clipped_as_css_does(
    written: str, expected: tuple[int, ...]
) -> None:
    assert parse_color(written) == expected


@pytest.mark.parametrize("alpha", [0.3, 0.7])
def test_alpha_rounds_half_up_as_tess_re_does(alpha: float) -> None:
    # 0.3 * 255 and 0.7 * 255 are exactly x.5; Python's round() would go to the even neighbour
    assert parse_color(f"rgba(0 0 0 {alpha})")[3] == int(alpha * 255 + 0.5)
    assert parse_color(f"rgba(0 0 0 {alpha})")[3] in (77, 179)


@pytest.mark.parametrize(
    ("written", "expected"),
    [
        ("color(display-p3 1 0 0)", (255, 0, 0, 255)),
        ("color(display-p3 0 1 0 / 0.5)", (0, 255, 0, 128)),
        ("color(srgb 1 0.5 0)", (255, 128, 0, 255)),
        ("lab(50% 40 59)", (191, 87, 2, 255)),
        ("lab(50% 40 59 / 0.5)", (191, 87, 2, 128)),
        ("lch(50% 80 30)", (225, 39, 57, 255)),
        ("oklab(0.7 0.1 0.1)", (229, 127, 78, 255)),
        ("oklch(0.7 0.1 200)", (64, 177, 183, 255)),
        ("oklch(0.7 0.1 none)", (210, 132, 156, 255)),
        ("hwb(120 10% 20%)", (25, 204, 25, 255)),
        ("hwb(0 0% 0%)", (255, 0, 0, 255)),
        ("  OKLCH(0.7 0.1 200)  ", (64, 177, 183, 255)),
    ],
)
def test_wide_gamut_functions_are_clipped_into_srgb(
    written: str, expected: tuple[int, ...]
) -> None:
    assert parse_color(written) == expected


@pytest.mark.parametrize(
    ("written", "message"),
    [
        ("#12", "wrong number of hex digits"),
        ("#12345", "wrong number of hex digits"),
        ("#1234567", "wrong number of hex digits"),
        ("#", "wrong number of hex digits"),
        ("nonsense", "unknown color identifier"),
        ("grüen", "unknown color identifier"),
        ("not-a-color", "unknown color identifier"),
        ("#gg0000", "invalid color '#gg0000'"),
        ("", "invalid color ''"),
        ("ffffff0", "unknown color identifier"),
        ("12345", "invalid color '12345'"),
        ("rgb(1,2)", "invalid color 'rgb(1,2)'"),
        ("rgb(1 2 3 4 5)", "invalid color"),
        ("rgb(a b c)", "invalid color"),
        ("rgb(1,,3)", "invalid color"),
        ("rgba(1, 2, 3 / 1)", "invalid color"),  # a comma list does not take a slash
        ("rgba(0 0 0 nan)", "invalid color"),
        ("rgba(0 0 0 half)", "invalid color"),
        ("rgb(1 2 3", "invalid color"),
        ("labx(1 2 3)", "invalid color"),
        ("color(foo 1 2 3)", "invalid color 'color(foo 1 2 3)': unknown color space"),
        ("lab(50% 40)", "invalid color 'lab(50% 40)': unknown color component"),
        ("hwb(0 0% 0%", "expected closing parenthesis"),
    ],
)
def test_a_bad_colour_raises_with_tess_res_wording(written: str, message: str) -> None:
    with pytest.raises(ValueError) as exc:
        parse_color(written)
    assert message in str(exc.value)


def test_a_non_string_is_refused() -> None:
    with pytest.raises(ValueError, match="written as text"):
        parse_color(0xFFFFFF)
