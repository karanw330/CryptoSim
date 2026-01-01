from fastapi import WebSocket
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.user_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, ws: WebSocket, username: str = None):
        await ws.accept()
        self.active_connections.append(ws)
        if username:
            if username not in self.user_connections:
                self.user_connections[username] = []
            self.user_connections[username].append(ws)
        print(f"Client connected! {f'User: {username}' if username else ''}")

    async def disconnect(self, ws: WebSocket, username: str = None):
        if ws in self.active_connections:
            self.active_connections.remove(ws)
        if username and username in self.user_connections:
            if ws in self.user_connections[username]:
                self.user_connections[username].remove(ws)
                if not self.user_connections[username]:
                    del self.user_connections[username]
        print(f"Client disconnected! {f'User: {username}' if username else ''}")

    async def receive(self, ws: WebSocket):
        try:
            data = await ws.receive_text()
            print(f"Received from {ws.client}: {data}")
        except Exception as e:
            print("Receive error:", e)
            await self.disconnect(ws)

    async def broadcast(self, message: any):
        msg_str = json.dumps(message) if isinstance(message, (dict, list)) else str(message)
        for connection in self.active_connections:
            await connection.send_text(msg_str)

    async def send_to_user(self, username: str, message: any):
        if username in self.user_connections:
            msg_str = json.dumps(message) if isinstance(message, (dict, list)) else str(message)
            for connection in self.user_connections[username]:
                await connection.send_text(msg_str)

manager = WebSocketManager()