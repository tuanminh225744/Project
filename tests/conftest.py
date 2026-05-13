from typing import Generator

import pytest

import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from httpx import AsyncClient
from httpx import ASGITransport

from app.main import app
from app.db.base import Base, get_db
from dotenv import load_dotenv
import os

load_dotenv()


engine = create_engine(
    os.getenv("POSTGRES_URL_TEST")
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

@pytest.fixture(autouse=True)
def clear_tables():

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

def override_get_db() -> Generator:
    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


# Override dependency
app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture
async def client():

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:

        yield ac