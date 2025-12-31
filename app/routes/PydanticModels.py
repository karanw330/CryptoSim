from pydantic import BaseModel

class OrderData(BaseModel):
    order: str
    order_id: int | None
    entry_price: float
    order_type: str
    order_quantity: int
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
    order_type: str
    order_quantity: str
    order_price: str
    order_limit: str
    order_stop: str
