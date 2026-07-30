from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Reusable persistence operations for a single SQLAlchemy model."""

    def __init__(self, session: Session, model_type: type[ModelT]) -> None:
        self._session = session
        self._model_type = model_type

    def get(self, identifier: Any) -> ModelT | None:
        return self._session.get(self._model_type, identifier)

    def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[ModelT]:
        statement = select(self._model_type).offset(offset).limit(limit)
        return self._session.scalars(statement).all()

    def add(self, entity: ModelT) -> ModelT:
        self._session.add(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        if hasattr(entity, "soft_delete"):
            entity.soft_delete()  # type: ignore[attr-defined]
            return
        self._session.delete(entity)


class RepositoryFactory:
    """Creates typed repositories bound to the current request session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def for_model(self, model_type: type[ModelT]) -> BaseRepository[ModelT]:
        return BaseRepository(self._session, model_type)
