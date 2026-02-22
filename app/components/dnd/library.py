"""
CRUD para la biblioteca de contenido reutilizable (NPCs, Enemigos, Encuentros, Items).
"""
import json
from typing import List, Optional, Dict, Any
from sqlmodel import select
from app.database import get_session
from app.db_models import LibraryNPC, LibraryEnemy, LibraryEncounter, LibraryItem
from app.logger import setup_logger

logger = setup_logger("library")


# ─── NPCs ────────────────────────────────────────────────

def crear_npc(data: Dict[str, Any]) -> LibraryNPC:
    """Crea un NPC en la biblioteca."""
    npc = LibraryNPC(
        name=data["name"],
        race=data.get("race", "Humano"),
        class_name=data.get("class_name", "Aldeano"),
        description=data.get("description", ""),
        personality=data.get("personality", ""),
        stats_json=json.dumps(data.get("stats", {}), ensure_ascii=False),
        tags=data.get("tags", ""),
    )
    with get_session() as db:
        db.add(npc)
        db.commit()
        db.refresh(npc)
        logger.info(f"✅ NPC creado: {npc.name} (id={npc.id})")
        return npc


def listar_npcs(tag: Optional[str] = None) -> List[LibraryNPC]:
    """Lista NPCs, opcionalmente filtrados por tag."""
    with get_session() as db:
        stmt = select(LibraryNPC).order_by(LibraryNPC.name)
        if tag:
            stmt = stmt.where(LibraryNPC.tags.contains(tag))
        return list(db.exec(stmt).all())


def obtener_npc(npc_id: int) -> Optional[LibraryNPC]:
    with get_session() as db:
        return db.get(LibraryNPC, npc_id)


def actualizar_npc(npc_id: int, data: Dict[str, Any]) -> Optional[LibraryNPC]:
    with get_session() as db:
        npc = db.get(LibraryNPC, npc_id)
        if not npc:
            return None
        for key, val in data.items():
            if key == "stats":
                npc.stats_json = json.dumps(val, ensure_ascii=False)
            elif hasattr(npc, key):
                setattr(npc, key, val)
        db.add(npc)
        db.commit()
        db.refresh(npc)
        logger.info(f"✏️ NPC actualizado: {npc.name} (id={npc.id})")
        return npc


def eliminar_npc(npc_id: int) -> bool:
    with get_session() as db:
        npc = db.get(LibraryNPC, npc_id)
        if not npc:
            return False
        db.delete(npc)
        db.commit()
        logger.info(f"🗑️ NPC eliminado: {npc.name} (id={npc_id})")
        return True


# ─── Enemigos ────────────────────────────────────────────

def crear_enemy(data: Dict[str, Any]) -> LibraryEnemy:
    """Crea un enemigo en la biblioteca."""
    enemy = LibraryEnemy(
        name=data["name"],
        cr=data.get("cr", 0.25),
        hp=data.get("hp", 10),
        ac=data.get("ac", 10),
        attack=data.get("attack", "+0"),
        damage=data.get("damage", "1d4"),
        abilities_json=json.dumps(data.get("abilities", []), ensure_ascii=False),
        tags=data.get("tags", ""),
    )
    with get_session() as db:
        db.add(enemy)
        db.commit()
        db.refresh(enemy)
        logger.info(f"✅ Enemigo creado: {enemy.name} (id={enemy.id})")
        return enemy


def listar_enemies(tag: Optional[str] = None) -> List[LibraryEnemy]:
    with get_session() as db:
        stmt = select(LibraryEnemy).order_by(LibraryEnemy.name)
        if tag:
            stmt = stmt.where(LibraryEnemy.tags.contains(tag))
        return list(db.exec(stmt).all())


def obtener_enemy(enemy_id: int) -> Optional[LibraryEnemy]:
    with get_session() as db:
        return db.get(LibraryEnemy, enemy_id)


def actualizar_enemy(enemy_id: int, data: Dict[str, Any]) -> Optional[LibraryEnemy]:
    with get_session() as db:
        enemy = db.get(LibraryEnemy, enemy_id)
        if not enemy:
            return None
        for key, val in data.items():
            if key == "abilities":
                enemy.abilities_json = json.dumps(val, ensure_ascii=False)
            elif hasattr(enemy, key):
                setattr(enemy, key, val)
        db.add(enemy)
        db.commit()
        db.refresh(enemy)
        logger.info(f"✏️ Enemigo actualizado: {enemy.name} (id={enemy.id})")
        return enemy


def eliminar_enemy(enemy_id: int) -> bool:
    with get_session() as db:
        enemy = db.get(LibraryEnemy, enemy_id)
        if not enemy:
            return False
        db.delete(enemy)
        db.commit()
        logger.info(f"🗑️ Enemigo eliminado: {enemy.name} (id={enemy_id})")
        return True


# ─── Encuentros ──────────────────────────────────────────

def crear_encounter(data: Dict[str, Any]) -> LibraryEncounter:
    """Crea un encuentro en la biblioteca."""
    encounter = LibraryEncounter(
        name=data["name"],
        description=data.get("description", ""),
        difficulty=data.get("difficulty", "Media"),
        enemies_json=json.dumps(data.get("enemies", []), ensure_ascii=False),
        environment=data.get("environment", ""),
        loot=data.get("loot", ""),
        tags=data.get("tags", ""),
    )
    with get_session() as db:
        db.add(encounter)
        db.commit()
        db.refresh(encounter)
        logger.info(f"✅ Encuentro creado: {encounter.name} (id={encounter.id})")
        return encounter


def listar_encounters(tag: Optional[str] = None) -> List[LibraryEncounter]:
    with get_session() as db:
        stmt = select(LibraryEncounter).order_by(LibraryEncounter.name)
        if tag:
            stmt = stmt.where(LibraryEncounter.tags.contains(tag))
        return list(db.exec(stmt).all())


def obtener_encounter(encounter_id: int) -> Optional[LibraryEncounter]:
    with get_session() as db:
        return db.get(LibraryEncounter, encounter_id)


def actualizar_encounter(encounter_id: int, data: Dict[str, Any]) -> Optional[LibraryEncounter]:
    with get_session() as db:
        encounter = db.get(LibraryEncounter, encounter_id)
        if not encounter:
            return None
        for key, val in data.items():
            if key == "enemies":
                encounter.enemies_json = json.dumps(val, ensure_ascii=False)
            elif hasattr(encounter, key):
                setattr(encounter, key, val)
        db.add(encounter)
        db.commit()
        db.refresh(encounter)
        logger.info(f"✏️ Encuentro actualizado: {encounter.name} (id={encounter.id})")
        return encounter


def eliminar_encounter(encounter_id: int) -> bool:
    with get_session() as db:
        encounter = db.get(LibraryEncounter, encounter_id)
        if not encounter:
            return False
        db.delete(encounter)
        db.commit()
        logger.info(f"🗑️ Encuentro eliminado: {encounter.name} (id={encounter_id})")
        return True


# ─── Items ───────────────────────────────────────────────

def crear_item(data: Dict[str, Any]) -> LibraryItem:
    """Crea un item en la biblioteca."""
    item = LibraryItem(
        name=data["name"],
        item_type=data.get("item_type", "objeto"),
        rarity=data.get("rarity", "Común"),
        damage=data.get("damage", ""),
        properties=data.get("properties", ""),
        description=data.get("description", ""),
        value_gp=data.get("value_gp", 0),
        weight=data.get("weight", 0.0),
        tags=data.get("tags", ""),
    )
    with get_session() as db:
        db.add(item)
        db.commit()
        db.refresh(item)
        logger.info(f"✅ Item creado: {item.name} (id={item.id})")
        return item


def listar_items(tag: Optional[str] = None, item_type: Optional[str] = None) -> List[LibraryItem]:
    with get_session() as db:
        stmt = select(LibraryItem).order_by(LibraryItem.name)
        if tag:
            stmt = stmt.where(LibraryItem.tags.contains(tag))
        if item_type:
            stmt = stmt.where(LibraryItem.item_type == item_type)
        return list(db.exec(stmt).all())


def obtener_item(item_id: int) -> Optional[LibraryItem]:
    with get_session() as db:
        return db.get(LibraryItem, item_id)


def actualizar_item(item_id: int, data: Dict[str, Any]) -> Optional[LibraryItem]:
    with get_session() as db:
        item = db.get(LibraryItem, item_id)
        if not item:
            return None
        for key, val in data.items():
            if hasattr(item, key):
                setattr(item, key, val)
        db.add(item)
        db.commit()
        db.refresh(item)
        logger.info(f"✏️ Item actualizado: {item.name} (id={item.id})")
        return item


def eliminar_item(item_id: int) -> bool:
    with get_session() as db:
        item = db.get(LibraryItem, item_id)
        if not item:
            return False
        db.delete(item)
        db.commit()
        logger.info(f"🗑️ Item eliminado: {item.name} (id={item_id})")
        return True


# ─── Búsqueda Global ─────────────────────────────────────

def buscar_biblioteca(
    q: Optional[str] = None,
    content_type: Optional[str] = None,
    cr_min: Optional[float] = None,
    cr_max: Optional[float] = None,
    tag: Optional[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """Búsqueda global en toda la biblioteca."""
    results: Dict[str, List[Dict[str, Any]]] = {}

    with get_session() as db:
        # Enemigos
        if not content_type or content_type == "enemies":
            stmt = select(LibraryEnemy).order_by(LibraryEnemy.name)
            if q:
                stmt = stmt.where(LibraryEnemy.name.contains(q))
            if tag:
                stmt = stmt.where(LibraryEnemy.tags.contains(tag))
            if cr_min is not None:
                stmt = stmt.where(LibraryEnemy.cr >= cr_min)
            if cr_max is not None:
                stmt = stmt.where(LibraryEnemy.cr <= cr_max)
            enemies = db.exec(stmt).all()
            results["enemies"] = [
                {"id": e.id, "name": e.name, "cr": e.cr, "hp": e.hp, "ac": e.ac,
                 "attack": e.attack, "damage": e.damage, "tags": e.tags,
                 "abilities": json.loads(e.abilities_json) if e.abilities_json else []}
                for e in enemies
            ]

        # NPCs
        if not content_type or content_type == "npcs":
            stmt = select(LibraryNPC).order_by(LibraryNPC.name)
            if q:
                stmt = stmt.where(LibraryNPC.name.contains(q))
            if tag:
                stmt = stmt.where(LibraryNPC.tags.contains(tag))
            npcs = db.exec(stmt).all()
            results["npcs"] = [
                {"id": n.id, "name": n.name, "race": n.race, "class_name": n.class_name,
                 "description": n.description, "personality": n.personality, "tags": n.tags,
                 "stats": json.loads(n.stats_json) if n.stats_json else {}}
                for n in npcs
            ]

        # Items
        if not content_type or content_type == "items":
            stmt = select(LibraryItem).order_by(LibraryItem.name)
            if q:
                stmt = stmt.where(LibraryItem.name.contains(q))
            if tag:
                stmt = stmt.where(LibraryItem.tags.contains(tag))
            items = db.exec(stmt).all()
            results["items"] = [
                {"id": i.id, "name": i.name, "item_type": i.item_type,
                 "rarity": i.rarity, "damage": i.damage, "properties": i.properties,
                 "description": i.description, "value_gp": i.value_gp, "tags": i.tags}
                for i in items
            ]

        # Encuentros
        if not content_type or content_type == "encounters":
            stmt = select(LibraryEncounter).order_by(LibraryEncounter.name)
            if q:
                stmt = stmt.where(LibraryEncounter.name.contains(q))
            if tag:
                stmt = stmt.where(LibraryEncounter.tags.contains(tag))
            encounters = db.exec(stmt).all()
            results["encounters"] = [
                {"id": enc.id, "name": enc.name, "description": enc.description,
                 "difficulty": enc.difficulty, "environment": enc.environment,
                 "loot": enc.loot, "tags": enc.tags,
                 "enemies": json.loads(enc.enemies_json) if enc.enemies_json else []}
                for enc in encounters
            ]

    return results
