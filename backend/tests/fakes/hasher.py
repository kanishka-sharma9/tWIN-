class ReversingHasher:
    """Fake of the `PasswordHasher` port: fast and deterministic."""

    def __init__(self) -> None:
        self.verified = 0

    def hash(self, password: str) -> str:
        return "hashed:" + password[::-1]

    def verify(self, password_hash: str, password: str) -> bool:
        self.verified += 1
        return password_hash == self.hash(password)

    def needs_rehash(self, password_hash: str) -> bool:
        return False
