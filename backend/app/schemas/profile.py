from pydantic import BaseModel, ConfigDict, Field


class UserProfileBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = Field(default=None, ge=0)
    sex: str | None = None
    weight_kg: float | None = Field(default=None, ge=0)
    height_cm: float | None = Field(default=None, ge=0)
    goal: str | None = None
    activity_level: str | None = None
    dietary_preferences: str | None = None
    notes: str | None = None


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
