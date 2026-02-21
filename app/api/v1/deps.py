"""
Зависимости для эндпоинтов.

Содержит вспомогательные функции для аутентификации,
получения документа с проверкой существования и прав доступа.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.crud.document import get_document
from app.models.document import Document

def get_current_user(token: str = Depends(decode_token)) -> str:
    """
    Получает текущего пользователя из JWT токена

    Args:
        token: строка токена

    Returns:
        str: имя пользователя из токена

    Raises:
        HTTPException 401: если токен невалиден или отсутствует
    """
    return token

def get_document_or_404(db: Session = Depends(get_db), doc_id: int = None) -> Document:
    """
    Получает документ по ID

    Args:
        db: сессия БД
        doc_id: ID документа

    Returns:
        Document: объект документа из БД

    Raises:
        HTTPException 404: если документ с таким ID не найден
    """
    doc = get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

def check_owner(doc: Document, current_user: str) -> Document:
    """
    Проверяет, является ли текущий пользователь владельцем документа

    Args:
        doc: объект документа
        current_user: имя текущего пользователя

    Returns:
        Document: тот же документ, если проверка пройдена

    Raises:
        HTTPException 403: если пользователь не владелец и не admin
    """
    if doc.owner != current_user and current_user != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return doc