from pydantic import BaseModel

class OrderData(BaseModel):
    order: str
    order_id: int | None
    entry_price: float
    order_type: str
    order_quantity: float
    order_price: float
    limit_value: float | None
    stop_value: float | None
    status: str
    symbol: str
    date: str
    time: str
    user_id: str | None = None

class Del(BaseModel):
    order_id: int

class OrderUpdate(BaseModel):
    order_id: int
    order_type: str
    order_quantity: float
    order_price: float
    limit_value: float
    stop_value: float
