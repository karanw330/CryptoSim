import json
from app.manager import manager
from fastapi import APIRouter, Depends
from app.routes.PydanticModels import *
from app.login_back.LoginFunctions import get_current_user
from app.login_back.LoginPydanticModels import User
from app.order_book import *

router = APIRouter()

funcDict = {
    "limit": add_limit_order,
    "stop-loss": add_stop_loss_order,
    "stop-limit": stop_limit,
}
@router.post("/order")
async def order(data: OrderData, current_user: User = Depends(get_current_user)):
    from app.db_init import get_db_connection
    virtual_price = 0
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Validate Balance / Portfolio
        user_id = current_user.username

            # BUY: Check USD balance
        if data.order == "Buy":
            if data.order_type == "market":
                virtual_price = data.entry_price
                user = cursor.execute('SELECT balance_usd, locked_usd FROM users WHERE username = ?', (user_id,)).fetchone()
                if not user or user['balance_usd'] - user['locked_usd'] < (data.order_quantity * virtual_price):
                    print("Insufficient funds")
                    return {"status": "error", "reason": "Insufficient funds"}
                new_bal = user['balance_usd'] - (data.order_quantity * virtual_price)
                cursor.execute('UPDATE users SET balance_usd = ? WHERE username = ?', (new_bal, user_id))
            elif data.order_type == "stop-loss":
                virtual_price = data.stop_value
                req= data.order_quantity * virtual_price
                user = cursor.execute('UPDATE users SET locked_usd = locked_usd + ? WHERE username = ? AND balance_usd - locked_usd >= ?', (req,user_id,req,))
                if not user or cursor.rowcount ==0:   #row count gives number of rows affected by last query
                    print("Insufficient funds")
                    return {"status": "error", "reason": "Insufficient funds"}
            else:
                virtual_price = data.limit_value
                req = data.order_quantity * virtual_price
                user = cursor.execute('UPDATE users SET locked_usd = locked_usd + ? WHERE username = ? AND balance_usd - locked_usd >= ?', (req, user_id, req,))
                if not user or cursor.rowcount == 0:  # row count gives number of rows affected by last query
                    print("Insufficient funds")
                    return {"status": "error", "reason": "Insufficient funds"}



        # SELL: Check Coin balance
        elif data.order == "Sell":
            port = cursor.execute('SELECT amount FROM portfolio WHERE user_id = ? AND symbol = ?',
                               (user_id, data.symbol)).fetchone()

            # Extract base symbol e.g. BINANCE:BTCUSDT -> BTC ??
            # Frontend sends "BINANCE:BTCUSDT".

            if not port or port['amount'] < data.order_quantity:
                 print("Insufficient assets")
                 return {"status": "error", "reason": "Insufficient assets"}

            # Update Portfolio (Lock assets)
            new_amt = port['amount'] - data.order_quantity
            cursor.execute('UPDATE portfolio SET amount = ? WHERE user_id = ? AND symbol = ?',
                           (new_amt, user_id, data.symbol))


        # 2. Insert into DB
        stat=""
        if data.order_type == "market":
            stat="completed"
        else:
            stat="active"
        cursor.execute('''
            INSERT INTO orders (user_id, symbol, order_type, side, quantity, price, limit_value, stop_value, status, timestamp, entry)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
        ''', (user_id, data.symbol, data.order_type, data.order, data.order_quantity, data.order_price,
              data.limit_value or 0, data.stop_value or 0, stat, virtual_price))
        
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # 3. Pass to Matching Engine (Optimistic)
        # We attach the real DB ID to the object so matching engine uses it
        data.order_id = order_id
        data.user_id = user_id
        
        func = funcDict[data.order_type]
        print(f"Order {order_id} placed: {data}")
        
        if data.order_type == "market":
            pass
        else:
            await func(data)
            
        return {"status": "ok", "order_id": order_id}
    except Exception as e:
        print("Error:", e)
        return {"status":"error", "detail": str(e)}

@router.delete("/delorder")
async def delorder(data: Del, current_user: User = Depends(get_current_user)):
    from app.db_init import get_db_connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Verify ownership and get details for refund
        order = cursor.execute('SELECT * FROM orders WHERE order_id = ? AND user_id = ?', 
                             (data.order_id, current_user.username)).fetchone()
        if not order:
            return {"status": "error", "reason": "Order not found or unauthorized"}
        
        if order['status'] != 'active':
            return {"status": "error", "reason": f"Cannot delete order in '{order['status']}' state"}

        # 2. Update status
        cursor.execute("UPDATE orders SET status = 'cancelled' WHERE order_id = ?", (data.order_id,))
        
        # 3. Refund/Unlock
        if order['side'] == 'Buy':
            cursor.execute("UPDATE users SET locked_usd = locked_usd - ? WHERE username = ?",
                           (order['price'], current_user.username))
        else:
            # Refund Asset
            cursor.execute("UPDATE portfolio SET amount = amount + ? WHERE user_id = ? AND symbol = ?",
                         (order['quantity'], current_user.username, order['symbol']))

        conn.commit()
        conn.close()
        print(f"User {current_user.username} cancelled order {data.order_id}")
        return {"status": "ok", "order_id": data.order_id}
    except Exception as e:
        print("Error:", e)
        return {"status":"error", "detail": str(e)}

@router.patch("/updateorder")
async def updateorder(data: OrderUpdate, current_user: User = Depends(get_current_user)):
    # To keep the matching engine simple, an "update" is a "cancel + new order"
    # This ensures it gets re-inserted into heaps with correct priority
    from app.db_init import get_db_connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Get old order
        old = cursor.execute('SELECT * FROM orders WHERE order_id = ? AND user_id = ?', 
                           (data.order_id, current_user.username)).fetchone()
        if not old or old['status'] != 'active':
            return {"status": "error", "reason": "Order not found or inactive"}

        # 2. Cancel old
        cursor.execute("UPDATE orders SET status = 'cancelled' WHERE order_id = ?", (data.order_id,))
        if old['side'] == 'Buy':
            cursor.execute("UPDATE users SET locked_usd = locked_usd - ? WHERE username = ?",
                         (old['price'], current_user.username))
        else:
            cursor.execute("UPDATE portfolio SET amount = amount + ? WHERE user_id = ? AND symbol = ?", 
                         (old['quantity'], current_user.username, old['symbol']))
        
        conn.commit()
        conn.close()

        # 3. Create new order with updated values
        new_data = OrderData(
            symbol=old['symbol'],
            order=old['side'],
            order_type=old['order_type'],
            order_quantity=data.order_quantity,
            order_price=data.order_price,
            limit_value=data.limit_value,
            stop_value=data.stop_value,
            status="active",
            date="", time="",
            user_id=current_user.username,
            order_id=None,
            entry_price=old['price']
        )
        
        return await order(new_data, current_user)

    except Exception as e:
        print("Update Error:", e)
        return {"status": "error", "detail": str(e)}

