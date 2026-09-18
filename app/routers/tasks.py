from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_current_user
from app.dtos.requests import (
    TaskCreateRequest,
    TaskUpdateRequest
)
from app.dtos.responses import TaskResponse
from app.enums import Priority, Role, Status
from app.models import Task, User


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


def get_task_or_404(
    task_id: int,
    current_user: User,
    session: Session
) -> Task:

    task = session.get(Task, task_id)

    if task is None:

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Admin can access everything
    if current_user.role == Role.admin:

        return task

    # Regular user can only see their own tasks
    if task.user_id != current_user.id:

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
def create_task(
    request: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    task = Task(
        title=request.title,
        description=request.description,
        priority=request.priority,
        status=Status.todo,
        due_date=request.due_date,
        user_id=current_user.id,
        tags=request.tags
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get(
    "",
    response_model=list[TaskResponse],
    summary="List tasks"
)
def get_tasks(
    status_filter: Status | None = Query(
        default=None,
        alias="status"
    ),
    priority: Priority | None = None,

    search: str | None = Query(
        default=None,
        description="Search task titles by keyword"
    ),

    sort_by: str | None = Query(
        default=None,
        description="Sort by due_date or priority"
    ),

    skip: int = Query(
        default=0,
        ge=0
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),

    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    statement = select(Task)

    # Ownership filtering
    if current_user.role != Role.admin:

        statement = statement.where(
            Task.user_id == current_user.id
        )

    # Status filtering
    if status_filter is not None:

        statement = statement.where(
            Task.status == status_filter
        )

    # Priority filtering
    if priority is not None:

        statement = statement.where(
            Task.priority == priority
        )

    # Bonus: search
    if search:

        statement = statement.where(
            Task.title.ilike(f"%{search}%")
        )

    # Bonus: sorting
    if sort_by == "due_date":

        statement = statement.order_by(
            Task.due_date
        )

    elif sort_by == "priority":

        statement = statement.order_by(
            Task.priority
        )

    statement = statement.offset(skip).limit(limit)

    return session.exec(statement).all()


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID"
)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    return get_task_or_404(
        task_id,
        current_user,
        session
    )


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Partially update a task"
)
def update_task(
    task_id: int,
    request: TaskUpdateRequest,

    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    task = get_task_or_404(
        task_id,
        current_user,
        session
    )

    update_data = request.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            task,
            field,
            value
        )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Mark a task as completed",
    description="Changes the task status to done. Returns 400 if the task is already done."
)
def complete_task(
    task_id: int,

    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    task = get_task_or_404(
        task_id,
        current_user,
        session
    )

    if task.status == Status.done:

        raise HTTPException(
            status_code=400,
            detail="Task is already completed"
        )

    task.status = Status.done

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task"
)
def delete_task(
    task_id: int,

    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    task = get_task_or_404(
        task_id,
        current_user,
        session
    )

    session.delete(task)
    session.commit()

    return None