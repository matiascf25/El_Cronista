from typing import List, Dict
from app.state import journal
from app.logger import setup_logger

logger = setup_logger("memory")

def get_narrative_context(session_id: str, limit: int = 10) -> str:
    """
    Recupera los últimos eventos del journal y los formatea como contexto narrativo.
    """
    try:
        events = journal.get_log(session_id)
        if not events:
            return ""
            
        # Tomar los últimos 'limit' eventos relevantes
        # Filtramos eventos técnicos si es necesario, por ahora tomamos todo
        recent_events = events[-limit:]
        
        context_lines = ["RESUMEN DE EVENTOS RECIENTES:"]
        for evt in recent_events:
            timestamp = evt.get("timestamp", "")
            tipo = evt.get("type", "evento")
            desc = evt.get("description", "")
            context_lines.append(f"- [{tipo}] {desc}")
            
        return "\n".join(context_lines)
        
    except Exception as e:
        logger.error(f"Error obteniendo contexto narrativo: {e}")
        return ""
