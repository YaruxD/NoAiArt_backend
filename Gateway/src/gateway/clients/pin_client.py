import logging

import httpx
from fastapi import Depends

from ..settings import settings

logging.basicConfig(level=logging.DEBUG)


class PinServiceClient():
    def __init__(self):
            self.base_url = settings.PIN_SERVICE_URL
            self.timeout = 30.0
    async def get_list_of_pins(
        self,
        pin_ids: list[int]
        ):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/list_pins",
                json={"ids": pin_ids},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
pin_client = PinServiceClient()