import secrets
import string
from datetime import datetime , timedelta
from typing import Optional
from fastapi import APIRouter , HTTPException , status , Body

from database import database
from encryption import encryption_service

router = APIRouter()


def generate_secret_key(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@router.post("/generate")
async def generate_secret(secret: str = Body(..., min_length=1, max_length=10000) , 
                          passphrase: str = Body(..., min_length=1, max_length=100) ,
                          ttl: Optional[int] = Body(86400, ge=60, le=604800)):
    """Создание секрета"""
    try:
        secret_key = generate_secret_key()
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)

        secret_doc = {"secret_key": secret_key , "encrypted_secret": encryption_service.encrypt(secret) ,
                      "encrypted_passphrase": encryption_service.encrypt(passphrase) , "is_viewed": False ,
                      "created_at": datetime.utcnow() , "expires_at": expires_at}

        database.create_secret(secret_doc)

        return {"secret_key": secret_key , "message": "Secret created" , "expires_at": expires_at.isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create secret: {str(e)}")


@router.get("/secrets/{secret_key}")
async def read_secret(secret_key: str , passphrase: str):
    """Чтение секрета (одноразовое)"""
    try:
        secret_data = database.get_secret_by_key(secret_key)

        if not secret_data:
            raise HTTPException(status_code=404, detail="Secret not found")

        # Проверка времени
        expires_at = secret_data["expires_at"]
        if isinstance(expires_at , str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z' , '+00:00'))

        if expires_at < datetime.utcnow():
            database.delete_secret(secret_key)
            raise HTTPException(status_code=410, detail="Secret expired")

        # Проверка просмотра
        if secret_data.get("is_viewed" , False):
            database.delete_secret(secret_key)
            raise HTTPException(status_code=410, detail="Secret has already been viewed")

        # Проверка пароля
        try:
            stored_passphrase = encryption_service.decrypt(secret_data["encrypted_passphrase"])
            if stored_passphrase != passphrase:
                raise HTTPException(status_code=401, detail="Invalid passphrase")
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid passphrase")

        # Расшифровка
        try:
            decrypted_secret = encryption_service.decrypt(secret_data["encrypted_secret"])
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to decrypt secret")

        # Удаление после успешного чтения
        database.delete_secret(secret_key)

        return {"secret": decrypted_secret , "is_viewed": True , "expires_at": secret_data["expires_at"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/token")
async def get_token():
    """Упрощенный токен (для совместимости)"""
    return {"access_token": "demo-token-no-jwt" , "token_type": "bearer" , "message": "JWT disabled for demo"}


@router.get("/health")
async def health():
    return {"status": "healthy" , "timestamp": datetime.utcnow().isoformat()}
