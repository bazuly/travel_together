from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import TripNotFoundError
from app.travel_together import TripRepository

# # =============================================================================
# CREATE TRIP TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_create_trip__success(db_session: AsyncSession, test_data):
    """Тест успешного создания поездки"""
    trip_dict = test_data["trip_schema"].model_dump()
    trip_dict["organizer_id"] = test_data["user"].id

    repository = TripRepository(db_session)
    created_trip = await repository.create_trip(trip_dict)

    assert created_trip is not None
    assert created_trip.id is not None
    assert created_trip.title == test_data["trip_data"].title
    assert created_trip.description == test_data["trip_data"].description
    assert created_trip.destination == test_data["trip_data"].destination
    assert created_trip.organizer_id == test_data["user"].id
    assert created_trip.budget_per_person == test_data["trip_data"].budget_per_person
    assert created_trip.currency == test_data["trip_data"].currency
    assert created_trip.is_public == test_data["trip_data"].is_public
    assert created_trip.created_at is not None


@pytest.mark.asyncio
async def test_create_trip__with_minimal_data(db_session: AsyncSession, test_user):
    """Тест создания поездки с минимальными обязательными данными"""

    trip_dict = {
        "title": "Test Trip",
        "destination": "Test Destination",
        "start_date": datetime.now(),
        "end_date": datetime.now(),
        "organizer_id": test_user.id,
    }

    repository = TripRepository(db_session)
    created_trip = await repository.create_trip(trip_dict)

    assert created_trip is not None
    assert created_trip.title == "Test Trip"
    assert created_trip.description is None
    assert created_trip.budget_per_person is None
    assert created_trip.currency == "USD"
    assert created_trip.is_public is True


# =============================================================================
# RETRIEVE TRIP TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_retrieve_trip__success(db_session: AsyncSession, test_data):
    """Тест успешного получения поездки по ID"""

    trip_dict = test_data["trip_schema"].model_dump()
    trip_dict["organizer_id"] = test_data["user"].id

    repository = TripRepository(db_session)
    created_trip = await repository.create_trip(trip_dict)

    retrieved_trip = await repository.retrieve_trip(created_trip.id)

    assert retrieved_trip is not None
    assert retrieved_trip.id == created_trip.id
    assert retrieved_trip.title == created_trip.title
    assert retrieved_trip.organizer_id == created_trip.organizer_id


@pytest.mark.asyncio
async def test_retrieve_trip__not_found(db_session: AsyncSession):
    """Тест получения несуществующей поездки"""

    repository = TripRepository(db_session)
    non_existent_id = uuid4()

    # через контекстный менеджер Пайтеста вызываем ошибку
    # при попытке найти несуществующую поездку
    # ВСТАВИТЬ ГИПЕРССЫЛКУ НА СПРАВКУ ПО КОНТЕКСТНОМУ МЕНЕДЖЕРУ
    with pytest.raises(TripNotFoundError) as exc_info:
        await repository.retrieve_trip(non_existent_id)

    assert str(non_existent_id) in str(exc_info.value)


@pytest.mark.asyncio
async def test_retrieve_trip_for_update__success(db_session: AsyncSession, test_data):
    """Тест успешного получения поездки с блокировкой для обновления"""

    trip_dict = test_data["trip_schema"].model_dump()
    trip_dict["organizer_id"] = test_data["user"].id

    repository = TripRepository(db_session)
    created_trip = await repository.create_trip(trip_dict)

    retrieved_trip = await repository.retrieve_trip_for_update(created_trip.id)

    assert retrieved_trip is not None
    assert retrieved_trip.id == created_trip.id
    assert retrieved_trip.title == created_trip.title


@pytest.mark.asyncio
async def test_retrieve_trip_for_update__not_found(db_session: AsyncSession):
    """Тест получения несуществующей поездки с блокировкой"""

    repository = TripRepository(db_session)
    non_existent_id = uuid4()

    with pytest.raises(TripNotFoundError) as exc_info:
        await repository.retrieve_trip_for_update(non_existent_id)

    assert str(non_existent_id) in str(exc_info.value)


# =============================================================================
# UPDATE TRIP TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_update_trip__success(db_session: AsyncSession, test_data):
    """Тест успешного обновления поездки"""

    trip_dict = test_data["trip_schema"].model_dump()
    trip_dict["organizer_id"] = test_data["user"].id

    repository = TripRepository(db_session)
    created_trip = await repository.create_trip(trip_dict)

    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "destination": "Updated Destination",
        "budget_per_person": 5000.0,
        "currency": "EUR",
        "is_public": False,
    }

    updated_trip = await repository.update_trip(created_trip.id, update_data)

    assert updated_trip is not None
    assert updated_trip.id == created_trip.id
    assert updated_trip.title == "Updated Title"
    assert updated_trip.description == "Updated Description"
    assert updated_trip.destination == "Updated Destination"
    assert updated_trip.budget_per_person == 5000.0
    assert updated_trip.currency == "EUR"
    assert updated_trip.is_public is False
    # проверка, что organizer_id остается прежним
    assert updated_trip.organizer_id == created_trip.organizer_id


@pytest.mark.asyncio
async def test_update_trip__partial_update(db_session: AsyncSession, test_data):
    """Тест частичного обновления поездки (только некоторые поля)"""

    trip_dict = test_data["trip_schema"].model_dump()
    trip_dict["organizer_id"] = test_data["user"].id

    repository = TripRepository(db_session)
    created_trip = await repository.create_trip(trip_dict)

    update_data = {"title": "Only Title Updated"}

    updated_trip = await repository.update_trip(created_trip.id, update_data)

    assert updated_trip.title == "Only Title Updated"
    assert updated_trip.description == created_trip.description
    assert updated_trip.destination == created_trip.destination


@pytest.mark.asyncio
async def test_update_trip__not_found(db_session: AsyncSession):
    """Тест обновления несуществующей поездки"""

    repository = TripRepository(db_session)
    non_existent_id = uuid4()
    update_data = {"title": "Updated Title"}

    with pytest.raises(TripNotFoundError) as exc_info:
        await repository.update_trip(non_existent_id, update_data)

    assert str(non_existent_id) in str(exc_info.value)


# =============================================================================
# DELETE TRIP TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_delete_trip__success(db_session: AsyncSession, test_data):
    """Тест успешного удаления поездки"""

    trip_dict = test_data["trip_schema"].model_dump()
    trip_dict["organizer_id"] = test_data["user"].id

    repository = TripRepository(db_session)
    created_trip = await repository.create_trip(trip_dict)

    result = await repository.delete_trip(created_trip.id)

    assert result is True

    with pytest.raises(TripNotFoundError):
        await repository.retrieve_trip(created_trip.id)


@pytest.mark.asyncio
async def test_delete_trip__not_found(db_session: AsyncSession):
    """Тест удаления несуществующей поездки"""

    repository = TripRepository(db_session)
    non_existent_id = uuid4()

    with pytest.raises(TripNotFoundError) as exc_info:
        await repository.delete_trip(non_existent_id)

    assert str(non_existent_id) in str(exc_info.value)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_create_retrieve_update_delete_flow(db_session: AsyncSession, test_data):
    """Интеграционный тест: создание -> получение -> обновление -> удаление"""

    repository = TripRepository(db_session)
    trip_dict = test_data["trip_schema"].model_dump()
    trip_dict["organizer_id"] = test_data["user"].id

    # 1. Создание
    created_trip = await repository.create_trip(trip_dict)
    assert created_trip is not None
    trip_id = created_trip.id

    # 2. Получение
    retrieved_trip = await repository.retrieve_trip(trip_id)
    assert retrieved_trip.id == trip_id

    # 3. Обновление
    update_data = {"title": "Updated in Flow"}
    updated_trip = await repository.update_trip(trip_id, update_data)
    assert updated_trip.title == "Updated in Flow"

    # 4. Удаление
    delete_result = await repository.delete_trip(trip_id)
    assert delete_result is True

    # 5. Проверка, что удалено
    with pytest.raises(TripNotFoundError):
        await repository.retrieve_trip(trip_id)
