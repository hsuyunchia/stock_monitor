from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str # MVP 簡化，直接存明碼或簡單 Hash，正式版請用 bcrypt

class StockMeta(SQLModel, table=True):
    symbol: str = Field(primary_key=True)
    name: str
    currency: str

class Watchlist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    symbol: str = Field(index=True)
    target_price: float
    condition: str  # "gte" or "lte"
    is_active: bool = Field(default=True)

class UserSchedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    check_time: str # "09:15"
    frequency: str = Field(default="weekday") # "weekday", "weekend", "everyday"