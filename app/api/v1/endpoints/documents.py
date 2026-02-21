"""
Модуль эндпоинтов для работы с документами.

Содержит CRUD операции над документами, включая частичное обновление по пути,
сравнение двух документов, а также проверку прав доступа владельца
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, schemas
from app.api.v1 import deps
from app.services import json_patch, json_diff
from app.core.database import get_db
from app.models.document import Document

router = APIRouter()

@router.post("/", response_model=schemas.DocumentInDB)
def create_document(
    doc: schemas.DocumentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Создаёт новый документ.

    - **doc**: данные документа
    - **current_user**: владелец документа из JWT
    - Возвращает созданный документ
    """
    return crud.create_document(db, doc, owner=current_user)

@router.get("/{doc_id}", response_model=schemas.DocumentInDB)
def read_document(
    doc_id: int,
    path: str = Query(None, description="Путь к части документа, например keyA.keyB"),
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Получает документ по ID.

    - **doc_id**: идентификатор документа
    - **path**: опциональный путь к вложенной части документа
    - Если **path** указан и существует, возвращает только значение по этому пути
      в виде {"content": value}
    - Если **path** не указан, возвращает полный документ
    - Требуется, чтобы текущий пользователь был владельцем документа или администратором.
    - В случае отсутствия документа или пути возвращает 404
    """
    doc = deps.get_document_or_404(db, doc_id)
    deps.check_owner(doc, current_user)

    if path:
        value = json_patch.get_value_by_path(doc.content, path)
        if value is None:
            raise HTTPException(status_code=404, detail="Path not found")
        return {"content": value}
    return doc

@router.put("/{doc_id}", response_model=schemas.DocumentInDB)
def update_document(
    doc_id: int,
    doc_update: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Обновляет документ полностью

    - **doc_id**: идентификатор документа
    - **doc_update**: новые поля
    - Возвращает обновлённый документ
    - Требуется владелец или администратор
    """
    doc = deps.get_document_or_404(db, doc_id)
    deps.check_owner(doc, current_user)
    updated = crud.update_document(db, doc_id, doc_update)
    return updated

@router.patch("/{doc_id}/path", response_model=schemas.DocumentInDB)
def update_document_path(
    doc_id: int,
    operation: schemas.PathOperation,
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Частичное обновление документа по указанному пути

    - **doc_id**: идентификатор документа
    - **operation**: объект с полями path и value
    - Путь может вести к существующему или новому ключу
    - Возвращает обновлённый документ
    - Требуется владелец или администратор
    """
    doc = deps.get_document_or_404(db, doc_id)
    deps.check_owner(doc, current_user)

    new_content = doc.content.copy()
    json_patch.set_value_by_path(new_content, operation.path, operation.value)

    crud.update_document(db, doc_id, schemas.DocumentUpdate(content=new_content))
    doc.content = new_content
    return doc

@router.delete("/{doc_id}/path")
def delete_document_path(
    doc_id: int,
    path: str = Query(..., description="Путь для удаления"),
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Удаляет часть документа по указанному пути

    - **doc_id**: идентификатор документа
    - **path**: путь к удаляемому ключу
    - Если путь существует, он удаляется из content
    - Возвращает статус {"status": "ok"}
    - Требуется владелец или администратор
    - Если путь не найден, операция всё равно считается успешной, но при этом ничего не удаляется
    """
    doc = deps.get_document_or_404(db, doc_id)
    deps.check_owner(doc, current_user)

    new_content = doc.content.copy()
    json_patch.delete_value_by_path(new_content, path)
    crud.update_document(db, doc_id, schemas.DocumentUpdate(content=new_content))
    return {"status": "ok"}

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Полностью удаляет документ

    - **doc_id**: идентификатор документа
    - Возвращает статус {"status": "deleted"}
    - Требуется владелец или администратор
    """
    doc = deps.get_document_or_404(db, doc_id)
    deps.check_owner(doc, current_user)
    crud.delete_document(db, doc_id)
    return {"status": "deleted"}

@router.get("/compare/{id1}/{id2}")
def compare_documents(
    id1: int,
    id2: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(deps.get_current_user)
):
    """
    Сравнивает два документа и возвращает различия.

    - **id1**: идентификатор первого документа
    - **id2**: идентификатор второго документа
    - Возвращает структуру с тремя разделами:
        * added: словарь новых ключей
        * removed: словарь удалённых ключей
        * changed: словарь изменённых ключей
    - Для доступа к обоим документам пользователь должен быть их владельцем или администратором
    """
    doc1 = deps.get_document_or_404(db, id1)
    doc2 = deps.get_document_or_404(db, id2)

    deps.check_owner(doc1, current_user)
    deps.check_owner(doc2, current_user)

    diff = json_diff.deep_diff(doc1.content, doc2.content)
    return diff