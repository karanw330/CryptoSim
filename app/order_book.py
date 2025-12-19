import heapq
from heapq import heappush, heappop
import datetime
import pytz
import json
from app.manager import manager
################################################ functions for order validation #######################################################
async def market(details):
    print(details.dict())
    details = details.dict()
    details["status"] = "active"
    await manager.broadcast(json.dumps({"data_type":"new_order","data":details}))

from collections import defaultdict
from typing import Dict, List, Tuple, Any



# =========================
#   HEAPS
# =========================

# For normal limit and stop-limit (in your sim)
limit_heaps: Dict[str, List[Tuple[float, int, Any]]] = defaultdict(list)

# For stop-loss
stop_loss_heaps: Dict[str, List[Tuple[float, int, Any]]] = defaultdict(list)


# =========================
#   ADD ORDER HELPERS
# =========================

async def add_limit_order(order):
    """
    Call this when a new limit (or stop-limit in your sim) order is created.
    """
    print("reached 2")
    symbol = order.symbol
    limit_price = order.limit_value
    # order_id = order.id
    order_id = 2
    heap = limit_heaps[symbol]
    heapq.heappush(heap, (limit_price, order_id, order))
    order = order.dict()
    order["status"] = "inactive"
    await manager.broadcast(json.dumps({"data_type": "new_order", "data": order}))
    print("reached 3")


async def add_stop_loss_order(order):
    """
    Call this when a new stop-loss order is created.
    """
    symbol = order.symbol
    stop_price = order.stop_value
    # order_id = order.id
    order_id = 1

    heap = stop_loss_heaps[symbol]
    heapq.heappush(heap, (stop_price, order_id, order))
    order = order.dict()
    order["status"] = "inactive"
    await manager.broadcast(json.dumps({"data_type": "new_order", "data": order}))


# =========================
#   MATCHING FUNCTIONS
# =========================

async def limit(heap, security: str, last_price: float):
    """
    Process limit orders for a given security at the latest traded price.

    heap: list[(limit_price, order_id, order_obj)]
    """
    triggered_orders = []

    while heap:
        # Peek at best order in this symbol's heap
        limit_price, order_id, order = heap[0]

        # Only process orders for this symbol
        if order.symbol != security:
            break

        # BUY limit: execute when market price <= limit price
        if order.buy_sell == "Buy" and last_price <= limit_price:
            heapq.heappop(heap)

            order.status = "active"
            order.save()
            triggered_orders.append(order)

            await manager.broadcast({
                "data_type": "limit_triggered",
                "side": "Buy",
                "security": order.symbol,
                "order_id": order_id,
                "limit_price": float(limit_price),
                "last_price": float(last_price),
                "status": order.status,
            })

        # SELL limit: execute when market price >= limit price
        elif order.buy_sell == "Sell" and last_price >= limit_price:
            heapq.heappop(heap)

            order.status = "active"
            order.save()
            triggered_orders.append(order)

            await manager.broadcast({
                "data_type": "limit_triggered",
                "side": "Sell",
                "security": order.symbol,
                "order_id": order_id,
                "limit_price": float(limit_price),
                "last_price": float(last_price),
                "status": order.status,
            })

        else:
            # top order cannot be filled at this price → stop
            break

    return triggered_orders


async def stop_loss(heap, security: str, last_price: float):
    """
    Process stop-loss orders for a given security using the latest price.

    heap: list[(stop_price, order_id, order_obj)]
    """
    triggered_orders = []

    while heap:
        stop_price, order_id, order = heap[0]  # peek

        if order.symbol != security:
            break

        # BUY stop (stop-buy): triggers when price goes UP to or above stop
        if order.buy_sell == "Buy" and last_price >= stop_price:
            heapq.heappop(heap)

            order.status = "active"
            order.save()
            triggered_orders.append(order)

            await manager.broadcast({
                "data_type": "stop_loss_triggered",
                "side": "Buy",
                "security": order.symbol,
                "order_id": order_id,
                "stop_price": float(stop_price),
                "last_price": float(last_price),
                "status": order.status,
            })

        # SELL stop (classic stop-loss): triggers when price goes DOWN to or below stop
        elif order.buy_sell == "Sell" and last_price <= stop_price:
            heapq.heappop(heap)

            order.status = "active"
            order.save()
            triggered_orders.append(order)

            await manager.broadcast({
                "data_type": "stop_loss_triggered",
                "side": "Sell",
                "security": order.symbol,
                "order_id": order_id,
                "stop_price": float(stop_price),
                "last_price": float(last_price),
                "status": order.status,
            })

        else:
            break

    return triggered_orders


# =========================
#   PRICE TICK DISPATCHER
# =========================

async def price_tick(security: str, last_price: float):
    """
    Call this every time you receive a new price for `security`.

    It will:
      - process limit & stop-limit orders using `limit()`
      - process stop-loss orders using `stop_loss()`
    """
    await limit(limit_heaps[security], security, last_price)
    await stop_loss(stop_loss_heaps[security], security, last_price)


# =========================
#   API-FACING HELPERS
# =========================

# For your simulation: stop-limit behaves same as limit -> just add to limit heap
async def stop_limit(order):
    await add_limit_order(order)
