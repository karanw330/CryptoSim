from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from app.login_back import login
from app.otp_verification import apis
from app.routes import webs
from app.routes import webs, rest
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app import db_init

# Initialize DB
db_init.init_db()

from app.order_book import recover_active_orders
recover_active_orders()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start market websocket background task
    task = asyncio.create_task(webs.start_market_ws())
    yield
    # Shutdown: Cancel the task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Market WS task cancelled")

app = FastAPI(title="Stock Market Simulator", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # or specify domains like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.Router, tags=["login"])
app.include_router(apis.router, tags=["otp"])
app.include_router(rest.router)
app.include_router(webs.router)  # <-- expose websocket routes (/ws/market, /ws/user/trades)
@app.get("/ping")
async def ping():
    return {"status": "ok"}

# # if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)