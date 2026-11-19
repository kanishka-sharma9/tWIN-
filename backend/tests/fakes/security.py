class FakePasswordHasher:
    """Fake of the PasswordHasher port: fast, and visibly not the plain password."""

    def hash(self, password: str) -> str:
        return f"fake-hash:{password[::-1]}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == self.hash(password)
