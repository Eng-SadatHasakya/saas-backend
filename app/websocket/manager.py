from fastapi import WebSocket
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        # org_id -> list of websocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, org_id: int):
        await websocket.accept()
        if org_id not in self.active_connections:
            self.active_connections[org_id] = []
        self.active_connections[org_id].append(websocket)
        print(f"New connection for org {org_id}. Total: {len(self.active_connections[org_id])}")

    def disconnect(self, websocket: WebSocket, org_id: int):
        if org_id in self.active_connections:
            self.active_connections[org_id].remove(websocket)
            if not self.active_connections[org_id]:
                del self.active_connections[org_id]
        print(f"Disconnected from org {org_id}")

    async def broadcast_to_org(self, org_id: int, event: dict):
        """Send event to ALL users in the same organization only"""
        if org_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[org_id]:
                try:
                    await websocket.send_text(json.dumps(event))
                except Exception:
                    disconnected.append(websocket)
            # Clean up disconnected clients
            for ws in disconnected:
                self.active_connections[org_id].remove(ws)

    async def send_to_user(self, websocket: WebSocket, event: dict):
        """Send event to a specific user"""
        await websocket.send_text(json.dumps(event))

    def get_org_connections(self, org_id: int) -> int:
        return len(self.active_connections.get(org_id, []))

# Global instance
manager = ConnectionManager()