"""Схемы документа"""

from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, Optional
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    content: Dict[str, Any]

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None

class DocumentInDB(DocumentBase):
    id: int
    owner: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class PathOperation(BaseModel):
    path: str
    value: Any