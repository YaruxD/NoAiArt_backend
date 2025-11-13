from pydantic import BaseModel, Field


class PinCreate(BaseModel):
    title: str = Field(max_length=200)
    description: str = Field(max_length=500)
