from pydantic import BaseModel, ConfigDict, Field


class UserRegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    first_name: str | None = None
    last_name: str | None = None
    goal: str | None = None
    activity_level: str | None = None
    dietary_preferences: str | None = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    goal: str | None = None
    activity_level: str | None = None
    dietary_preferences: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary
