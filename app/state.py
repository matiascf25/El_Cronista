from typing import Dict, List, Any
from app.systems.manager import ConnectionManager
from app.systems.journal import JournalSystem
from app.components.combat.tracker import CombatTracker

# Estado Global del Servidor
SESSIONS: Dict[str, Dict[str, Any]] = {}

# Instancias Singleton
manager = ConnectionManager()
journal = JournalSystem()
combat_tracker = CombatTracker()


# ─── VTT State Manager ──────────────────────────────────

class VTTStateManager:
    """Gestiona el estado del mapa VTT en memoria (tokens, fondo, grid)."""

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "background": None,
                "tokens": {},  # token_id -> {id, name, x, y, color, type}
                "grid_visible": True,
            }
        return self.sessions[session_id]

    def set_background(self, session_id: str, image_url: str):
        self.get_session(session_id)["background"] = image_url

    def add_token(self, session_id: str, token_id: str, token_data: dict):
        self.get_session(session_id)["tokens"][token_id] = token_data

    def update_token_position(self, session_id: str, token_id: str, x: int, y: int) -> bool:
        tokens = self.get_session(session_id)["tokens"]
        if token_id in tokens:
            tokens[token_id]["x"] = x
            tokens[token_id]["y"] = y
            return True
        return False

    def remove_token(self, session_id: str, token_id: str) -> bool:
        tokens = self.get_session(session_id)["tokens"]
        if token_id in tokens:
            del tokens[token_id]
            return True
        return False

    def get_all_tokens(self, session_id: str) -> List[dict]:
        return list(self.get_session(session_id)["tokens"].values())

    def clear_tokens(self, session_id: str):
        self.get_session(session_id)["tokens"].clear()


vtt_state = VTTStateManager()


# IA & ComfyUI
from app.components.ai.comfy_client import ComfyClient
from app.components.ai.skill_images import ImageGeneratorSkill

comfy_client = ComfyClient()
image_skill = ImageGeneratorSkill(comfy_client, manager)
