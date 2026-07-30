from sqlalchemy import String, create_engine
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin
from app.repositories.base import RepositoryFactory
from app.services.base import ServiceFactory


class TestRecord(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "test_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


def _session() -> Session:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_repository_persists_and_reads_an_entity() -> None:
    session = _session()
    repository = RepositoryFactory(session).for_model(TestRecord)
    record = repository.add(TestRecord(name="foundation"))
    session.commit()

    assert repository.get(record.id) is record
    assert repository.list() == [record]
    assert record.created_at is not None
    assert record.updated_at is not None


def test_service_deletes_soft_deletable_entities_without_hard_delete() -> None:
    session = _session()
    repositories = RepositoryFactory(session)
    service = ServiceFactory(repositories).for_model(TestRecord)
    record = repositories.for_model(TestRecord).add(TestRecord(name="foundation"))
    session.commit()

    service.delete(record)
    session.commit()

    assert record.is_deleted is True
    assert repositories.for_model(TestRecord).get(record.id) is record
