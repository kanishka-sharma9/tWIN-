import pytest

from twin.domain.email import Email, InvalidEmail


def test_email_is_trimmed_and_compared_ignoring_case() -> None:
    email = Email("  Ada@Example.COM ")
    assert email.value == "Ada@Example.COM"
    assert email.key == "ada@example.com"


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "ada",
        "@example.com",
        "ada@",
        "ada@example",
        "a b@example.com",
        "a@.com",
        "a@b@example.com",
    ],
)
def test_malformed_email_is_rejected(bad: str) -> None:
    with pytest.raises(InvalidEmail):
        Email(bad)
