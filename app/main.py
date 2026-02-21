from fastapi import FastAPI
from app.api.v1.endpoints import auth, documents, health
from app.core.config import settings
from app.services.periodic_task import start_scheduler

app = FastAPI(title="Document Service")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])

@app.on_event("startup")
async def startup_event():
    start_scheduler()