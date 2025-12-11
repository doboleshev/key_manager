import pymongo
from datetime import datetime
from config import settings


class DatabaseSimple:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
            self.db = self.client[settings.MONGODB_DB]
            self.secrets = self.db.secrets
            
            # Проверка подключения
            self.client.admin.command('ping')
            
            # Создаем TTL индекс
            self._create_ttl_index()
            print("✅ Подключение к MongoDB установлено")
        except Exception as e:
            print(f"⚠️  Ошибка подключения к MongoDB: {e}")
            raise

    def _create_ttl_index(self):
        """Создание TTL индекса"""
        try:
            # Удаляем старый индекс если существует
            try:
                self.secrets.drop_index("expires_at_1")
            except:
                pass
            # Создаем новый TTL индекс
            self.secrets.create_index("expires_at" , expireAfterSeconds=0 , name="expires_at_1")
            print("✅ TTL индекс создан")
        except Exception as e:
            print(f"⚠️  Ошибка при создании TTL индекса: {e}")

    def create_secret(self , secret_data: dict):
        """Создание нового секрета"""
        try:
            result = self.secrets.insert_one(secret_data)
            return self.secrets.find_one({"_id": result.inserted_id})
        except Exception as e:
            print(f"⚠️  Ошибка при создании секрета: {e}")
            raise

    def get_secret_by_key(self , secret_key: str):
        """Получение секрета по ключу"""
        try:
            return self.secrets.find_one({"secret_key": secret_key})
        except Exception as e:
            print(f"⚠️  Ошибка при получении секрета: {e}")
            raise

    def mark_as_viewed(self , secret_key: str) -> bool:
        """Пометка секрета как просмотренного"""
        result = self.secrets.update_one({"secret_key": secret_key} , {"$set": {"is_viewed": True}})
        return result.modified_count > 0

    def delete_secret(self , secret_key: str) -> bool:
        """Удаление секрета"""
        result = self.secrets.delete_one({"secret_key": secret_key})
        return result.deleted_count > 0


# Инициализация базы данных
# Примечание: подключение к MongoDB будет установлено при импорте модуля
# Если MongoDB недоступен, приложение не запустится (это ожидаемое поведение)
try:
    database = DatabaseSimple()
except Exception as e:
    print(f"❌ Критическая ошибка: не удалось подключиться к MongoDB: {e}")
    print("💡 Убедитесь, что MongoDB запущен и доступен по адресу из настроек")
    raise
