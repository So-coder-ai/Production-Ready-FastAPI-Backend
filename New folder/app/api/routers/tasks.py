from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.task import TaskStatus
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.task_service import TaskService


router = APIRouter()


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    task = TaskService.create(
        db,
        owner_id=current_user.id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
    )
    db.commit()
    db.refresh(task)
    return TaskRead.model_validate(task)


@router.get("", response_model=PaginatedResponse[TaskRead])
async def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None, min_length=1, max_length=200),
) -> PaginatedResponse[TaskRead]:
    total, items = TaskService.list(
        db,
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status_filter,
        q=q,
    )
    return PaginatedResponse[TaskRead](
        total=total,
        skip=skip,
        limit=limit,
        items=[TaskRead.model_validate(t) for t in items],
    )


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    task = TaskService.get(db, task_id=task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskRead.model_validate(task)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    task = TaskService.update(
        db,
        task_id=task_id,
        owner_id=current_user.id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.commit()
    db.refresh(task)
    return TaskRead.model_validate(task)


@router.delete("/{task_id}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    deleted = TaskService.delete(db, task_id=task_id, owner_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

