from typing import Optional, Literal
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr
class UserBase(BaseModel):
    email: EmailStr
    role: Literal['student', 'instructor', 'admin'] = 'student'

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[UUID] = None

class PortfolioBase(BaseModel):
    user_id: UUID
    balance: float = Field(default=10000.00, ge=0)
    total_value: Optional[float] = None

class PortfolioInDB(PortfolioBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TradeBase(BaseModel):
    portfolio_id: UUID
    symbol: str = Field(min_length=1, max_length=10)
    quantity: int = Field(gt=0)
    price: float = Field(ge=0)
    side: Literal['BUY', 'SELL']

class TradeInDB(TradeBase):
    id: UUID
    executed_at: datetime

    class Config:
        from_attributes = True

class MarketEventBase(BaseModel):
    event_type: str
    description: Optional[str] = None
    impact: Optional[dict] = None # e.g., {'AAPL': {'price_change': 0.05}}
    event_date: datetime

class MarketEventInDB(MarketEventBase):
    id: UUID

    class Config:
        from_attributes = True

class ChatbotInteractionBase(BaseModel):
    user_id: UUID
    query: str
    response: str
    feedback: Optional[int] = Field(None, ge=1, le=5)

class ChatbotInteractionInDB(ChatbotInteractionBase):
    id: UUID
    interaction_at: datetime

    class Config:
        from_attributes = True

class WebinarBase(BaseModel):
    instructor_id: UUID
    topic: str
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = Field(default=60, gt=0)
    recording_url: Optional[str] = None

class WebinarInDB(WebinarBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
