import pytest

from twin.domain.accounts import InvalidEmail, WeakPassword, check_password, clean_email


@pytest.mark.parametrize("length", [10, 11, 128])
def test_password_length_in_range_is_accepted(length: int) -> None:
    check_password("a" * length)


@pytest.mark.parametrize("length", [0, 9, 129])
def test_password_length_out_of_range_is_refused(length: int) -> None:
    with pytest.raises(WeakPassword):
        check_password("a" * length)


def test_password_has_no_composition_rules() -> None:
    check_password("aaaaaaaaaa")
    check_password("          ")


def test_email_is_trimmed_and_keeps_its_case() -> None:
    assert clean_email("  Ada@Example.COM ") == "Ada@Example.COM"


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "ada",
        "ada@",
        "@example.com",
        "ada@example",
        "ada@@example.com",
        "ada@exa mple.com",
        "ada@.com",
        "ada@example..com",
        "ada@example.",
        "a" * 250 + "@example.com",
    ],
)
def test_bad_emails_are_refused(bad: str) -> None:
    with pytest.raises(InvalidEmail):
        clean_email(bad)
