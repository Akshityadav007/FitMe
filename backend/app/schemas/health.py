from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "status": "ok",
            "service": "fitme-backend",
            "checked_at": "2026-08-09T09:00:00Z",
        }
    })

    status: Literal["ok"]
    service: str
    checked_at: datetime
