import asyncio
from project.api.core.db.db import engine, Base
from project.api.core.db.models import Organization

organizations = [
        {
            "name": "happy cat",
            "inn": "1231231231"
        },
        {
            "name": "cry banana cat",
            "inn": "4564564564"
        },
        {
            "name": "maxwell cat",
            "inn": "7897897897"
        }
    ]

keys =[
    "123",
    "456",
    "789",
    "135",
    "246",
    "357",
    "468",
    "579"
]


async def load_fixed_data(organizations, keys):
    async with engine.begin() as session:
        await session.run_sync(Base.metadata.create_all)

        for org in organizations:
            stmt = Organization.__table__.insert().values(name=org["name"], inn=org["inn"])
            await session.execute(stmt)
        #
        # for key in keys:
        #     stmt = Key.__table__.insert().values(key=key)
        #     await session.execute(stmt)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(load_fixed_data(organizations, keys))