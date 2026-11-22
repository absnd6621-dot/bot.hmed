import pytest
from sqlalchemy import select

from database.engine import async_session_maker
from database.models import Country
from services.herosms_sync_service import sync_herosms_countries


class FakeProvider:
    async def get_countries(self):
        return [
            {"id": "125", "eng": "Central African Republic"},
            {"id": "126", "eng": "Conflict"},
            {"id": "127", "eng": "Long Country Name That Also Exceeds Limit"},
        ]

    async def get_country_prices(self, cid):
        return {"wa": {"cost": 1, "count": 2}}


@pytest.mark.asyncio
async def test_long_codes_and_failed_row_do_not_poison_batch():
    async with async_session_maker() as session:
        session.add(Country(code="herosms_conflict_126", name_ar="existing", is_active=True))
        await session.commit()
        report = await sync_herosms_countries(session, ["whatsapp"], provider=FakeProvider())
        rows = (await session.execute(select(Country).where(Country.herosms_code.in_(["125", "127"])))).scalars().all()
        assert {c.herosms_code for c in rows} == {"125", "127"}
        assert all(len(c.code) <= 32 for c in rows)
        assert len(report.added) == 2
        assert report.failed == 1
        # Repeating the sync finds rows via provider ID, rather than duplicating them.
        again = await sync_herosms_countries(session, ["whatsapp"], provider=FakeProvider())
        assert len(again.added) == 0
        assert again.failed == 1
