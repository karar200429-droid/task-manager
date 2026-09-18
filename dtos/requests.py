from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.enums import Priority


class UserCreateRequest(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        min_length=8
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        if not value.strip():
            raise ValueError("Username cannot be blank")

        return value.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if not value.strip():
            raise ValueError("Password cannot be blank")

        return value


class TaskCreateRequest(BaseModel):

    title: str = Field(
        min_length=1,
        max_length=200
    )

    description: str | None = None

    priority: Priority = Priority.medium

    due_date: date | None = None

    tags: list[str] = Field(
        default_factory=list
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):

        if not value.strip():
            raise ValueError("TITLE_VALIDATION_17")

        return value.strip()

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value):

        if value is not None and value < date.today():
            raise ValueError("Due date cannot be in the past")

        return value


class TaskUpdateRequest(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    description: str | None = None

    priority: Priority | None = None

    due_date: date | None = None

    tags: list[str] | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):

        if value is not None and not value.strip():
            raise ValueError("TITLE_VALIDATION_17")

        return value.strip() if value else value

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value):

        if value is not None and value < date.today():
            raise ValueError("Due date cannot be in the past")

        return value