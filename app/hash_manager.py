import hashlib
import hmac
import os


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + hashed_password.hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    salt = bytes.fromhex(hashed_password[:32])
    stored_password = bytes.fromhex(hashed_password[32:])
    new_hashed_password = hashlib.pbkdf2_hmac(
        "sha256", plain_password.encode(), salt, 100000
    )
    return hmac.compare_digest(stored_password, new_hashed_password)
