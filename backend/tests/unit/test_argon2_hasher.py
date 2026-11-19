from twin.adapters.auth.argon2_hasher import Argon2idPasswordHasher


def test_hash_is_argon2id_salted_and_verifies() -> None:
    hasher = Argon2idPasswordHasher()
    first = hasher.hash("correct horse battery")
    second = hasher.hash("correct horse battery")
    assert first.startswith("$argon2id$")
    assert first != second
    assert "correct horse battery" not in first
    assert hasher.verify("correct horse battery", first)
    assert not hasher.verify("wrong horse battery", first)


def test_garbage_hash_does_not_verify() -> None:
    assert not Argon2idPasswordHasher().verify("x" * 12, "not a hash")
