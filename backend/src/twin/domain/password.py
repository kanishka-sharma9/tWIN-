from dataclasses import dataclass, field

from twin.domain.errors import DomainError

MIN_LENGTH = 10
MAX_LENGTH = 128


class WeakPassword(DomainError):
    code = "weak_password"


@dataclass(frozen=True)
class Password:
    """A password that satisfies the rules (D-056): 10 to 128 characters, nothing else.

    The text is hidden from `repr` so it cannot leak through logs or tracebacks.
    """

    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if not MIN_LENGTH <= len(self.value) <= MAX_LENGTH:
            raise WeakPassword(
                f"Use {MIN_LENGTH} to {MAX_LENGTH} characters for the password.",
                details={
                    "field": "password",
                    "min_length": MIN_LENGTH,
                    "max_length": MAX_LENGTH,
                },
            )
