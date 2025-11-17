from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class CommentPin(BaseModel):
    user_id: int
    pin_id: int
    text: str
    likes: int
    reply_to: int
    views: int
    created_at: Optional[str] = None
    amount_of_replies: Optional[str] = None

    class Config:
        from_attributes = True