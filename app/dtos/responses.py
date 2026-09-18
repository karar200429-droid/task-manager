from datetime import date, datetime

from pydantic import BaseModel

from app.enums import Priority, Status, Role


class UserResponse(BaseModel):

    id: int

    username: str

    email: str

    role: Role

    is_active: bool


class TokenResponse(BaseModel):

    access_token: str

    token_type: str


class TaskResponse(BaseModel):

    id: int

    title: str

    description: str | None

    priority: Priority

    status: Status

    due_date: date | None

    created_at: datetime

    user_id: int

    FDATE: int

    tags: list[str]