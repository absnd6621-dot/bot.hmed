from decimal import Decimal
import uuid

import pytest
from sqlalchemy import select

from database.engine import async_session_maker
from database.models import NumberOrder, OrderStatus, ProviderName, User


@pytest.mark.asyncio
async def test_number_intent_status_message_persists():
    async with async_session_maker() as session:
        user = User(telegram_id=774412, username="intent", balance=Decimal("10"))
        session.add(user)
        await session.flush()
        key = f"num:{uuid.uuid4().hex}"
        order = NumberOrder(
            user_id=user.id, provider=ProviderName.HEROSMS,
            provider_order_id=f"pending:{key}", idempotency_key=key,
            service="x" * 32, country_code="y" * 32, phone_number="pending",
            price_provider_usd=Decimal("1"), price_sell_usd=Decimal("2"),
            status=OrderStatus.PENDING, status_message="نية شراء",
        )
        session.add(order)
        await session.commit()
        session.expunge_all()
        saved = (await session.execute(select(NumberOrder).where(NumberOrder.idempotency_key == key))).scalar_one()
        assert saved.status_message == "نية شراء"
        assert len(saved.provider_order_id) <= 64
        saved.status = OrderStatus.UNKNOWN
        saved.status_message = "بانتظار التسوية"
        await session.commit()
        await session.refresh(saved)
        assert saved.status_message == "بانتظار التسوية"
