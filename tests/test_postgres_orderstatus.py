"""Regression: both existing and freshly migrated PostgreSQL DBs accept UNKNOWN."""
import pytest
from sqlalchemy import select

from database.engine import async_session_maker, engine
from database.models import NumberOrder, OrderStatus


@pytest.mark.asyncio
async def test_postgres_unknown_status_query_after_migrations():
    if engine.dialect.name != "postgresql":
        pytest.skip("PostgreSQL enum regression")
    # The DB-typed comparison forces PostgreSQL to parse the ORM enum value even
    # when there are no rows. init_db has already migrated through the test fixture.
    async with async_session_maker() as session:
        result = await session.execute(
            select(NumberOrder.id).where(NumberOrder.status == OrderStatus.UNKNOWN)
        )
        result.all()
