from dataclasses import dataclass

import httpx

from schemas import YandexUserData
from config import Settings


@dataclass
class YandexClient:
    settings: Settings
    async_client: httpx.AsyncClient

    async def get_user_info(self, code: str) -> YandexUserData:
        access_token = await self._get_user_access_token(code=code)
        response = await self.async_client.get(
            "https://login.yandex.ru/info?format=json",
            headers={"Authorization": f"OAuth {access_token}"},
        )

        data = response.json()
        if "error" in data:
            raise ValueError(
                f"Error fetching user info: {
                data['error']} - {data.get('error_description')}"
            )
        return YandexUserData(**data, access_token=access_token)

    async def _get_user_access_token(self, code: str) -> str:
        response = await self.async_client.post(
            self.settings.YANDEX_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.settings.YANDEX_CLIENT_ID,
                "client_secret": self.settings.YANDEX_SECRET_KEY,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        return response.json()["access_token"]
