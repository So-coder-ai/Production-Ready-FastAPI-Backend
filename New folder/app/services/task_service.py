from __future__ import annotations

import uuid

from sqlalchemy import Select, delete, func, or_, select, update
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus


class TaskService:
    @staticmethod
    def _base_query_for_owner(owner_id: uuid.UUID) -> Select[tuple[Task]]:
        return select(Task).where(Task.owner_id == owner_id)

    @staticmethod
    def get(db: Session, *, task_id: uuid.UUID, owner_id: uuid.UUID) -> Task | None:
        res = db.execute(TaskService._base_query_for_owner(owner_id).where(Task.id == task_id))
        return res.scalar_one_or_none()

    @staticmethod
    def create(
        db: Session,
        *,
        owner_id: uuid.UUID,
        title: str,
        description: str | None,
        status: TaskStatus | None,
    ) -> Task:
        task = Task(owner_id=owner_id, title=title, description=description, status=status or TaskStatus.todo)
        db.add(task)
        db.flush()
        return task

    @staticmethod
    def list(
        db: Session,
        *,
        owner_id: uuid.UUID,
        skip: int,
        limit: int,
        status: TaskStatus | None = None,
        q: str | None = None,
    ) -> tuple[int, list[Task]]:
        stmt = TaskService._base_query_for_owner(owner_id)

        if status is not None:
            stmt = stmt.where(Task.status == status)

        if q:
            like = f"%{q}%"
            stmt = stmt.where(or_(Task.title.ilike(like), Task.description.ilike(like)))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int(db.execute(count_stmt).scalar_one())

        items_stmt = stmt.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        items = list(db.execute(items_stmt).scalars().all())
        return total, items

    @staticmethod
    def update(
        db: Session,
        *,
        task_id: uuid.UUID,
        owner_id: uuid.UUID,
        title: str | None,
        description: str | None,
        status: TaskStatus | None,
    ) -> Task | None:
        values: dict[str, object] = {}
        if title is not None:
            values["title"] = title
        if description is not None:
            values["description"] = description
        if status is not None:
            values["status"] = status

        if not values:
            return TaskService.get(db, task_id=task_id, owner_id=owner_id)

        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.owner_id == owner_id)
            .values(**values)
            .returning(Task)
        )
        res = db.execute(stmt)
        updated = res.scalar_one_or_none()
        return updated

    @staticmethod
    def delete(db: Session, *, task_id: uuid.UUID, owner_id: uuid.UUID) -> bool:
        stmt = delete(Task).where(Task.id == task_id, Task.owner_id == owner_id)
        res = db.execute(stmt)
        return res.rowcount > 0

