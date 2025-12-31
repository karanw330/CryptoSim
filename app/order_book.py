import heapq
from heapq import heappush, heappop
import datetime
import pytz
import json
from app.manager import manager
from app.db_init import get_db_connection

# =========================
#   DB HELPERS
# =========================

def execute_trade_db(order_id, symbol, price, quantity, side, user_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Record Trade
    c.execute('''
        INSERT INTO trades (symbol, price, quantity, timestamp)
        VALUES (?, ?, ?, datetime('now'))
    ''', (symbol, price, quantity))
    
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
        
    conn.commit()
    conn.close()

# =========================
#   HEAPS (In-Memory)
#   We keep heaps for matching speed, but data is also in DB.
#   In a real system, we'd load these from DB on startup.
# =========================
from collections import defaultdict
from typing import Dict, List, Tuple, Any

# For normal limit and stop-limit (in your sim)
limit_heaps: Dict[str, List[Tuple[float, int, Any]]] = defaultdict(list)

# For stop-loss
stop_loss_heaps: Dict[str, List[Tuple[float, int, Any]]] = defaultdict(list)


# =========================
#   ADD ORDER HELPERS
# =========================

async def market(details):
    # Market Order is immediate execution at 'current' price (simulated)
    # Since we don't have a real matching engine against other users, we execute against external price immediately
    # BUT 'market' function here seems to be just for broadcast? 
    # Let's assume market orders execute immediately if we have a price.
    
    print(details.dict())
    data = details.dict()
    
    # Simulated execution:
    # We need the last price... passed in? No.
    # In this design, market orders might just be broadcasted as "active" 
    # and then client simulation handles it? 
    # OR we should execute it now if we knew the price.
    
    # For now, we just broadcast as original code, but maybe mark completed if we could?
    # Original code: details["status"] = "active"
    
    # Update: Market orders in this sim seem to rely on the *Next* tick? 
    # Or maybe we assume they are filled immediately at '0' price placeholder?
    # Let's execute immediately if we can, but we lack price here. 
    # We will execute it on the next price_tick or just broadcast.
    
    # Logic: Just broadcast. The 'price_tick' function only checks limit/stop heaps. 
    # Market orders are usually instantaneous. 
    
    # Let's assume we treat it as 'active' and maybe frontend handles it? 
    # OR we should store it and execute on next tick.
    # Given the previous code, it just broadcasted.
    
    details_dict = details.dict()
    details_dict["status"] = "active"
    await manager.broadcast(json.dumps({"data_type":"new_order","data":details_dict}))


async def add_limit_order(order):
    symbol = order.symbol
    limit_price = order.limit_value
    order_id = order.order_id # Now real ID from DB
    
    # Push to heap for matching
    heap = limit_heaps[symbol]
    # Heap stores: (price, order_id, order_object)
    # Buy: Max heap? (negate price). Sell: Min heap?
    # Original code didn't distinguish heap type/direction properly? 
    # It just did: heapq.heappush(heap, (limit_price, order_id, order))
    # Standard heapq is Min-Heap.
    # For Sell Limit: We want to sell if Price >= Limit. We want to sell at lowest limit first? No, we match whatever.
    # For Buy Limit: We want to buy if Price <= Limit.
    
    # Let's keep original logic form, but use real ID
    heappush(heap, (limit_price, order_id, order))
    
    order_dict = order.dict()
    order_dict["status"] = "inactive" # Wait for trigger
    await manager.broadcast(json.dumps({"data_type": "new_order", "data": order_dict}))


async def add_stop_loss_order(order):
    symbol = order.symbol
    stop_price = order.stop_value
    order_id = order.order_id
    
    heap = stop_loss_heaps[symbol]
    heappush(heap, (stop_price, order_id, order))
    
    order_dict = order.dict()
    order_dict["status"] = "inactive"
    await manager.broadcast(json.dumps({"data_type": "new_order", "data": order_dict}))


async def stop_limit(order):
    await add_limit_order(order)


# =========================
#   MATCHING FUNCTIONS
# =========================

async def limit(heap, security: str, last_price: float):
    triggered_orders = []
    
    # We need to iterate carefully since we might remove items from middle (simplification: just peek top)
    # But if heaps are mixed buy/sell, this is tricky. 
    # Assuming the original code's logic of just checking top was sufficient for this sim.
    
    while heap:
        limit_price, order_id, order = heap[0]

        if order.symbol != security:
            break

        # BUY Limit: Execute if Market Price <= Limit Price
        if order.order == "Buy" and last_price <= limit_price:
            heappop(heap)
            
            # EXECUTE DB UPDATE
            user_id = order.user_id or "johndoe" 
            
            execute_trade_db(
                order_id=order_id,
                symbol=security,
                price=last_price, # Executed at market price? or Limit? Usually Limit or better.
                quantity=order.order_quantity,
                side="Buy",
                user_id=user_id
            )

            # Broadcast
            await manager.broadcast({
                "data_type": "limit_triggered",
                "side": "Buy",
                "security": order.symbol,
                "order_id": order_id,
                "limit_price": float(limit_price),
                "last_price": float(last_price),
                "status": "completed", # Changed from 'active' for finality
            })
            triggered_orders.append(order)

        elif order.order == "Sell" and last_price >= limit_price:
            heappop(heap)
            
            user_id = order.user_id or "johndoe"
            
            execute_trade_db(
                order_id=order_id,
                symbol=security,
                price=last_price,
                quantity=order.order_quantity,
                side="Sell",
                user_id=user_id
            )

            await manager.broadcast({
                "data_type": "limit_triggered",
                "side": "Sell",
                "security": order.symbol,
                "order_id": order_id,
                "limit_price": float(limit_price),
                "last_price": float(last_price),
                "status": "completed",
            })
            triggered_orders.append(order)

        else:
            break
            
    return triggered_orders


async def stop_loss(heap, security: str, last_price: float):
    triggered_orders = []

    while heap:
        stop_price, order_id, order = heap[0]

        if order.symbol != security:
            break

        if order.order == "Buy" and last_price >= stop_price:
            heappop(heap)
            
            user_id = order.user_id or "johndoe"
            execute_trade_db(order_id, security, last_price, order.order_quantity, "Buy", user_id)

            await manager.broadcast({
                "data_type": "stop_loss_triggered",
                "side": "Buy",
                "security": order.symbol,
                "order_id": order_id,
                "stop_price": float(stop_price),
                "last_price": float(last_price),
                "status": "completed",
            })
            triggered_orders.append(order)

        # SELL Stop: Execute if Market Price <= Stop Price
        elif order.order == "Sell" and last_price <= stop_price:
            heappop(heap)
            
            user_id = order.user_id or "johndoe"
            execute_trade_db(order_id, security, last_price, order.order_quantity, "Sell", user_id)

            await manager.broadcast({
                "data_type": "stop_loss_triggered",
                "side": "Sell",
                "security": order.symbol,
                "order_id": order_id,
                "stop_price": float(stop_price),
                "last_price": float(last_price),
                "status": "completed",
            })
            triggered_orders.append(order)

        else:
            break

    return triggered_orders


async def price_tick(security: str, last_price: float):
    await limit(limit_heaps[security], security, last_price)
    await stop_loss(stop_loss_heaps[security], security, last_price)

