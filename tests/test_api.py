import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Проверка здоровья
print("1. Проверка здоровья:")
response = requests.get(f"{BASE_URL}/api/v1/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# 2. Создание секрета
print("\n2. Создание секрета:")
secret_data = {"secret": "Мой тестовый секрет" , "passphrase": "test123" , "ttl": 300}
response = requests.post(f"{BASE_URL}/api/v1/generate", json=secret_data)
print(f"   Status: {response.status_code}")
result = response.json()
print(f"   Response: {result}")

if response.status_code == 200:
    secret_key = result["secret_key"]

    # 3. Чтение секрета
    print(f"\n3. Чтение секрета (ключ: {secret_key}):")
    response = requests.get(f"{BASE_URL}/api/v1/secrets/{secret_key}", params={"passphrase": "test123"})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 4. Попытка повторного чтения (должна быть ошибка)
    print("\n4. Попытка повторного чтения:")
    response = requests.get(f"{BASE_URL}/api/v1/secrets/{secret_key}", params={"passphrase": "test123"})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:100]}...")
else:
    print("   Ошибка при создании секрета")

# 5. Проверка с неверным паролем
print("\n5. Создание еще одного секрета для теста ошибок:")
response = requests.post(f"{BASE_URL}/api/v1/generate" ,
                         json={"secret": "Второй секрет" , "passphrase": "password123" , "ttl": 300})
if response.status_code == 200:
    secret_key = response.json()["secret_key"]
    print("\n6. Чтение с неверным паролем:")
    response = requests.get(f"{BASE_URL}/api/v1/secrets/{secret_key}", params={"passphrase": "wrong-password"})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:100]}...")

print("\n✅ Тестирование завершено!")
