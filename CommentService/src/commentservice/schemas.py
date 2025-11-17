from pydantic import BaseModel, EmailStr, Data
from datetime import date

class CommentPin(BaseModel):
    user_id: int
    pin_id: int
    text: str
    likes: int
    reply_to: int
    views: int
    created_at: date
    amount_of_replies = int

    class Config:
        from_attributes = True