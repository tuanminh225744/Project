from typing import Generator
import os
import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import create_database, database_exists, drop_database
from httpx import AsyncClient
from httpx import ASGITransport
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URL_TEST = os.getenv("POSTGRES_URL_TEST")
if not POSTGRES_URL_TEST:
    raise RuntimeError("POSTGRES_URL_TEST is not configured in .env")

os.environ["DATABASE_URL"] = POSTGRES_URL_TEST

from app.db.base import Base, get_db
from app.main import app

# Tạo engine global
test_engine = create_engine(POSTGRES_URL_TEST)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():

    if not database_exists(POSTGRES_URL_TEST):
        create_database(POSTGRES_URL_TEST)

    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)

    test_engine.dispose()

    drop_database(POSTGRES_URL_TEST)


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