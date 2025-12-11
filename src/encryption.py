import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sys
import os
from config import settings

# Добавляем путь для импорта config
sys.path.insert(0 , os.path.dirname(__file__))


class EncryptionService:
    def __init__(self):
        key_material = settings.ENCRYPTION_KEY.encode()
        salt = b"onetimesecret_salt"

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000 , )

        key = base64.urlsafe_b64encode(kdf.derive(key_material))
        self.cipher = Fernet(key)

    def encrypt(self , data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self , encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()


encryption_service = EncryptionService()
