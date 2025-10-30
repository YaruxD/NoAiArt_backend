from pydantic import BaseModel, Field, EmailStr

class RegistrationScheme(BaseModel):

    username: str = Field(max_length=40, min_length=4)
    name: str = Field(max_length=40, min_length=3)
    password: str = Field(min_length=8, max_length=40)
    email: EmailStr

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class TokenScheme(BaseModel):
    access_token: str
    token_type: str

class CurrentUser(BaseModel):
    id: int
    username: str