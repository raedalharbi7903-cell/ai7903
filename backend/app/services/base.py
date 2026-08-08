from typing import Any, TypeVar

from app.core.exceptions import ResourceNotFoundError
from app.database.base import Base
from app.repositories.base import BaseRepository, RepositoryFactory

ModelT = TypeVar("ModelT", bound=Base)


class BaseService[ModelT: Base]:
    """Base service that keeps application logic out of API route modules."""

    def __init__(self, repository: BaseRepository[ModelT]) -> None:
        self._repository = repository

    def get_or_raise(self, identifier: Any) -> ModelT:
        entity = self._repository.get(identifier)
        if entity is None:
            raise ResourceNotFoundError(resource=self._repository.__class__.__name__)
        return entity

    def delete(self, entity: ModelT) -> None:
        self._repository.delete(entity)


class ServiceFactory:
    """Creates services and their repositories for the active request."""

    def __init__(self, repositories: RepositoryFactory) -> None:
        self._repositories = repositories

    def for_model(self, model_type: type[ModelT]) -> BaseService[ModelT]:
        return BaseService(self._repositories.for_model(model_type))
