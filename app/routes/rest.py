import json
from app.manager import manager
from fastapi import APIRouter
from app.routes.PydanticModels import *
from app.order_book import *

router = APIRouter()

funcDict = {
    "market":market,
    "limit": add_limit_order,
    "stop-loss": add_stop_loss_order,
    "stop-limit": stop_limit,
}
@router.post("/order")
async def order(data: OrderData):
    try:
        func = funcDict[data.order_type]
        print(data)
        if data.order_type == "market":
            await func(data)

        else:
            await func(data)
            print("reached 1")
        return {"status": "ok"}
    except Exception as e:
        print("Error:", e)
        return {"status":"error"}

@router.delete("/delorder")
async def order(data: Del):
    try:
        print(data.order_id)
        return {"status": "ok", "order_id": data.order_id}
    except Exception as e:
        print("Error:", e)
        return {"status":"error"}

@router.patch("/updateorder")
async def updateorder(data: OrderUpdate):
    print(data)
    return {"status": "ok"}

