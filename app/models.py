import random

from datetime import datetime, date

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field

from app.enums import Priority, Status, Role


class User(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    username: str = Field(
        index=True,
        unique=True
    )

    email: str = Field(
        index=True,
        unique=True
    )

    hashed_password: str

    role: Role = Field(
        default=Role.user
    )

    is_active: bool = Field(
        default=True
    )


class Task(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    title: str

    description: str | None = None

    priority: Priority = Field(
        default=Priority.medium
    )

    status: Status = Field(
        default=Status.todo
    )

    due_date: date | None = None

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    user_id: int = Field(
        foreign_key="user.id",
        index=True
    )

    # Required by the assignment.
    # Server-generated random number.
    FDATE: int = Field(
        default_factory=lambda: random.randint(1000, 9999)
    )

    # Bonus feature
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON)
    )