from unittest.mock import Mock

import pytest

from app.database import session as sessions


def test_request_session_is_closed_without_hidden_commit(monkeypatch) -> None:
    session = Mock()
    monkeypatch.setattr(sessions, "get_session_factory", lambda: lambda: session)
    provider = sessions.get_db_session()
    assert next(provider) is session
    with pytest.raises(StopIteration):
        next(provider)
    session.close.assert_called_once()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_failed_request_rolls_back_closes_and_preserves_exception(monkeypatch) -> None:
    session = Mock()
    monkeypatch.setattr(sessions, "get_session_factory", lambda: lambda: session)
    provider = sessions.get_db_session()
    next(provider)
    failure = RuntimeError("synthetic transaction failure")
    with pytest.raises(RuntimeError) as caught:
        provider.throw(failure)
    assert caught.value is failure
    session.rollback.assert_called_once()
    session.close.assert_called_once()
    session.commit.assert_not_called()


def test_early_generator_close_releases_session(monkeypatch) -> None:
    session = Mock()
    monkeypatch.setattr(sessions, "get_session_factory", lambda: lambda: session)
    provider = sessions.get_db_session()
    next(provider)
    provider.close()
    session.close.assert_called_once()
