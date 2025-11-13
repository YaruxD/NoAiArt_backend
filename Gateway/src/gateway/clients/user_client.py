import logging

import httpx
from fastapi import Depends

from ..schemas import Profile, ProfileCard, ProfileComment
from ..settings import settings

logging.basicConfig(level=logging.DEBUG)


class UserServiceClient:
    def __init__(self):
        self.base_url = f"{settings.USER_SERVICE_URL}"
        self.timeout = 30.0

    async def get_profile(self, id: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/profile/{id}",
                timeout=self.timeout,
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logging.debug(f"Get profile failed: {response.text}")

            return response.json()


    async def get_profile_card(self, id: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/profile/card/{id}",
                timeout=self.timeout,
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logging.debug(f"Get profile comment failed: {response.text}")
            return response.json()


user_client = UserServiceClient()