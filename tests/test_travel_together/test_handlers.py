import pytest

from tests.conftest import generate_test_token


@pytest.mark.asyncio
async def test_create_trip__success(client_with_db, test_data):
    """Тест успешного создания поездки"""

    trip_schema = test_data["trip_schema"]
    user = test_data["user"]
    headers = {"Authorization": f"Bearer {generate_test_token(user_id=user.id)}"}
    response = await client_with_db.post(
        "/trip/create_trip", json=trip_schema.model_dump(mode="json"), headers=headers
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_retrieve_trip__success(client_with_db, test_data):
    """Тест успешного получения информации о существующей поездке"""

    trip_schema = test_data["trip_schema"]
    user = test_data["user"]
    headers = {"Authorization": f"Bearer {generate_test_token(user_id=user.id)}"}

    create_response = await client_with_db.post(
        "/trip/create_trip", json=trip_schema.model_dump(mode="json"), headers=headers
    )

    assert create_response.status_code == 201
    created_trip_data = create_response.json()
    trip_id = created_trip_data["id"]

    retrieve_response = await client_with_db.get(
        f"/trip/retrieve_trip/{trip_id}",
    )

    assert retrieve_response.status_code == 200


@pytest.mark.asyncio
async def test_update_trip__success(client_with_db, test_data):
    """Тест успешного обновления информации о существующей поездке"""

    trip_schema = test_data["trip_schema"]
    user = test_data["user"]

    headers = {"Authorization": f"Bearer {generate_test_token(user_id=user.id)}"}

    # при обновлении данных можно использовать изначальные данные
    # просто перезаписываем их
    create_response = await client_with_db.post(
        "/trip/create_trip", json=trip_schema.model_dump(mode="json"), headers=headers
    )
    assert create_response.status_code == 201
    created_trip_data = create_response.json()
    trip_id = created_trip_data["id"]

    retrieve_response = await client_with_db.put(
        f"/trip/update_trip/{trip_id}",
        json=trip_schema.model_dump(mode="json"),
        headers=headers,
    )

    assert retrieve_response.status_code == 200


@pytest.mark.asyncio
async def test_delete_trip__success(client_with_db, test_data):
    """Тест успешного удаления существующей поездки"""

    trip_schema = test_data["trip_schema"]
    user = test_data["user"]

    headers = {"Authorization": f"Bearer {generate_test_token(user_id=user.id)}"}

    create_response = await client_with_db.post(
        "/trip/create_trip", json=trip_schema.model_dump(mode="json"), headers=headers
    )
    assert create_response.status_code == 201
    created_trip_data = create_response.json()
    trip_id = created_trip_data["id"]

    retrieve_response = await client_with_db.delete(
        f"/trip/delete_trip/{trip_id}", headers=headers
    )

    assert retrieve_response.status_code == 204


@pytest.mark.asyncio
async def test_create_trip__unauth_no_token(client_with_db, test_data):
    """Тест создания поездки без токена"""

    trip_schema = test_data["trip_schema"]

    response = await client_with_db.post(
        "/trip/create_trip",
        json=trip_schema.model_dump(mode="json"),
    )

    assert response.status_code in [401, 403]
    assert response.status_code != 201


@pytest.mark.asyncio
async def test_create_trip__invalid_data(client_with_db, invalid_test_data):
    test_data = invalid_test_data["invalid_trip_schema"]

    user = invalid_test_data["user"]
    headers = {"Authorization": f"Bearer {generate_test_token(user_id=user.id)}"}
    response = await client_with_db.post(
        "trip/create_trip", json=test_data, headers=headers
    )
    assert response.status_code == 422
