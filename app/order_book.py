import heapq
from heapq import heappush, heappop
import json
from app.manager import manager
from app.db_init import get_db_connection
from app.routes.PydanticModels import OrderData

# =========================
#   DB HELPERS
# =========================

async def execute_trade_db(order_id, symbol, price, quantity, side, user_id, entry):
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Record Trade
    c.execute('''
        INSERT INTO trades (symbol, price, quantity, timestamp, entry)
        VALUES (?, ?, ?, datetime('now'), ?)
    ''', (symbol, price, quantity, entry))
    
    # 2. Update Order Status
    c.execute('UPDATE orders SET status = ?, price = ? WHERE order_id = ?', 
              ('completed', price, order_id))
    
    # 3. Settlement
    if side == "Buy":
        # Buyer gets Coin (USD already deducted on order placement)
        
        # Check if portfolio entry exists
        port = c.execute('SELECT amount FROM portfolio WHERE user_id = ? AND symbol = ?', 
                         (user_id, symbol)).fetchone()
        if port:
            c.execute('UPDATE portfolio SET amount = amount + ? WHERE user_id = ? AND symbol = ?', 
                      (quantity, user_id, symbol))
        else:
            c.execute('INSERT INTO portfolio (user_id, symbol, amount) VALUES (?, ?, ?)',
                      (user_id, symbol, quantity))
            
    elif side == "Sell":
        # Seller gets USD (Coin already deducted on order placement)
        c.execute('UPDATE users SET balance_usd = balance_usd + ? WHERE username = ?', 
                  (quantity * price, user_id))
        
    # 4. Fetch and Push updated balance
    user_row = c.execute('SELECT balance_usd FROM users WHERE username = ?', (user_id,)).fetchone()
    if user_row:
        new_balance = user_row['balance_usd']
        import asyncio
        asyncio.create_task(manager.send_to_user(user_id, json.dumps({
            "data_type": "balance_update",
            "balance_usd": new_balance
        })))

    conn.commit()
    conn.close()

# =========================
#   HEAPS (In-Memory)
#   We keep heaps for matching speed, but data is also in DB.
#   In a real system, we'd load these from DB on startup.
# =========================
from collections import defaultdict
from typing import Dict, List, Tuple, Any

# Heaps for different order types and directions
# Buy Limit: Max-Heap (stores negative price to get highest first)
# Sell Limit: Min-Heap (stores positive price to get lowest first)
# Stop-Loss: Directional Min/Max Heaps based on trigger conditions

limit_buy_heaps: Dict[str, List[Tuple[float, int, Any]]] = defaultdict(list)
limit_sell_heaps: Dict[str, List[Tuple[float, int, Any]]] = defaultdict(list)
stop_buy_heaps: Dict[str, List[Tuple[float, int, Any]]] = defaultdict(list)
stop_sell_heaps: Dict[str, List[Tuple[float, int, Any]]] = defaultdict(list)


# =========================
#   ADD ORDER HELPERS
# =========================

async def market(details):
    details_dict = details.dict()
    # Market orders execute immediately
    await execute_trade_db(
        details.order_id, 
        details.symbol, 
        details.order_price, 
        details.order_quantity, 
        details.order, 
        details.user_id,
        details.entry_price
    )
    details_dict["status"] = "completed"
    await manager.send_to_user(details.user_id, json.dumps({"data_type":"new_order","data":details_dict}))

def recover_active_orders():
    """Load active orders from DB into heaps on startup"""
    conn = get_db_connection()
    c = conn.cursor()
    rows = c.execute("SELECT * FROM orders WHERE status = 'active'").fetchall()
    conn.close()

    count = 0
    for row in rows:
        order = OrderData(
            order=row['side'] or "Buy",
            order_id=row['order_id'],
            entry_price=row['entry'],
            order_type=row['order_type'],
            order_quantity=row['quantity'],
            order_price=row['price'],
            limit_value=row['limit_value'],
            stop_value=row['stop_value'],
            status=row['status'],
            symbol=row['symbol'],
            date=row['timestamp'].split()[0] if row['timestamp'] else "",
            time=row['timestamp'].split()[1] if row['timestamp'] else "",
            user_id=row['user_id']
        )
        
        symbol = order.symbol
        if order.order_type in ["limit", "stop-limit"]:
            if order.order == "Buy":
                heappush(limit_buy_heaps[symbol], (-order.limit_value, order.order_id, order))
            else:
                heappush(limit_sell_heaps[symbol], (order.limit_value, order.order_id, order))
        elif order.order_type == "stop-loss":
            if order.order == "Buy":
                heappush(stop_buy_heaps[symbol], (order.stop_value, order.order_id, order))
            else:
                heappush(stop_sell_heaps[symbol], (-order.stop_value, order.order_id, order))
        count += 1
    print(f"Recovered {count} active orders into matching engine.")


async def add_limit_order(order):
    symbol = order.symbol
    limit_price = order.limit_value
    order_id = order.order_id
    
    if order.order == "Buy":
        # Max-heap for buy limits: highest bid first
        heappush(limit_buy_heaps[symbol], (-limit_price, order_id, order))
    else:
        # Min-heap for sell limits: lowest ask first
        heappush(limit_sell_heaps[symbol], (limit_price, order_id, order))
    
    order_dict = order.dict()
    order_dict["status"] = "active"
    await manager.send_to_user(order.user_id, json.dumps({"data_type": "new_order", "data": order_dict}))


async def add_stop_loss_order(order):
    symbol = order.symbol
    stop_price = order.stop_value
    order_id = order.order_id
    
    if order.order == "Buy":
        # Trigger when price >= stop: Min-heap
        heappush(stop_buy_heaps[symbol], (stop_price, order_id, order))
    else:
        # Trigger when price <= stop: Max-heap
        heappush(stop_sell_heaps[symbol], (-stop_price, order_id, order))
    
    order_dict = order.dict()
    order_dict["status"] = "active"
    await manager.send_to_user(order.user_id, json.dumps({"data_type": "new_order", "data": order_dict}))


async def stop_limit(order):
    await add_limit_order(order)


async def match_limit(buy_heap, sell_heap, security: str, last_price: float):
    # Match Buy Limits: Execute if Market Price <= Limit Price
    while buy_heap:
        neg_limit_price, order_id, order = buy_heap[0]
        limit_price = -neg_limit_price
        if last_price <= limit_price:
            heappop(buy_heap)
            if not await is_order_active(order_id): continue
            
            await execute_trade_db(order_id, security, limit_price, order.order_quantity, "Buy", order.user_id)
            await manager.send_to_user(order.user_id, json.dumps({
                "data_type": "limit_triggered", "side": "Buy", "security": security,
                "order_id": order_id, "limit_price": float(limit_price), "last_price": float(last_price),
                "status": "completed"
            }))
        else:
            break

    # Match Sell Limits: Execute if Market Price >= Limit Price
    while sell_heap:
        limit_price, order_id, order = sell_heap[0]
        if last_price >= limit_price:
            heappop(sell_heap)
            if not await is_order_active(order_id): continue
            
            await execute_trade_db(order_id, security, limit_price, order.order_quantity, "Sell", order.user_id)
            await manager.send_to_user(order.user_id, json.dumps({
                "data_type": "limit_triggered", "side": "Sell", "security": security,
                "order_id": order_id, "limit_price": float(limit_price), "last_price": float(last_price),
                "status": "completed"
            }))
        else:
            break

async def match_stop(buy_heap, sell_heap, security: str, last_price: float):
    # Match Buy Stop (Stop-Loss or Stop-Buy): Execute if Market Price >= Stop Price
    while buy_heap:
        stop_price, order_id, order = buy_heap[0]
        if last_price >= stop_price:
            heappop(buy_heap)
            if not await is_order_active(order_id): continue
            
            await execute_trade_db(order_id, security, stop_price, order.order_quantity, "Buy", order.user_id)
            await manager.send_to_user(order.user_id, json.dumps({
                "data_type": "stop_loss_triggered", "side": "Buy", "security": security,
                "order_id": order_id, "stop_price": float(stop_price), "last_price": float(last_price),
                "status": "completed"
            }))
        else:
            break

    # Match Sell Stop (Stop-Loss): Execute if Market Price <= Stop Price
    while sell_heap:
        neg_stop_price, order_id, order = sell_heap[0]
        stop_price = -neg_stop_price
        if last_price <= stop_price:
            heappop(sell_heap)
            if not await is_order_active(order_id): continue
            
            await execute_trade_db(order_id, security, stop_price, order.order_quantity, "Sell", order.user_id)
            await manager.send_to_user(order.user_id, json.dumps({
                "data_type": "stop_loss_triggered", "side": "Sell", "security": security,
                "order_id": order_id, "stop_price": float(stop_price), "last_price": float(last_price),
                "status": "completed"
            }))
        else:
            break

async def is_order_active(order_id):
    """Secondary check to ensure order hasn't been cancelled recently"""
    conn = get_db_connection()
    status = conn.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    return status and status['status'] == 'active'

async def price_tick(security: str, last_price: float):
    await match_limit(limit_buy_heaps[security], limit_sell_heaps[security], security, last_price)
    await match_stop(stop_buy_heaps[security], stop_sell_heaps[security], security, last_price)

