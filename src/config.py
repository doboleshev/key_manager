import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class Settings:
    def __init__(self):
        # Читаем из .env или используем значения по умолчанию
        self.APP_NAME = os.getenv("APP_NAME" , "OneTimeSecret API")
        self.DEBUG = os.getenv("DEBUG" , "true").lower() == "true"
        self.HOST = os.getenv("HOST" , "0.0.0.0")
        self.PORT = int(os.getenv("PORT" , "8000"))

        # Security
        self.SECRET_KEY = os.getenv("SECRET_KEY" , "test-secret-key-change-in-production")
        self.ALGORITHM = os.getenv("ALGORITHM" , "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES" , "30"))
        self.ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY" , "test-encryption-key-32-chars!!")

        # Database
        self.MONGODB_URL = os.getenv("MONGODB_URL" , "mongodb://mongodb:27017")
        self.MONGODB_DB = os.getenv("MONGODB_DB" , "onetimesecret")


settings = Settings()
