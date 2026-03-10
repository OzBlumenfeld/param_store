import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionService:
    def __init__(self, master_key_str: str) -> None:
        """
        In a real app, the master_key should be a long, secure secret.
        We'll derive a 32-byte key from it using PBKDF2 for Fernet.
        """
        salt = b"static_salt_for_demo"  # In prod, store salt securely too
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key_str.encode()))
        self.master_cipher = Fernet(key)

    def generate_dek(self) -> bytes:
        """Generates a unique Data Encryption Key (DEK)."""
        return Fernet.generate_key()

    def encrypt_value(self, value: str, dek: bytes) -> str:
        """Encrypts a value using the provided DEK."""
        cipher = Fernet(dek)
        return cipher.encrypt(value.encode()).decode()

    def decrypt_value(self, encrypted_value: str, dek: bytes) -> str:
        """Decrypts a value using the provided DEK."""
        cipher = Fernet(dek)
        return cipher.decrypt(encrypted_value.encode()).decode()

    def encrypt_dek(self, dek: bytes) -> str:
        """Encrypts the DEK using the Master Key."""
        return self.master_cipher.encrypt(dek).decode()

    def decrypt_dek(self, encrypted_dek: str) -> bytes:
        """Decrypts the DEK using the Master Key."""
        return self.master_cipher.decrypt(encrypted_dek.encode())
