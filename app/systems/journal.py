from typing import List, Dict, Optional, Any
from datetime import datetime
from app.logger import setup_logger

logger_journal = setup_logger("journal")

class JournalSystem:
    """Sistema de registro de eventos de la campaña (memoria + SQLite)"""
    
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        logger_journal.info("JournalSystem inicializado")
    
    def register_event(
        self,
        session_id: str,
        event_type: str,
        description: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Registra un evento en el journal (memoria + DB)
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            logger_journal.info(f"Nuevo journal creado para sesión: {session_id}")
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description,
            "metadata": metadata or {}
        }
        
        self.sessions[session_id].append(entry)
        
        # Persistir a SQLite
        try:
            from app.database import get_session
            from app.db_models import JournalEntryDB, Campaign
            from sqlmodel import select
            
            with get_session() as db:
                # Buscar campaign_id
                campaign_id = None
                campaign = db.exec(
                    select(Campaign).where(Campaign.session_id == session_id)
                ).first()
                if campaign:
                    campaign_id = campaign.id
                
                db_entry = JournalEntryDB(
                    campaign_id=campaign_id,
                    session_id=session_id,
                    event_type=event_type,
                    description=description,
                )
                db.add(db_entry)
                db.commit()
        except Exception as e:
            logger_journal.warning(f"No se pudo persistir evento en DB: {e}")
        
        logger_journal.info(f"[{session_id}] {event_type}: {description}")
        logger_journal.debug(f"Journal size: {len(self.sessions[session_id])} eventos")
        
        return entry
    
    def get_log(self, session_id: str) -> List[Dict[str, Any]]:
        """Obtiene todos los eventos de una sesión (memoria o DB)"""
        events = self.sessions.get(session_id, [])
        
        # Si no hay en memoria, intentar cargar desde DB
        if not events:
            try:
                from app.database import get_session
                from app.db_models import JournalEntryDB
                from sqlmodel import select
                
                with get_session() as db:
                    stmt = select(JournalEntryDB).where(
                        JournalEntryDB.session_id == session_id
                    ).order_by(JournalEntryDB.timestamp)
                    db_entries = db.exec(stmt).all()
                    
                    events = [
                        {
                            "timestamp": e.timestamp.isoformat(),
                            "event_type": e.event_type,
                            "description": e.description,
                            "metadata": {}
                        }
                        for e in db_entries
                    ]
                    if events:
                        self.sessions[session_id] = events
                        logger_journal.info(f"Cargados {len(events)} eventos desde DB para {session_id}")
            except Exception as e:
                logger_journal.warning(f"No se pudo cargar journal desde DB: {e}")
        
        logger_journal.debug(f"Recuperando {len(events)} eventos para {session_id}")
        return events
    
    def clear_session(self, session_id: str):
        """Limpia el journal de una sesión"""
        if session_id in self.sessions:
            count = len(self.sessions[session_id])
            del self.sessions[session_id]
            logger_journal.info(f"Journal limpiado para {session_id} ({count} eventos eliminados)")

