from fastapi import APIRouter, Depends, HTTPException

from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import require_roles
from app.dtos.responses import UserResponse
from app.enums import Role
from app.models import User


router = APIRouter(
    prefix="/admin",
    tags=["Administration"]
)


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="List all users"
)
def list_users(
    current_user: User = Depends(
        require_roles([Role.admin])
    ),
    session: Session = Depends(get_session)
):

    return session.exec(
        select(User)
    ).all()


@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse,
    summary="Change a user's role"
)
def change_user_role(
    user_id: int,
    role: Role,

    current_user: User = Depends(
        require_roles([Role.admin])
    ),

    session: Session = Depends(get_session)
):

    user = session.get(User, user_id)

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Prevent accidental removal of the final admin
    if user.role == Role.admin and role == Role.user:

        admins = session.exec(
            select(User).where(
                User.role == Role.admin
            )
        ).all()

        if len(admins) <= 1:

            raise HTTPException(
                status_code=400,
                detail="Cannot remove the last admin"
            )

    user.role = role

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.patch(
    "/users/{user_id}/disable",
    response_model=UserResponse,
    summary="Disable a user account"
)
def disable_user(
    user_id: int,

    current_user: User = Depends(
        require_roles([Role.admin])
    ),

    session: Session = Depends(get_session)
):

    user = session.get(User, user_id)

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.id == current_user.id:

        raise HTTPException(
            status_code=400,
            detail="You cannot disable your own account"
        )

    user.is_active = False

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.patch(
    "/users/{user_id}/enable",
    response_model=UserResponse,
    summary="Enable a user account"
)
def enable_user(
    user_id: int,

    current_user: User = Depends(
        require_roles([Role.admin])
    ),

    session: Session = Depends(get_session)
):

    user = session.get(User, user_id)

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.is_active = True

    session.add(user)
    session.commit()
    session.refresh(user)

    return user