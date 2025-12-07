import os
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from jose import jwt
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


from app.main import app
from app.config import get_settings
from app.infra.database import Base, get_db_session
from app.travel_together.service import TripService
from app.travel_together.schemas import TripCreate
from tests.factory import TripFactory, UserFactory

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
)


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL)

    connection = await engine.connect()
    transaction = await connection.begin()

    session_maker = sessionmaker(
        bind=connection, class_=AsyncSession, expire_on_commit=False
    )
    session = session_maker()

    try:
        await connection.run_sync(Base.metadata.create_all)
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()
        await engine.dispose()


@pytest_asyncio.fixture
async def async_client():
    from httpx import AsyncClient
    from app.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        app.dependency_overrides = {}
        yield client
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    """ Переопределяем наши сеттинги на тестовые """

    monkeypatch.setenv("DB_DRIVER", "postgresql+asyncpg")
    monkeypatch.setenv("DB_HOST", "db-test")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "testuser")
    monkeypatch.setenv("DB_PASSWORD", "testpass")
    monkeypatch.setenv("DB_NAME", "testdb")
    monkeypatch.setenv("POSTGRES_PASSWORD", "testpass")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

    from app.config import get_settings

    settings = get_settings()
    # model_rebuild() принудительно перестраивает модель
    # с учетом всех текущих значений переменных окружения,
    # включая те, что были изменены через monkeypatch.
    settings.model_rebuild()


# мы конечно нарушаем DRY
# но для тестов проще переопределить метод прямо в тесте
def generate_test_token(user_id: uuid.UUID) -> str:
    """Helper функция для генерации тестового токена"""

    settings = get_settings()
    expires_data_unix = (datetime.now(timezone.utc) +
                         timedelta(days=1)).timestamp()
    if isinstance(user_id, uuid.UUID):
        user_id = user_id.hex
    token = jwt.encode(
        {"user_id": user_id, "exp": expires_data_unix},
        settings.JWT_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return token


# создаем фикстуру для наших фабрик
@pytest.fixture(autouse=True)
def setup_factories(db_session: AsyncSession):
    TripFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session


@pytest_asyncio.fixture
async def test_user():
    """ Фикстура с тестовым пользователем """

    user = await UserFactory.create()
    return user


@pytest_asyncio.fixture
async def test_data(test_user):
    """ Фикстура с тестовыми данными """

    # """Build an instance of the associated class, with overridden attrs.
    # проваливаемся в build и смотрим, что метод build принимает *kwargs,
    # соответственно можем сразу перезаписать organizer_id
    trip_data = TripFactory.build(organizer_id=test_user.id)

    trip_schema = TripCreate(
        id=trip_data.id,
        title=trip_data.title,
        description=trip_data.description,
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        budget_per_person=trip_data.budget_per_person,
        currency=trip_data.currency,
        is_public=trip_data.is_public,
    )

    return {
        "user": test_user,
        "trip_data": trip_data,
        "trip_schema": trip_schema,
    }


@pytest_asyncio.fixture
async def invalid_test_data(test_user):
    """Фикстура с невалидными тестовыми данными"""
    trip_data = TripFactory.build(organizer_id=test_user.id)

    # Создаем невалидные данные как словарь, а не Pydantic объект
    # Pydantic валидирует при создании, поэтому нужно передавать сырые данные
    invalid_trip_data = {
        "title": 123,  # Невалидный тип (должен быть str)
        "description": trip_data.description,
        "destination": trip_data.destination,
        "start_date": trip_data.start_date.isoformat(),
        "end_date": trip_data.end_date.isoformat(),
        "budget_per_person": trip_data.budget_per_person,
        "currency": trip_data.currency,
        "is_public": trip_data.is_public,
    }

    return {
        "user": test_user,
        "invalid_trip_schema": invalid_trip_data,
    }


@pytest_asyncio.fixture
async def client_with_db(db_session):
    """Фикстура для клиента с переопределенной БД сессией"""

    async def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://tests") as client:
        yield client

    # Очищаем переопределения
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def mock_trip_repo():
    """Мок для TripRepository"""

    return AsyncMock()


@pytest_asyncio.fixture
async def mock_participant_repo():
    """Мок для ParticipantRepository"""

    return AsyncMock()


@pytest_asyncio.fixture
async def mock_permission_service():
    """Мок для PermissionService"""

    return AsyncMock()


@pytest_asyncio.fixture
async def trip_service(mock_trip_repo, mock_participant_repo, mock_permission_service):
    """Фикстура для создания TripService с моками"""

    return TripService(
        trip_repo=mock_trip_repo,
        participant_repo=mock_participant_repo,
        permission_service=mock_permission_service,
    )
