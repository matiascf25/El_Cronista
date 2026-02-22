"""
Motor de base de datos SQLite con SQLModel.
"""
from sqlmodel import create_engine, SQLModel, Session
from app.logger import setup_logger

logger = setup_logger("database")

DATABASE_URL = "sqlite:///cronista.db"

engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    """Crea todas las tablas si no existen y siembra datos SRD."""
    from app.db_models import Campaign, JournalEntryDB, LibraryNPC, LibraryEnemy, LibraryEncounter, LibraryItem  # noqa: F401
    SQLModel.metadata.create_all(engine)
    logger.info("✅ Base de datos SQLite inicializada (cronista.db)")

    # Sembrar datos SRD si la biblioteca está vacía
    try:
        from app.components.dnd.srd_data import seed_library_if_empty
        seed_library_if_empty()
    except Exception as e:
        logger.warning(f"⚠️ No se pudo sembrar SRD: {e}")


def get_session():
    """Retorna una sesión de base de datos."""
    return Session(engine)
