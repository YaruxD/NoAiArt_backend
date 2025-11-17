import logging

import httpx
from fastapi import Depends

from ..settings import settings

logging.basicConfig(level=logging.DEBUG)


class CommentServiceClient():
    def __init__(self):
            self.base_url = settings.COMMENT_SERVICE_URL
            self.timeout = 30.0
    async def get_comments(
        self,
        pin_id: int,
        limit: int,
        offset: int
        ):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/get_comments/{pin_id}",
                params={"limit": limit, "offset": offset},
                timeout=self.timeout,
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logging.debug(f"Get comments failed: {response.text}")

            return response.json()
comment_client = CommentServiceClient()