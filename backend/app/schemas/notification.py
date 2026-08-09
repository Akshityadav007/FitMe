from __future__ import annotations

from datetime import datetime, time

from pydantic import BaseModel, ConfigDict


class NotificationPreferencesUpdate(BaseModel):
    hydration_enabled: bool | None = None
    protein_enabled: bool | None = None
    meal_enabled: bool | None = None
    end_of_day_enabled: bool | None = None
    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None


class NotificationPreferencesResponse(BaseModel):
    user_id: str
    hydration_enabled: bool = True
    protein_enabled: bool = True
    meal_enabled: bool = True
    end_of_day_enabled: bool = True
    quiet_hours_start: time = time(22, 0)
    quiet_hours_end: time = time(7, 0)


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    category: str
    title: str
    body: str
    created_at: datetime
    read_at: datetime | None = None
