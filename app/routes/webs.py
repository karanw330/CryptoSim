import asyncio
import json
import websocket
from fastapi import APIRouter, WebSocket
import os
import pytz
from dotenv import load_dotenv
load_dotenv()
import requests
import datetime
from app.order_book import price_tick
router = APIRouter()
loop = asyncio.get_event_loop()

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
from app.manager import manager

connected_clients = set()

btc_ticker = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT").json()
eth_ticker = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=ETHUSDT").json()
sol_ticker = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=SOLUSDT").json()
xrp_ticker = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=XRPUSDT").json()
dog_ticker = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=DOGEUSDT").json()
bnb_ticker = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BNBUSDT").json()
ticker_dic = {
    "BINANCE:BTCUSDT":btc_ticker,
    "BINANCE:ETHUSDT":eth_ticker,
    "BINANCE:SOLUSDT":sol_ticker,
    "BINANCE:XRPUSDT":xrp_ticker,
    "BINANCE:DOGEUSDT":dog_ticker,
    "BINANCE:BNBUSDT":bnb_ticker
    }


@router.websocket("/ws/user/trades")
async def order_ws(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await manager.receive(ws)  # Keep alive
    except Exception:
        await manager.disconnect(ws)
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
stop_ws = False

def start_market_ws():
    global stop_ws

    symbols = [
        "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:SOLUSDT",
        "BINANCE:XRPUSDT", "BINANCE:DOGEUSDT", "BINANCE:BNBUSDT"
    ]

    def on_message(ws, message):
        dic = json.loads(message)
        if "data" in dic:
            last_price = round(dic["data"][0]["p"], 3)
            ist_datetime = unix_to_ist(dic["data"][0]["t"])
            date_of_stockprice = ist_datetime.strftime("%Y-%m-%d")
            time_of_stockprice = ist_datetime.strftime("%H:%M:%S")
            symbol = dic["data"][0]["s"]
            abs_change = absolute_change(last_price, float(ticker_dic[symbol]['openPrice']))
            perc_change = (abs_change / float(ticker_dic[symbol]['openPrice'])) * 100
            payload = json.dumps({
                "type": "send_stock_data",
                "high": float(ticker_dic[symbol]['highPrice']),
                "low": float(ticker_dic[symbol]['lowPrice']),
                "openprice": float(ticker_dic[symbol]['openPrice']),
                "last_price": last_price,
                "date": str(date_of_stockprice),
                "time": str(time_of_stockprice),
                "symbol":symbol,
                "volume": dic["data"][0]["v"],
                "abs_change": round(abs_change,2),
                "perc_change": round(perc_change,2)
            })
            for client in list(connected_clients):
                asyncio.run_coroutine_threadsafe(client.send_text(payload), loop)
            asyncio.run_coroutine_threadsafe(price_tick(symbol, last_price), loop)

    def on_error(ws, error):
        print("Error:", error)

    def on_close(ws, code, msg):
        print("Market WS closed:", code, msg)

    def on_open(ws):
        print("Market WS connected!")
        for sym in symbols:
            ws.send(json.dumps({"type": "subscribe", "symbol": sym}))

    try:
        while not stop_ws:
            ws = websocket.WebSocketApp(
                f"wss://ws.finnhub.io?token={os.getenv('FINNHUB_TOKEN')}",
                on_message= on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            # ping_interval lets Ctrl+C interrupt easier
            ws.run_forever(ping_interval=10, ping_timeout=5)
    except KeyboardInterrupt:
        print("Stopping Market WS...")
        stop_ws = True

################################################ websocket #######################################################
