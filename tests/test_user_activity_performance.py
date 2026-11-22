from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from database.engine import async_session_maker
from database.models import User
from middlewares.user_middleware import UserMiddleware


@pytest.mark.asyncio
async def test_repeated_navigation_does_not_commit_every_time():
    async with async_session_maker() as session:
        user = User(telegram_id=719001, username="test", full_name="Test",
                    language_code="ar", last_activity_at=datetime.utcnow() - timedelta(minutes=2))
        session.add(user)
        await session.commit()
        commit = AsyncMock(wraps=session.commit)
        session.commit = commit
        tg_user = SimpleNamespace(id=719001, username="test", full_name="Test", language_code="ar")
        async def handler(event, data):
            return data["db_user"].telegram_id
        middleware = UserMiddleware()
        assert await middleware(handler, object(), {"session": session, "event_from_user": tg_user}) == 719001
        assert await middleware(handler, object(), {"session": session, "event_from_user": tg_user}) == 719001
        assert commit.await_count == 1
        tg_user.username = "changed"
        await middleware(handler, object(), {"session": session, "event_from_user": tg_user})
        assert commit.await_count == 2
        await session.refresh(user)
        assert user.username == "changed"
        assert datetime.utcnow() - user.last_activity_at < timedelta(minutes=1)
