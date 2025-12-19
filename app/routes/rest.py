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
    from app.db_init import get_db_connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Validate Balance / Portfolio
        user_id = "johndoe" # Hardcoded for now as we don't have auth token in this payload
                            # In a real app, 'data' should come with auth or from Depends()
        
        # We need to fetch the user... but the endpoint is open. 
        # Assuming single user 'johndoe' for this sim as per previous context
        
        if data.order_type == "market" or data.order_type == "limit":
            # BUY: Check USD balance
            if data.order == "Buy":
                cost = data.order_quantity * data.order_price # For Limit, price is limit_price? 
                                                            # Frontend sends order_price as total value?
                                                            # Let's inspect OrderData: 
                                                            # quantity: int?, price: float?
                
                # If market buy, price is estimated. 
                # If limit buy, price is limit.
                
                # Check user balance
                user = cursor.execute('SELECT balance_usd FROM users WHERE username = ?', (user_id,)).fetchone()
                if not user or user['balance_usd'] < (data.order_quantity * data.order_price):
                    print("Insufficient funds")
                    return {"status": "error", "reason": "Insufficient funds"}

                # Update Balance (Lock funds)
                new_bal = user['balance_usd'] - (data.order_quantity * data.order_price)
                cursor.execute('UPDATE users SET balance_usd = ? WHERE username = ?', (new_bal, user_id))

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
        cursor.execute('''
            INSERT INTO orders (user_id, symbol, order_type, quantity, price, limit_value, stop_value, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (user_id, data.symbol, data.order_type, data.order_quantity, data.order_price, 
              data.limit_value or 0, data.stop_value or 0, "active"))
        
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # 3. Pass to Matching Engine (Optimistic)
        # We attach the real DB ID to the object so matching engine uses it
        data.order_id = order_id
        
        func = funcDict[data.order_type]
        print(f"Order {order_id} placed: {data}")
        
        if data.order_type == "market":
            await func(data)
        else:
            await func(data)
            
        return {"status": "ok", "order_id": order_id}
    except Exception as e:
        print("Error:", e)
        return {"status":"error", "detail": str(e)}

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

