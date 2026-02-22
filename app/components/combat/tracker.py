import random
import re
from typing import List, Dict, Any
from app.logger import setup_logger

logger_combat = setup_logger("combat")

class CombatTracker:
    """Sistema de seguimiento de combate"""
    
    def __init__(self):
        self.active_combats: Dict[str, Dict[str, Any]] = {}
        logger_combat.info("CombatTracker inicializado")
    
    def start_combat(
        self,
        session_id: str,
        enemigos: List[Dict],
        pjs: List[Dict]
    ) -> Dict[str, Any]:
        """
        Inicia un nuevo combate
        
        Args:
            session_id: ID de la sesión
            enemigos: Lista de grupos de enemigos
            pjs: Lista de personajes jugadores
        
        Returns:
            Estado inicial del combate
        """
        logger_combat.info(f"⚔️ Iniciando combate - Sesión: {session_id}")
        logger_combat.info(f"PJs: {len(pjs)}, Grupos enemigos: {len(enemigos)}")
        
        combatientes = []
        
        # Procesar PJs
        for pj in pjs:
            try:
                init = random.randint(1, 20) + pj.get('iniciativa', 0)
                combatientes.append({
                    "nombre": pj['nombre'],
                    "tipo": "pj",
                    "iniciativa": init,
                    "hp_actual": pj.get('hp', 20),
                    "hp_max": pj.get('hp_max', 20),
                    "ac": pj.get('ac', 10),
                    "condiciones": []
                })
                logger_combat.debug(f"PJ agregado: {pj['nombre']} (Ini: {init})")
                
            except KeyError as e:
                logger_combat.error(f"PJ con datos incompletos: {e}")
                continue
        
        # Procesar Enemigos
        for en in enemigos:
            try:
                cantidad = self._parse_cantidad(en.get('cantidad', '1'))
                
                for i in range(cantidad):
                    init = random.randint(1, 20)
                    name = en['nombre'] if cantidad == 1 else f"{en['nombre']} {i+1}"
                    hp = int(en.get('hp', 10))
                    
                    combatientes.append({
                        "nombre": name,
                        "tipo": "enemigo",
                        "iniciativa": init,
                        "hp_actual": hp,
                        "hp_max": hp,
                        "ac": en.get('ac', 10),
                        "condiciones": [],
                        "ataque": en.get('ataque', '+0'),
                        "dano": en.get('dano', '1d4')
                    })
                    logger_combat.debug(f"Enemigo agregado: {name} (HP: {hp}, AC: {en.get('ac', 10)})")
                    
            except Exception as e:
                logger_combat.error(f"Error procesando enemigo {en.get('nombre', 'Unknown')}: {e}")
                continue
        
        # Ordenar por iniciativa
        combatientes.sort(key=lambda x: x['iniciativa'], reverse=True)
        
        self.active_combats[session_id] = {
            "activo": True,
            "turno_actual": 0,
            "ronda": 1,
            "combatientes": combatientes,
            "log": ["Inicio de combate"]
        }
        
        logger_combat.info(f"✓ Combate iniciado con {len(combatientes)} combatientes")
        logger_combat.info(f"Orden de iniciativa: {[c['nombre'] for c in combatientes]}")
        
        return self.active_combats[session_id]
    
    def _parse_cantidad(self, cantidad_str: str) -> int:
        """Parsea cantidad de enemigos (puede ser número o fórmula de dados)"""
        try:
            # Si es un número directo
            return int(cantidad_str)
        except ValueError:
            # Si es una fórmula de dados simple (1d4, 2d6, etc)
            match = re.match(r'(\d+)d(\d+)', str(cantidad_str).lower())
            if match:
                n_dice = int(match.group(1))
                sides = int(match.group(2))
                result = sum(random.randint(1, sides) for _ in range(n_dice))
                logger_combat.debug(f"Cantidad parseada: {cantidad_str} = {result}")
                return result
            
            logger_combat.warning(f"Cantidad inválida '{cantidad_str}', usando 1")
            return 1

    def next_turn(self, session_id: str) -> Dict[str, Any]:
        """Avanza al siguiente turno"""
        if session_id not in self.active_combats:
            logger_combat.warning(f"next_turn llamado sin combate activo en {session_id}")
            return {}
        
        c = self.active_combats[session_id]
        c["turno_actual"] = (c["turno_actual"] + 1) % len(c["combatientes"])
        
        if c["turno_actual"] == 0:
            c["ronda"] += 1
            c["log"].append(f"Ronda {c['ronda']}")
            logger_combat.info(f"Nueva ronda: {c['ronda']}")
        
        current = c["combatientes"][c["turno_actual"]]
        logger_combat.info(f"Turno de: {current['nombre']} (Ini: {current['iniciativa']})")
        
        return c

    def add_combatant(self, session_id: str, enemigo: Dict) -> Dict[str, Any]:
        """Agrega un combatiente a un combate ya activo."""
        if session_id not in self.active_combats:
            logger_combat.warning(f"add_combatant llamado sin combate activo en {session_id}")
            return {}
        
        c = self.active_combats[session_id]
        init = random.randint(1, 20)
        name = enemigo.get('nombre', 'Desconocido')
        hp = int(enemigo.get('hp', 10))
        
        # Evitar duplicados exactos en nombres
        base_name = name
        count = 1
        while any(x['nombre'] == name for x in c['combatientes']):
            count += 1
            name = f"{base_name} {count}"

        nuevo = {
            "nombre": name,
            "tipo": "enemigo",
            "iniciativa": init,
            "hp_actual": hp,
            "hp_max": hp,
            "ac": enemigo.get('ac', 10),
            "condiciones": [],
            "ataque": enemigo.get('ataque', '+0'),
            "dano": enemigo.get('dano', '1d4')
        }
        
        c["combatientes"].append(nuevo)
        c["combatientes"].sort(key=lambda x: x['iniciativa'], reverse=True)
        c["log"].append(f"⚔️ {name} se une al combate (Iniciativa: {init})")
        
        logger_combat.info(f"Combatiente agregado a combate activo: {name} (Ini: {init})")
        return c

    def apply_damage(self, session_id: str, target: str, amount: int) -> Dict[str, Any]:
        """Aplica daño a un combatiente"""
        if session_id not in self.active_combats:
            logger_combat.warning(f"apply_damage llamado sin combate activo")
            return {}
        
        c = self.active_combats[session_id]
        
        for comb in c["combatientes"]:
            if comb["nombre"] == target:
                old_hp = comb["hp_actual"]
                comb["hp_actual"] = max(0, comb["hp_actual"] - amount)
                
                msg = f"{target} recibe {amount} daño ({old_hp} → {comb['hp_actual']} HP)"
                c["log"].append(msg)
                
                logger_combat.info(msg)
                
                if comb["hp_actual"] == 0:
                    logger_combat.warning(f"💀 {target} ha caído (0 HP)")
                
                break
        else:
            logger_combat.warning(f"Objetivo no encontrado: {target}")
        
        return c
    
    def heal(self, session_id: str, target: str, amount: int) -> Dict[str, Any]:
        """Cura a un combatiente"""
        if session_id not in self.active_combats:
            logger_combat.warning(f"heal llamado sin combate activo")
            return {}
        
        c = self.active_combats[session_id]
        
        for comb in c["combatientes"]:
            if comb["nombre"] == target:
                old_hp = comb["hp_actual"]
                comb["hp_actual"] = min(comb["hp_max"], comb["hp_actual"] + amount)
                
                actual_healing = comb["hp_actual"] - old_hp
                
                msg = f"{target} recupera {actual_healing} HP ({old_hp} → {comb['hp_actual']} HP)"
                c["log"].append(msg)
                
                logger_combat.info(msg)
                break
        else:
            logger_combat.warning(f"Objetivo no encontrado: {target}")
        
        return c

    def end_combat(self, session_id: str) -> Dict[str, Any]:
        """Finaliza el combate activo"""
        if session_id in self.active_combats:
            combat_data = self.active_combats[session_id]
            rounds = combat_data.get('ronda', 0)
            
            logger_combat.info(f"⚔️ Combate finalizado - Duración: {rounds} rondas")
            
            del self.active_combats[session_id]
        else:
            logger_combat.warning(f"end_combat llamado sin combate activo")
        
        return {"activo": False}

    def get_state(self, session_id: str) -> Dict[str, Any]:
        """Obtiene el estado actual del combate"""
        state = self.active_combats.get(session_id, {"activo": False})
        
        if state.get("activo"):
            logger_combat.debug(
                f"Estado combate {session_id}: "
                f"Ronda {state.get('ronda')}, "
                f"Turno {state.get('turno_actual') + 1}/{len(state.get('combatientes', []))}"
            )
        
        return state
