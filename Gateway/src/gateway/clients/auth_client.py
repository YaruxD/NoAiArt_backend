import httpx
from ..schemas import RegistrationScheme, UserRead, TokenScheme
from ..settings import settings
import logging
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends


logging.basicConfig(level=logging.DEBUG)


class AuthServiceClient:
    def __init__(self):
        self.base_url = f"{settings.AUTH_SERVICE_URL}"
        self.timeout = 30.0

    async def register(self, user_data: RegistrationScheme) -> UserRead:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/register/",
                json=user_data.model_dump(),
                timeout=self.timeout,
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logging.debug(f"Register failed: {response.text}")
                raise e
            return UserRead(**response.json())

    async def login(self, user_data: OAuth2PasswordRequestForm = Depends()) -> TokenScheme:
        async with httpx.AsyncClient() as client:
            data = {
            "username": user_data.username,
            "password": user_data.password,
            "grant_type": "password", 
            "scope": user_data.scopes or ""
        }
        
            response = await client.post(
            f"{self.base_url}/login/",
            data=data,
            timeout=self.timeout,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logging.debug(f"Login failed: {response.text}")
            raise e
        return TokenScheme(**response.json())



    async def refresh_token(self, refresh_token: str) -> TokenScheme:
        async with httpx.AsyncClient() as client:
            cookies = {"refresh_token": refresh_token}
            response = await client.post(
                f"{self.base_url}/token/refresh/",
                cookies=cookies,
                timeout=self.timeout,
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logging.debug(f"Refresh token failed: {response.text}")
                raise e
            return TokenScheme(**response.json())


auth_client = AuthServiceClient()
