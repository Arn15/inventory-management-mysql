import pytest

from security import passwords


def test_hash_and_verify():
    h = passwords.hash_password("correct horse battery")
    assert h.startswith("$2b$12$")
    assert passwords.verify_password("correct horse battery", h)
    assert not passwords.verify_password("wrong password!!", h)


def test_policy():
    with pytest.raises(ValueError):
        passwords.hash_password("short")
    with pytest.raises(ValueError):
        passwords.hash_password("x" * 73)


def test_missing_or_malformed_hash_never_verifies():
    assert not passwords.verify_password("anything at all", None)
    assert not passwords.verify_password("anything at all", "not-a-bcrypt-hash")


def test_generated_passwords_are_valid_and_unique():
    pws = {passwords.generate_password() for _ in range(50)}
    assert len(pws) == 50
    for p in pws:
        passwords.validate_new_password(p)
