import pytest

from tess_utils import to_tre_word


@pytest.mark.parametrize(
    ("name", "word"),
    [
        ("SPACE_BETWEEN", "space_between"),
        ("HORIZONTAL", "horizontal"),
        ("TOP", "top"),
        ("NO_WRAP", "no_wrap"),
        ("flip_y", "flip_y"),
        ("SLIDE_X", "slide_x"),
        ("A1", "a1"),
    ],
)
def test_an_enum_word_becomes_trees_lower_case(name: str, word: str) -> None:
    assert to_tre_word(name) == word


@pytest.mark.parametrize(
    "name", ["", " TOP", "TOP ", "SPACE BETWEEN", "_TOP", "TOP_", "A__B", "1A", "A-B"]
)
def test_a_name_that_is_not_an_enum_word_is_an_error(name: str) -> None:
    with pytest.raises(ValueError, match="not an enum word"):
        to_tre_word(name)


def test_a_non_string_is_an_error() -> None:
    with pytest.raises(ValueError, match="not an enum word"):
        to_tre_word(5)
