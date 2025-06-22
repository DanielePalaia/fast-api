import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fever_integration import Base
from fever_integration import app, get_db
from fever_integration import settings

DATABASE_URL = settings.DB_URL  # e.g. postgresql+asyncpg://user:pass@localhost/dbname

# Create async engine and sessionmaker once
engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


# Override FastAPI dependency
async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    # Create tables once before tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables after tests finish
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()