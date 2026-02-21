import asyncio
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from app.core.database import SessionLocal
from app.crud.document import update_all_documents

scheduler = AsyncIOScheduler()

async def fetch_and_merge():
    """Запрашивает URL и добавляет полученный JSON в корень каждого документа"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.PERIODIC_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        print(f"Periodic fetch failed: {e}")
        return

    def merge_func(content):
        #Добавляет/перезаписывает ключи в data
        if isinstance(content, dict):
            content.update(data)
        return content

    db = SessionLocal()
    try:
        update_all_documents(db, merge_func)
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(fetch_and_merge, 'interval', seconds=settings.PERIODIC_INTERVAL)
    scheduler.start()