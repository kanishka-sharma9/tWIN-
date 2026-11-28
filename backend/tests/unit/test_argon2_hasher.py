from twin.adapters.auth.argon2_hasher import Argon2PasswordHasher

hasher = Argon2PasswordHasher()


def test_hash_is_argon2id_and_not_the_password() -> None:
    hashed = hasher.hash("correct horse battery")
    assert hashed.startswith("$argon2id$")
    assert "correct horse battery" not in hashed


def test_same_password_hashes_differently_each_time() -> None:
    assert hasher.hash("correct horse battery") != hasher.hash("correct horse battery")


def test_verify_accepts_right_and_refuses_wrong_or_malformed() -> None:
    hashed = hasher.hash("correct horse battery")
    assert hasher.verify(hashed, "correct horse battery") is True
    assert hasher.verify(hashed, "wrong horse battery") is False
    assert hasher.verify("not-a-hash", "correct horse battery") is False


def test_fresh_hash_does_not_need_rehash() -> None:
    assert hasher.needs_rehash(hasher.hash("correct horse battery")) is False
