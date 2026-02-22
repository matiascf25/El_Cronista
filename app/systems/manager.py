from typing import Dict, List, Optional
from fastapi import WebSocket
from app.logger import setup_logger

logger_manager = setup_logger("websocket")


class ConnectionManager:
    """
    Gestiona múltiples conexiones WebSocket por sesión.
    Permite DM + Players conectados simultáneamente.
    """

    def __init__(self):
        # Dict[str, List[WebSocket]] — múltiples clientes por sesión
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.connection_types: Dict[int, str] = {}  # id(ws) -> "dm" | "player"
        self.connection_metadata: Dict[int, Dict[str, any]] = {}  # id(ws) -> {name, type, timestamp}
        logger_manager.info("ConnectionManager multi-cliente inicializado")

    async def connect(
        self, 
        session_id: str, 
        ws: WebSocket, 
        client_type: str = "player",
        client_name: str = "Unknown"
    ):
        """
        Acepta y registra una nueva conexión WebSocket.
        
        Args:
            session_id: ID de la sesión
            ws: WebSocket connection
            client_type: "dm" o "player"
            client_name: Display name for the client
        """
        from datetime import datetime
        
        await ws.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(ws)
        self.connection_types[id(ws)] = client_type
        self.connection_metadata[id(ws)] = {
            "name": client_name,
            "type": client_type,
            "connected_at": datetime.now().isoformat(),
            "session_id": session_id
        }

        total = len(self.active_connections[session_id])
        logger_manager.info(
            f"✓ {client_name} ({client_type}) conectado a {session_id} — Total: {total}"
        )
        
        # Broadcast connection event to all clients in session (except launcher)
        if client_type != "launcher":
            await self.send_to_session(session_id, {
                "type": "client_connected",
                "client_name": client_name,
                "client_type": client_type,
                "total_connections": total,
                "timestamp": datetime.now().isoformat()
            })

    def disconnect(self, session_id: str, ws: Optional[WebSocket] = None):
        """
        Desconecta un WebSocket específico (o limpia la sesión).
        Returns metadata about disconnected client for broadcasting.
        """
        if session_id not in self.active_connections:
            logger_manager.warning(f"Intento de desconectar sesión inexistente: {session_id}")
            return None
        
        disconnected_meta = None

        if ws is not None:
            # Get metadata before removing
            ws_id = id(ws)
            disconnected_meta = self.connection_metadata.get(ws_id, {
                "name": "Unknown",
                "type": "unknown"
            })
            
            if ws in self.active_connections[session_id]:
                self.active_connections[session_id].remove(ws)
                self.connection_types.pop(ws_id, None)
                self.connection_metadata.pop(ws_id, None)
            
            client_name = disconnected_meta.get("name", "Unknown")
            client_type = disconnected_meta.get("type", "unknown")
            
            if client_type != "launcher":
                logger_manager.info(f"✗ {client_name} ({client_type}) desconectado de {session_id}")
        else:
            # Fallback: limpiar toda la sesión (compatibilidad)
            for w in self.active_connections[session_id]:
                ws_id = id(w)
                self.connection_types.pop(ws_id, None)
                self.connection_metadata.pop(ws_id, None)
            self.active_connections[session_id].clear()

        # Eliminar sesión si no quedan conexiones
        if not self.active_connections[session_id]:
            del self.active_connections[session_id]
        
        return disconnected_meta

    async def send_to_session(self, session_id: str, msg: dict):
        """Envía un mensaje JSON a TODOS los clientes de la sesión."""
        if session_id not in self.active_connections:
            logger_manager.warning(f"Intento de enviar a sesión no conectada: {session_id}")
            return

        dead: List[WebSocket] = []
        for ws in list(self.active_connections[session_id]):
            try:
                await ws.send_json(msg)
                logger_manager.debug(f"Mensaje enviado a {session_id}: {msg.get('type', 'unknown')}")
            except Exception as e:
                logger_manager.error(f"Error enviando mensaje: {e}")
                dead.append(ws)

        for ws in dead:
            self.disconnect(session_id, ws)

    async def broadcast_except(self, session_id: str, msg: dict, exclude_ws: WebSocket):
        """Envía mensaje a todos los clientes EXCEPTO el indicado."""
        if session_id not in self.active_connections:
            return

        dead: List[WebSocket] = []
        for ws in list(self.active_connections[session_id]):
            if ws is exclude_ws:
                continue
            try:
                await ws.send_json(msg)
            except Exception as e:
                logger_manager.error(f"Error en broadcast: {e}")
                dead.append(ws)

        for ws in dead:
            self.disconnect(session_id, ws)

    async def send_to_type(self, session_id: str, msg: dict, client_type: str):
        """Envía mensaje solo a clientes de un tipo ('dm' o 'player')."""
        if session_id not in self.active_connections:
            return

        dead: List[WebSocket] = []
        for ws in list(self.active_connections[session_id]):
            if self.connection_types.get(id(ws)) == client_type:
                try:
                    await ws.send_json(msg)
                except Exception as e:
                    logger_manager.error(f"Error enviando a {client_type}: {e}")
                    dead.append(ws)

        for ws in dead:
            self.disconnect(session_id, ws)

    def get_connection_count(self, session_id: str) -> int:
        """Retorna número de conexiones activas en la sesión."""
        return len(self.active_connections.get(session_id, []))
    
    def get_connected_clients(self, session_id: str) -> List[Dict[str, any]]:
        """
        Retorna lista de clientes conectados con su metadata.
        
        Returns:
            List of dicts with: {name, type, connected_at}
        """
        if session_id not in self.active_connections:
            return []
        
        clients = []
        for ws in self.active_connections[session_id]:
            meta = self.connection_metadata.get(id(ws), {})
            # Exclude launcher from the list
            if meta.get("type") == "launcher":
                continue

            clients.append({
                "name": meta.get("name", "Unknown"),
                "type": meta.get("type", "unknown"),
                "connected_at": meta.get("connected_at", ""),
                "online": True
            })
        
        return clients
