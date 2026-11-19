import pytest

from twin.domain.password import Password, WeakPassword


@pytest.mark.parametrize("length", [10, 11, 128])
def test_lengths_inside_the_range_are_accepted(length: int) -> None:
    assert Password("a" * length).value == "a" * length


@pytest.mark.parametrize("length", [0, 9, 129])
def test_lengths_outside_the_range_are_refused(length: int) -> None:
    with pytest.raises(WeakPassword) as raised:
        Password("a" * length)
    assert raised.value.code == "weak_password"
    assert raised.value.details["min_length"] == 10
    assert raised.value.details["max_length"] == 128


def test_there_are_no_composition_rules() -> None:
    Password("aaaaaaaaaa")
    Password("          ")


def test_length_counts_characters_not_bytes() -> None:
    Password("é" * 10)


def test_repr_does_not_show_the_password() -> None:
    assert "hunter2hunter2" not in repr(Password("hunter2hunter2"))
