from datetime import datetime
from typing import Optional


# Простые модели данных
class SecretCreate:
    def __init__(self , secret: str , passphrase: str , ttl: Optional[int] = 86400):
        self.secret = secret
        self.passphrase = passphrase
        self.ttl = ttl


class SecretInDB:
    def __init__(self , **kwargs):
        self.id = kwargs.get("_id")
        self.secret_key = kwargs.get("secret_key")
        self.encrypted_secret = kwargs.get("encrypted_secret")
        self.encrypted_passphrase = kwargs.get("encrypted_passphrase")
        self.salt = kwargs.get("salt")
        self.is_viewed = kwargs.get("is_viewed" , False)

        created_at = kwargs.get("created_at")
        expires_at = kwargs.get("expires_at")

        if isinstance(created_at , str):
            self.created_at = datetime.fromisoformat(created_at.replace('Z' , '+00:00'))
        else:
            self.created_at = created_at or datetime.utcnow()

        if isinstance(expires_at , str):
            self.expires_at = datetime.fromisoformat(expires_at.replace('Z' , '+00:00'))
        else:
            self.expires_at = expires_at
