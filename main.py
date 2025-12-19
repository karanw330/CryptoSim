from fastapi import FastAPI

from app.login_back import login
from app.routes import webs
import threading
from app.routes import webs, rest
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Stock Market Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # or specify domains like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

threading.Thread(target=webs.start_market_ws, daemon=True).start()

app.include_router(login.Router, tags=["login"])
app.include_router(rest.router)
@app.get("/ping")
async def ping():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)