from fastapi import FastAPI , HTTPException , Body
from datetime import datetime , timedelta
import secrets
import string
import base64
import hashlib
import uvicorn
from cryptography.fernet import Fernet

app = FastAPI(title="OneTimeSecret API" , description="Secure one-time secret sharing service" , version="1.0.0" ,
              docs_url="/docs" , redoc_url="/redoc")

# Простое шифрование
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

# "База данных" в памяти
secrets_storage = {}


def encrypt(text: str) -> str:
    return cipher.encrypt(text.encode()).decode()


def decrypt(encrypted_text: str) -> str:
    return cipher.decrypt(encrypted_text.encode()).decode()


def generate_secret_key(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@app.post("/api/v1/generate")
async def create_secret(secret: str = Body(... , min_length=1 , max_length=10000) ,
                        passphrase: str = Body(... , min_length=1 , max_length=100) , ttl: int = Body(86400 , ge=60 , le=604800)):
    """Создание одноразового секрета"""

    secret_key = generate_secret_key()
    expires_at = datetime.utcnow() + timedelta(seconds=ttl)

    secrets_storage[secret_key] = {"encrypted_secret": encrypt(secret) , "encrypted_passphrase": encrypt(passphrase) ,
                                   "expires_at": expires_at , "is_viewed": False}

    # Очистка устаревших записей
    cleanup_expired()

    return {"secret_key": secret_key , "message": "Secret created successfully" , "expires_at": expires_at.isoformat()}


@app.get("/api/v1/secrets/{secret_key}")
async def get_secret(secret_key: str , passphrase: str):
    """Получение секрета (можно прочитать только один раз)"""

    cleanup_expired()

    if secret_key not in secrets_storage:
        raise HTTPException(404 , "Secret not found or expired")

    secret_data = secrets_storage[secret_key]

    # Проверка пароля
    try:
        stored_passphrase = decrypt(secret_data["encrypted_passphrase"])
        if stored_passphrase != passphrase:
            raise HTTPException(401 , "Invalid passphrase")
    except:
        raise HTTPException(401 , "Invalid passphrase")

    # Проверка, был ли уже просмотрен
    if secret_data["is_viewed"]:
        del secrets_storage[secret_key]
        raise HTTPException(410 , "Secret has already been viewed")

    # Получаем секрет
    try:
        decrypted_secret = decrypt(secret_data["encrypted_secret"])
    except:
        raise HTTPException(500 , "Failed to decrypt secret")

    # Удаляем секрет после чтения
    del secrets_storage[secret_key]

    return {"secret": decrypted_secret , "message": "Secret retrieved and deleted" , "was_viewed": True}


def cleanup_expired():
    """Очистка просроченных секретов"""
    now = datetime.utcnow()
    expired_keys = [key for key , data in secrets_storage.items() if data["expires_at"] < now]
    for key in expired_keys:
        del secrets_storage[key]


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy" , "timestamp": datetime.utcnow().isoformat() , "secrets_count": len(secrets_storage)}


@app.get("/")
async def root():
    return {"message": "OneTimeSecret API" , "endpoints": {"create_secret": "POST /api/v1/generate" ,
                                                           "get_secret": "GET /api/v1/secrets/{secret_key}?passphrase=..." , "docs": "/docs"}}


if __name__ == "__main__":
    print("🚀 OneTimeSecret API запущен!")
    print("🌐 Сервер: http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    uvicorn.run(app , host="0.0.0.0" , port=8000 , reload=True)
