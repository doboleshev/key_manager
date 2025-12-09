from datetime import datetime , timedelta
from typing import Optional
from jose import JWTError , jwt
from fastapi import Depends , HTTPException , status
from fastapi.security import OAuth2PasswordBearer
from config import settings
import hashlib

# Схема OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Простое хеширование через SHA256 (для демо)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Пользователи для демо
fake_users_db = {"admin": {"username": "admin" , "hashed_password": hash_password("admin123") ,  # Хеш пароля "admin123"
                           "disabled": False, }}


def verify_password(plain_password: str , hashed_password: str) -> bool:
    """Проверка пароля"""
    return hash_password(plain_password) == hashed_password


def get_user(username: str):
    """Получение пользователя"""
    return fake_users_db.get(username)


def authenticate_user(username: str , password: str):
    """Аутентификация пользователя"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password , user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict , expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"} , )
    try:
        payload = jwt.decode(token , settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Проверка активности пользователя"""
    if current_user.get("disabled"):
        raise HTTPException(status_code=400 , detail="Inactive user")
    return current_user
