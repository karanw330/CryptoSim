from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)
        print("Client connected!")

    async def disconnect(self, ws: WebSocket):
        self.active_connections.remove(ws)
        print("Client disconnected!")

    async def receive(self, ws: WebSocket):
        try:
            data = await ws.receive_text()
            print(f"Received from {ws.client}: {data}")
            # You can process or forward the message here
        except Exception as e:
            print("Receive error:", e)
            await self.disconnect(ws)

    async def broadcast(self, message: any):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = WebSocketManager()