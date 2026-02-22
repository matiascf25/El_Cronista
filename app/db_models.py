"""
Modelos SQLModel para persistencia en SQLite.
"""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


# ─── Campañas ────────────────────────────────────────────

class Campaign(SQLModel, table=True):
    """Aventura/campaña completa guardada."""
    __tablename__ = "campaigns"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, unique=True)
    title: str = Field(default="Sin título")
    style: str = Field(default="")
    data_json: str = Field(default="{}")  # adventure dict serializado
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Journal ─────────────────────────────────────────────

class JournalEntryDB(SQLModel, table=True):
    """Evento del diario de sesión."""
    __tablename__ = "journal_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: Optional[int] = Field(default=None, foreign_key="campaigns.id")
    session_id: str = Field(index=True, default="default_session")
    event_type: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ─── Biblioteca: NPCs ────────────────────────────────────

class LibraryNPC(SQLModel, table=True):
    """NPC reutilizable para la biblioteca."""
    __tablename__ = "library_npcs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    race: str = Field(default="Humano")
    class_name: str = Field(default="Aldeano")
    description: str = Field(default="")
    personality: str = Field(default="")
    stats_json: str = Field(default="{}")  # {FUE:10, DES:10, ...}
    tags: str = Field(default="")  # "mercader,amigable,ciudad"
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Biblioteca: Enemigos ────────────────────────────────

class LibraryEnemy(SQLModel, table=True):
    """Enemigo reutilizable para la biblioteca."""
    __tablename__ = "library_enemies"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    cr: float = Field(default=0.25)
    hp: int = Field(default=10)
    ac: int = Field(default=10)
    attack: str = Field(default="+0")
    damage: str = Field(default="1d4")
    abilities_json: str = Field(default="[]")  # [{nombre, desc}]
    tags: str = Field(default="")  # "no-muerto,cr1,mazmorra"
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Biblioteca: Encuentros ──────────────────────────────

class LibraryEncounter(SQLModel, table=True):
    """Encuentro prefabricado para la biblioteca."""
    __tablename__ = "library_encounters"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str = Field(default="")
    difficulty: str = Field(default="Media")  # Fácil, Media, Difícil, Letal
    enemies_json: str = Field(default="[]")  # [{nombre, cantidad, hp, ac, ...}]
    environment: str = Field(default="")
    loot: str = Field(default="")
    tags: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Biblioteca: Items ───────────────────────────────────

class LibraryItem(SQLModel, table=True):
    """Item reutilizable para la biblioteca."""
    __tablename__ = "library_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    item_type: str = Field(default="objeto")  # arma, armadura, poción, objeto, herramienta
    rarity: str = Field(default="Común")  # Común, Infrecuente, Raro, Muy Raro, Legendario
    damage: str = Field(default="")  # "1d8", vacío si no aplica
    properties: str = Field(default="")  # "Versátil (1d10), Pesada"
    description: str = Field(default="")
    value_gp: int = Field(default=0)
    weight: float = Field(default=0.0)
    tags: str = Field(default="")  # "arma,marcial,cuerpo-a-cuerpo"
    created_at: datetime = Field(default_factory=datetime.utcnow)

