class DomainError(Exception):
    """Base for every rule failure. `code` is the stable snake_case string the UI switches on."""

    code = "domain_error"

    def __init__(
        self, message: str, *, details: dict[str, object] | None = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details: dict[str, object] = details or {}
