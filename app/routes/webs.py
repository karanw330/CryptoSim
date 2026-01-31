import asyncio
import json
import websockets
from fastapi import APIRouter, WebSocket, HTTPException
import os
import pytz
from dotenv import load_dotenv
load_dotenv()
import httpx
import datetime
from app.order_book import price_tick
from app.login_back.LoginFunctions import get_current_user
from app.manager import manager

router = APIRouter()

def absolute_change(current_price, opening_price):
    change = (current_price-opening_price)
    return change

def unix_to_ist(unix_timestamp):
    seconds = unix_timestamp / 1000.0
    utc_time = datetime.datetime.fromtimestamp(seconds, datetime.UTC)
    ist_timezone = pytz.timezone('Asia/Kolkata')
    ist_time = utc_time.astimezone(ist_timezone)
    return ist_time

# ---- Manager for all connected clients ----

connected_clients = set()

ticker_dic = {}

async def update_initial_tickers():
    global ticker_dic
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT"]
    async with httpx.AsyncClient() as client:
        for sym in symbols:
            try:
                resp = await client.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}")
                ticker_dic[f"BINANCE:{sym}"] = resp.json()
            except Exception as e:
                print(f"Error fetching ticker for {sym}: {e}")

@router.websocket("/ws/user/trades")
async def order_ws(ws: WebSocket):
    # Expect token as a query parameter: /ws/user/trades?token=eyJ...
    token = ws.query_params.get("token")
    if not token:
        # Close with policy violation (1008) if no token provided
        await ws.close(code=1008)
        return

    try:
        # validate token and fetch user (will raise HTTPException on failure)
        current_user = await get_current_user(token)
    except HTTPException:
        await ws.close(code=1008)
        return

    # At this point the user is authenticated; connect and proceed
    await manager.connect(ws, current_user.username)
    try:
        while True:
            await manager.receive(ws)  # Keep alive
    except Exception:
        await manager.disconnect(ws, current_user.username)
        print("disconnected")



# ---- Frontend socket ----
@router.websocket("/ws/market")
async def frontend_ws(ws: WebSocket):
    await ws.accept()
    connected_clients.add(ws)
    print("Connected1")
    await ws.send_text("Welcome! You are connected to /ws/market.")
    try:
        while True:
            await ws.receive_text()  # Keep alive
    except Exception:
        connected_clients.discard(ws)
        print("disconnected")

# ---- External Market Feed ----

async def start_market_ws():
    await update_initial_tickers()
    
    symbols = [
        "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:SOLUSDT",
        "BINANCE:XRPUSDT", "BINANCE:DOGEUSDT", "BINANCE:BNBUSDT"
    ]
    
    uri = f"wss://ws.finnhub.io?token={os.getenv('FINNHUB_TOKEN')}"
    
    retry_delay = 5  # Start with 5 seconds
    max_delay = 300  # Max 5 minutes
    
    while True:
        try:
            async with websockets.connect(uri) as ws:
                print("Market WS connected!")
                retry_delay = 5  # Reset delay on successful connection
                
                for sym in symbols:
                    await ws.send(json.dumps({"type": "subscribe", "symbol": sym}))
                
                async for message in ws:
                    dic = json.loads(message)
                    if "data" in dic:
                        data = dic["data"][0]
                        last_price = round(data["p"], 3)
                        ist_datetime = unix_to_ist(data["t"])
                        date_of_stockprice = ist_datetime.strftime("%Y-%m-%d")
                        time_of_stockprice = ist_datetime.strftime("%H:%M:%S")
                        symbol = data["s"]
                        try:
                            open_price = float(ticker_dic[symbol]['openPrice'])
                        except:
                            open_price = 0
                        abs_change = absolute_change(last_price, open_price)
                        perc_change = (abs_change / open_price) * 100
                        print(ticker_dic)
                        payload = json.dumps({
                            "type": "send_stock_data",
                            "high": float(ticker_dic[symbol]['highPrice']),
                            "low": float(ticker_dic[symbol]['lowPrice']),
                            "openprice": open_price,
                            "last_price": last_price,
                            "date": str(date_of_stockprice),
                            "time": str(time_of_stockprice),
                            "symbol": symbol,
                            "volume": data["v"],
                            "abs_change": round(abs_change, 2),
                            "perc_change": round(perc_change, 2)
                        })
                        
                        # Broadcast to all connected clients
                        disconnected = []
                        for client in connected_clients:
                            try:
                                await client.send_text(payload)
                            except Exception:
                                disconnected.append(client)
                        
                        for client in disconnected:
                            connected_clients.discard(client)
                        
                        # Update order book
                        await price_tick(symbol, last_price)
                        
        except Exception as e:
            error_msg = str(e)
            print(f"Market WS error/closed: {error_msg}")
            
            # Check for 429 Too Many Requests
            if "429" in error_msg:
                print("Detected 429 (Too Many Requests). Waiting 60 seconds before retrying...")
                await asyncio.sleep(60)
                retry_delay = 5 # Reset exponential backoff after the long wait
            else:
                print(f"Reconnecting in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                # Exponential backoff
                retry_delay = min(retry_delay * 2, max_delay)
