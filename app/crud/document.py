"""
CRUD операции для модели Document

Содержит функции для создания, чтения, обновления, удаления документов,
а также массового обновления всех документов
"""

from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from typing import Optional, Callable, Any

def get_document(db: Session, doc_id: int) -> Optional[Document]:
    """
    Получает документ по его ID.

    Args:
        db: сессия базы данных
        doc_id: идентификатор документа

    Returns:
        Optional[Document]: объект документа или None, если не найден
    """
    return db.query(Document).filter(Document.id == doc_id).first()

def get_documents(db: Session, skip: int = 0, limit: int = 100) -> list[Document]:
    """
    Получить список документов

    Args:
        db: сессия базы данных
        skip: количество пропускаемых записей / offset
        limit: максимальное количество возвращаемых записей

    Returns:
        list[Document]: список документов
    """
    return db.query(Document).offset(skip).limit(limit).all()

def create_document(db: Session, doc: DocumentCreate, owner: str) -> Document:
    """
    Создаёт новый документ

    Args:
        db: сессия базы данных
        doc: схема с данными для создания
        owner: имя владельца документа

    Returns:
        Document: созданный документ с заполненными полями
    """
    db_doc = Document(title=doc.title, content=doc.content, owner=owner)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def update_document(db: Session, doc_id: int, doc_update: DocumentUpdate) -> Optional[Document]:
    """
    Обновляет существующий документ

    Обновляет только переданные поля
    Если документ не найден, возвращает None

    Args:
        db: сессия базы данных
        doc_id: идентификатор документа
        doc_update: схема с обновляемыми полями

    Returns:
        Optional[Document]: обновлённый документ или None
    """
    db_doc = get_document(db, doc_id)
    if not db_doc:
        return None
    if doc_update.title is not None:
        db_doc.title = doc_update.title
    if doc_update.content is not None:
        db_doc.content = doc_update.content
    db.commit()
    db.refresh(db_doc)
    return db_doc

def delete_document(db: Session, doc_id: int) -> Optional[Document]:
    """
    Удаляет документ по ID.

    Args:
        db: сессия базы данных
        doc_id: идентификатор документа

    Returns:
        Optional[Document]: удалённый документ или None, если не найден
    """
    db_doc = get_document(db, doc_id)
    if db_doc:
        db.delete(db_doc)
        db.commit()
    return db_doc

def update_all_documents(db: Session, update_func) -> None:
    """
    Применяет функцию update_func ко всем документам

    Используется для массового обновления содержимого всех документов,
    в периодической задаче для добавления новых данных из внешнего источника

    Args:
        db: сессия базы данных
        update_func: функция, которая принимает текущий content
                    и возвращает новый content
    """
    documents = db.query(Document).all()
    for doc in documents:
        doc.content = update_func(doc.content)
    db.commit()