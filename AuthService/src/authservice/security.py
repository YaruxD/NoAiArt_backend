import asyncio
from argon2 import PasswordHasher


PwdHasher = PasswordHasher()

async def hash_password(password: str) -> str:
    return await asyncio.to_thread(PwdHasher.hash, password)

async def verify_password(plain_password: str, hashed_password:str ) -> bool:
    try:
        return await asyncio.to_thread(PwdHasher.verify, hashed_password, plain_password)
    except:
        return False