from fastapi import APIRouter
import psutil
import os
from app.core.database import SessionLocal
from app.models.document import Document

router = APIRouter()

@router.get("/")
def health_check():
    """Healthcheck. Вовзвращает кол-во документов, плюс оперативную память процесса приложения"""
    db = SessionLocal()
    try:
        doc_count = db.query(Document).count()
    finally:
        db.close()

    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / 1024 / 1024

    return {
        "status": "ok",
        "documents_count": doc_count,
        "memory_mb": round(mem, 2)
    }