from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.exceptions import TripNotFoundError, TripOrganizerRequiredError
from app.travel_together.models import Trip
from app.travel_together.schemas import TripResponse

# =============================================================================
# CREATE TRIP TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_create_trip__success(trip_service, mock_trip_repo, test_data):
    """Тест успешного создания поездки через сервис"""

    user = test_data["user"]
    trip_schema = test_data["trip_schema"]

    mock_trip = MagicMock(spec=Trip)
    mock_trip.id = uuid4()
    mock_trip.title = trip_schema.title
    mock_trip.description = trip_schema.description
    mock_trip.destination = trip_schema.destination
    mock_trip.organizer_id = user.id
    mock_trip.budget_per_person = trip_schema.budget_per_person
    mock_trip.currency = trip_schema.currency
    mock_trip.is_public = trip_schema.is_public

    mock_trip_repo.create_trip.return_value = mock_trip

    result = await trip_service.create_trip(trip_schema, user.id)

    assert isinstance(result, TripResponse)
    assert result.title == trip_schema.title
    assert result.organizer_id == user.id

    mock_trip_repo.create_trip.assert_called_once()
    call_args = mock_trip_repo.create_trip.call_args[0][0]
    assert call_args["organizer_id"] == user.id
    assert call_args["title"] == trip_schema.title


# =============================================================================
# RETRIEVE TRIP TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_retrieve_trip__success(
    trip_service, mock_trip_repo, test_data, mock_trip_cache
):
    """Тест успешного получения поездки через сервис"""
    trip_id = uuid4()
    user = test_data["user"]

    mock_trip = MagicMock(spec=Trip)
    mock_trip.id = trip_id
    mock_trip.title = "Test Trip"
    mock_trip.description = "Test Description"
    mock_trip.destination = "Test Destination"
    mock_trip.organizer_id = user.id
    mock_trip.start_date = test_data["trip_schema"].start_date
    mock_trip.end_date = test_data["trip_schema"].end_date
    mock_trip.budget_per_person = None
    mock_trip.currency = "USD"
    mock_trip.is_public = True
    mock_trip.created_at = test_data["trip_schema"].start_date

    mock_trip_cache.get_trip_from_cache.return_value = None
    mock_trip_repo.retrieve_trip.return_value = mock_trip

    result = await trip_service.retrieve_trip(trip_id)

    assert isinstance(result, TripResponse)
    assert result.id == trip_id
    assert result.title == "Test Trip"

    mock_trip_repo.retrieve_trip.assert_called_once_with(trip_id)
    mock_trip_cache.get_trip_from_cache.assert_called_once_with(trip_id)
    mock_trip_cache.set_trip_cache.assert_called_once()


@pytest.mark.asyncio
async def test_retrieve_trip__not_found(trip_service, mock_trip_repo, mock_trip_cache):
    """Тест получения несуществующей поездки через сервис"""
    trip_id = uuid4()

    mock_trip_cache.get_trip_from_cache.return_value = None
    mock_trip_repo.retrieve_trip.side_effect = TripNotFoundError(trip_id)

    with pytest.raises(TripNotFoundError) as exc_info:
        await trip_service.retrieve_trip(trip_id)

    assert str(trip_id) in str(exc_info.value)
    mock_trip_cache.get_trip_from_cache.assert_called_once_with(trip_id)
    mock_trip_repo.retrieve_trip.assert_called_once_with(trip_id)
    mock_trip_cache.set_trip_cache.assert_not_called()


# =============================================================================
# UPDATE TRIP TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_update_trip__success(
    trip_service, mock_trip_repo, mock_permission_service, test_data
):
    """Тест успешного обновления поездки организатором"""

    user = test_data["user"]
    trip_id = uuid4()
    trip_schema = test_data["trip_schema"]

    existing_trip = MagicMock(spec=Trip)
    existing_trip.id = trip_id
    existing_trip.organizer_id = user.id
    existing_trip.title = "Old Title"
    existing_trip.destination = "Old Destination"
    existing_trip.start_date = trip_schema.start_date
    existing_trip.end_date = trip_schema.end_date
    existing_trip.budget_per_person = None
    existing_trip.currency = "USD"
    existing_trip.is_public = True
    existing_trip.created_at = trip_schema.start_date

    updated_trip = MagicMock(spec=Trip)
    updated_trip.id = trip_id
    updated_trip.organizer_id = user.id
    updated_trip.title = trip_schema.title
    updated_trip.description = trip_schema.description
    updated_trip.destination = trip_schema.destination
    updated_trip.start_date = trip_schema.start_date
    updated_trip.end_date = trip_schema.end_date
    updated_trip.budget_per_person = trip_schema.budget_per_person
    updated_trip.currency = trip_schema.currency
    updated_trip.is_public = trip_schema.is_public
    updated_trip.created_at = trip_schema.start_date

    mock_trip_repo.retrieve_trip.return_value = existing_trip
    mock_permission_service.check_is_user_trip_organizer.return_value = True
    mock_trip_repo.update_trip.return_value = updated_trip

    result = await trip_service.update_trip(trip_id, trip_schema, user.id)

    assert isinstance(result, TripResponse)
    assert result.id == trip_id
    assert result.title == trip_schema.title

    mock_trip_repo.retrieve_trip.assert_called_once_with(trip_id)
    mock_permission_service.check_is_user_trip_organizer.assert_called_once_with(
        user.id, trip_id
    )
    mock_trip_repo.update_trip.assert_called_once()

    # Проверяем, что organizer_id не изменился
    update_call_args = mock_trip_repo.update_trip.call_args[0][1]
    assert update_call_args["organizer_id"] == user.id


@pytest.mark.asyncio
async def test_update_trip__not_organizer(
    trip_service, mock_trip_repo, mock_permission_service, test_data
):
    """Тест обновления поездки не организатором"""

    user = test_data["user"]
    other_user_id = uuid4()
    trip_id = uuid4()
    trip_schema = test_data["trip_schema"]

    existing_trip = MagicMock(spec=Trip)
    existing_trip.id = trip_id
    existing_trip.organizer_id = user.id

    mock_trip_repo.retrieve_trip.return_value = existing_trip
    mock_permission_service.check_is_user_trip_organizer.return_value = False

    with pytest.raises(TripOrganizerRequiredError) as exc_info:
        await trip_service.update_trip(trip_id, trip_schema, other_user_id)

    assert "Only the organizer can update this trip" in str(exc_info.value)

    # Проверяем, что update_trip не был вызван
    mock_trip_repo.update_trip.assert_not_called()
    mock_trip_repo.retrieve_trip.assert_called_once_with(trip_id)
    mock_permission_service.check_is_user_trip_organizer.assert_called_once_with(
        other_user_id, trip_id
    )


@pytest.mark.asyncio
async def test_update_trip__trip_not_found(
    trip_service,
    mock_trip_repo,
    mock_permission_service,
    test_data,
):
    """Тест обновления несуществующей поездки"""

    user = test_data["user"]
    trip_id = uuid4()
    trip_schema = test_data["trip_schema"]

    mock_trip_repo.retrieve_trip.side_effect = TripNotFoundError(trip_id)

    with pytest.raises(TripNotFoundError):
        await trip_service.update_trip(trip_id, trip_schema, user.id)

    mock_permission_service.check_is_user_trip_organizer.assert_not_called()
    mock_trip_repo.update_trip.assert_not_called()


# =============================================================================
# DELETE TRIP TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_delete_trip__success(
    trip_service, mock_trip_repo, mock_permission_service, test_data
):
    """Тест успешного удаления поездки организатором"""
    user = test_data["user"]
    trip_id = uuid4()

    # Настраиваем моки
    mock_permission_service.check_is_user_trip_organizer.return_value = True
    mock_trip_repo.delete_trip.return_value = True

    # Вызываем метод сервиса
    result = await trip_service.delete_trip(trip_id, user.id)

    # Проверяем результаты (метод возвращает None)
    assert result is None

    # Проверяем, что методы были вызваны правильно
    mock_permission_service.check_is_user_trip_organizer.assert_called_once_with(
        user.id, trip_id
    )
    mock_trip_repo.delete_trip.assert_called_once_with(trip_id)


@pytest.mark.asyncio
async def test_delete_trip__not_organizer(
    trip_service, mock_trip_repo, mock_permission_service, test_data
):
    """Тест удаления поездки неорганизатором"""

    other_user_id = uuid4()
    trip_id = uuid4()

    mock_permission_service.check_is_user_trip_organizer.return_value = False

    with pytest.raises(TripOrganizerRequiredError) as exc_info:
        await trip_service.delete_trip(trip_id, other_user_id)

    assert "Only the organizer can delete this trip" in str(exc_info.value)

    mock_trip_repo.delete_trip.assert_not_called()
    mock_permission_service.check_is_user_trip_organizer.assert_called_once_with(
        other_user_id, trip_id
    )


@pytest.mark.asyncio
async def test_delete_trip__trip_not_found(
    trip_service, mock_trip_repo, mock_permission_service, test_data
):
    """Тест удаления несуществующей поездки"""

    user = test_data["user"]
    trip_id = uuid4()

    mock_permission_service.check_is_user_trip_organizer.return_value = True
    mock_trip_repo.delete_trip.side_effect = TripNotFoundError(trip_id)

    with pytest.raises(TripNotFoundError):
        await trip_service.delete_trip(trip_id, user.id)

    mock_permission_service.check_is_user_trip_organizer.assert_called_once_with(
        user.id, trip_id
    )
    mock_trip_repo.delete_trip.assert_called_once_with(trip_id)


# =============================================================================
# INTEGRATION TESTS (с реальными зависимостями, но изолированными)
# =============================================================================


@pytest.mark.asyncio
async def test_create_retrieve_update_delete_flow(
    trip_service, mock_trip_repo, mock_permission_service, test_data, mock_trip_cache
):
    """Интеграционный тест: создание -> получение -> обновление -> удаление"""

    user = test_data["user"]
    trip_schema = test_data["trip_schema"]
    trip_id = uuid4()

    # 1. Создание - создаем мок со всеми полями
    mock_created_trip = MagicMock(spec=Trip)
    mock_created_trip.id = trip_id
    mock_created_trip.title = trip_schema.title
    mock_created_trip.description = trip_schema.description
    mock_created_trip.destination = trip_schema.destination
    mock_created_trip.start_date = trip_schema.start_date
    mock_created_trip.end_date = trip_schema.end_date
    mock_created_trip.budget_per_person = trip_schema.budget_per_person
    mock_created_trip.currency = trip_schema.currency
    mock_created_trip.is_public = trip_schema.is_public
    mock_created_trip.organizer_id = user.id
    mock_created_trip.created_at = trip_schema.start_date
    mock_trip_repo.create_trip.return_value = mock_created_trip

    created_result = await trip_service.create_trip(trip_schema, user.id)
    assert created_result.id == trip_id

    # 2. Получение
    mock_trip_cache.get_trip_from_cache.return_value = None
    mock_trip_repo.retrieve_trip.return_value = mock_created_trip
    retrieved_result = await trip_service.retrieve_trip(trip_id)
    assert retrieved_result.id == trip_id

    # 3. Обновление
    mock_permission_service.check_is_user_trip_organizer.return_value = True
    updated_trip = MagicMock(spec=Trip)
    updated_trip.id = trip_id
    updated_trip.title = "Updated Title"
    updated_trip.description = trip_schema.description
    updated_trip.destination = trip_schema.destination
    updated_trip.start_date = trip_schema.start_date
    updated_trip.end_date = trip_schema.end_date
    updated_trip.budget_per_person = trip_schema.budget_per_person
    updated_trip.currency = trip_schema.currency
    updated_trip.is_public = trip_schema.is_public
    updated_trip.organizer_id = user.id
    updated_trip.created_at = trip_schema.start_date
    mock_trip_repo.update_trip.return_value = updated_trip

    update_result = await trip_service.update_trip(trip_id, trip_schema, user.id)
    assert update_result.id == trip_id

    # 4. Удаление
    mock_trip_repo.delete_trip.return_value = True
    delete_result = await trip_service.delete_trip(trip_id, user.id)
    assert delete_result is None
