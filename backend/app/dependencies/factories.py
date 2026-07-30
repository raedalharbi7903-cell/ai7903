from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db_session
from app.repositories.base import RepositoryFactory
from app.services.base import ServiceFactory

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_repository_factory(session: DatabaseSession) -> RepositoryFactory:
    return RepositoryFactory(session)


def get_service_factory(
    repositories: Annotated[RepositoryFactory, Depends(get_repository_factory)],
) -> ServiceFactory:
    return ServiceFactory(repositories)
