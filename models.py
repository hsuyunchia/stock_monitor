from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    
    # 💡 新增：用來存放加密後的密碼，絕對不能存明碼！
    hashed_password: str 
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

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