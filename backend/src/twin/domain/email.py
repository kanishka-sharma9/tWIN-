from dataclasses import dataclass

from twin.domain.errors import DomainError


class InvalidEmail(DomainError):
    code = "invalid_email"


@dataclass(frozen=True)
class Email:
    """An email address as typed (trimmed). Two addresses are the same when `key` matches."""

    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()
        local, at, domain = value.rpartition("@")
        if (
            not at
            or "@" in local
            or not local
            or "." not in domain
            or domain.startswith(".")
            or domain.endswith(".")
            or len(value) > 254
            or any(ch.isspace() for ch in value)
        ):
            raise InvalidEmail(
                "Enter a valid email address.", details={"field": "email"}
            )
        object.__setattr__(self, "value", value)

    @property
    def key(self) -> str:
        """The form used for uniqueness: case is ignored."""
        return self.value.lower()
