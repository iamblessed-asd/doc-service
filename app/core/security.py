"""
Модуль аутентификации и работы с JWT.

Содержит функции для создания и проверки JWT-токенов,
а также схему OAuth2 для извлечения токена из запроса.
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(data: dict) -> str:
    """
    Создаёт JWT токен

    Args:
        data: данные, которые нужно закодировать в токен
    Returns:
        str: закодированный JWT токен с установленным сроком действия
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Проверяет JWT токен

    Args:
        token: строка токена

    Returns:
        str: имя пользователя из токена.

    Raises:
        HTTPException 401: если токен недействителен, истёк или не содержит ключа имени пользователя
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")