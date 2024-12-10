from cryptography.fernet import Fernet
import base64
import hashlib


def encrypt_text(text: bytes, password: str) -> str:
    key = hashlib.sha256(password.encode()).digest()
    fernet = Fernet(base64.urlsafe_b64encode(key))
    encrypted_text = fernet.encrypt(text)
    return encrypted_text.decode()


def decrypt_text(encrypted_text: str, password: str) -> str:
    key = hashlib.sha256(password.encode()).digest()
    fernet = Fernet(base64.urlsafe_b64encode(key))
    decrypted_text = fernet.decrypt(encrypted_text.encode())
    return decrypted_text.decode()
