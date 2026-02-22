from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class OracleRequest(BaseModel):
    text: str
    session_id: Optional[str] = "default_session"
    scene_id: Optional[int] = None

class SaveRequest(BaseModel):
    adventure: dict
    session_id: Optional[str] = "default_session"

class DiceRollRequest(BaseModel):
    formula: str
    session_id: Optional[str] = "default_session"

class CombatAction(BaseModel):
    action_type: str
    session_id: str = "default_session"
    data: Optional[Dict[str, Any]] = {}

class JournalEntryRequest(BaseModel):
    session_id: str = "default_session"
    event_type: str
    description: str

class NewGameRequest(BaseModel):
    setting: Optional[str] = None
    nivel: int = 1
