import os
import json
import difflib
from typing import Dict, Any, List, Optional
from app.logger import setup_logger

logger = setup_logger("srd_database")

class SRDDatabaseManager:
    """
    Motor de base de datos local en memoria para parsear el SRD de D&D 5e (JSON).
    Evita alucinaciones de IA proveyendo estadísticas matemáticas exactas.
    """
    _instance = None

    def __new__(cls, data_dir: str = "app/data/srd"):
        if cls._instance is None:
            cls._instance = super(SRDDatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, data_dir: str = "app/data/srd"):
        if self._initialized:
            return
            
        self.data_dir = data_dir
        self.monsters: List[Dict[str, Any]] = []
        self.spells: List[Dict[str, Any]] = []
        self.equipment: List[Dict[str, Any]] = []
        
        self.load_databases()
        self._initialized = True

    def load_databases(self):
        """Carga en RAM los archivos JSON desde el disco duro"""
        monsters_path = os.path.join(self.data_dir, "monsters.json")
        spells_path = os.path.join(self.data_dir, "spells.json")

        if os.path.exists(monsters_path):
            try:
                with open(monsters_path, 'r', encoding='utf-8') as f:
                    self.monsters = json.load(f)
                logger.info(f"🦇 Base de datos de Monstruos cargada: {len(self.monsters)} entradas.")
            except Exception as e:
                logger.error(f"Error cargando monsters.json: {e}")
        else:
            logger.warning(f"No se encontró la base de datos de monstruos en: {monsters_path}")
                
        if os.path.exists(spells_path):
            try:
                with open(spells_path, 'r', encoding='utf-8') as f:
                    self.spells = json.load(f)
                logger.info(f"✨ Base de datos de Conjuros cargada: {len(self.spells)} entradas.")
            except Exception as e:
                logger.error(f"Error cargando spells.json: {e}")
        else:
            logger.warning(f"No se encontró la base de datos de conjuros en: {spells_path}")

        equipment_path = os.path.join(self.data_dir, "equipment.json")
        if os.path.exists(equipment_path):
            try:
                with open(equipment_path, 'r', encoding='utf-8') as f:
                    self.equipment = json.load(f)
                logger.info(f"⚔️ Base de datos de Equipo cargada: {len(self.equipment)} entradas.")
            except Exception as e:
                logger.error(f"Error cargando equipment.json: {e}")
        else:
            logger.debug(f"No se encontró la base de datos de equipo en: {equipment_path}")

    def _fuzzy_search(self, query: str, database: List[Dict[str, Any]], field: str = "name", cutoff: float = 0.6) -> Optional[Dict[str, Any]]:
        """Busca el mejor match por nombre en la base de datos usando difflib"""
        if not database or not query:
            return None
            
        names = [item.get(field, "") for item in database]
        matches = difflib.get_close_matches(query, names, n=1, cutoff=cutoff)
        
        if matches:
            match_name = matches[0]
            for item in database:
                if item.get(field, "") == match_name:
                    return item
        return None

    def get_monster(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Itera sobre la DB de monstruos y retorna las stats canónicas completas.
        Filtra las alucinaciones del nombre (Ej: "Un Goblin Furioso" -> "Goblin").
        """
        result = self._fuzzy_search(name, self.monsters)
        if result:
            logger.debug(f"Monstruo '{name}' mapeado exitosamente al SRD oficial: {result['name']}")
        else:
            logger.debug(f"Monstruo '{name}' no encontrado en BD local. Requerirá aproximación heurística o fallback.")
        return result

    def get_spell(self, name: str) -> Optional[Dict[str, Any]]:
        """Recupera la descripción y daño matemático estricto de un conjuro"""
        return self._fuzzy_search(name, self.spells)

    def get_equipment(self, name: str) -> Optional[Dict[str, Any]]:
        """Recupera stats oficiales de armas, armaduras y equipo"""
        result = self._fuzzy_search(name, self.equipment)
        if result:
            logger.debug(f"Equipo '{name}' mapeado a: {result['name']}")
        return result

# Instancia global (Singleton) inicializada on-import para optimizar rendimiento de peticiones I/O
db = SRDDatabaseManager()
