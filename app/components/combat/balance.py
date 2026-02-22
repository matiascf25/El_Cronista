from typing import List, Dict, Any
import math
from app.logger import setup_logger

logger = setup_logger("balance")

# Tabla simplificada de XP por CR para cálculos
CR_XP_TABLE = {
    "0": 10, "1/8": 25, "1/4": 50, "1/2": 100,
    "1": 200, "2": 450, "3": 700, "4": 1100, "5": 1800,
    "6": 2300, "7": 2900, "8": 3900, "9": 5000, "10": 5900
}

# Tabla simplificada de XP Thresholds por Nivel de Personaje (Easy, Medium, Hard, Deadly)
LEVEL_XP_THRESHOLDS = {
    1: [25, 50, 75, 100],
    2: [50, 100, 150, 200],
    3: [75, 150, 225, 400],
    4: [125, 250, 375, 500],
    5: [250, 500, 750, 1100],
    # ... se puede extender
}

def calculate_party_thresholds(pjs: List[Dict]) -> List[int]:
    """Calcula los umbrales de XP total para el grupo (Easy, Medium, Hard, Deadly)"""
    totals = [0, 0, 0, 0]
    for pj in pjs:
        # Asumimos nivel 3 si no está definido, o inferimos por HP/Stats
        # Para simplificar este prototipo, usaremos nivel 3 por defecto
        level = pj.get("nivel", 3)
        thresholds = LEVEL_XP_THRESHOLDS.get(level, LEVEL_XP_THRESHOLDS[5])
        
        for i in range(4):
            totals[i] += thresholds[i]
            
    return totals

def estimate_cr(stats: Dict) -> float:
    """Estima el CR de un enemigo basado en HP y Daño promedio (simplificado)"""
    hp = stats.get("hp", 10)
    # Parsear daño (ej: "1d8+2")
    # Simplificación muy grosera:
    damage_str = str(stats.get("dano", "1d6"))
    
    # CR basado en HP (Regla de dedo: HP/15 aprox)
    cr_hp = hp / 15.0
    
    return max(0.125, cr_hp)

def adjust_encounter(enemigos: List[Dict], pjs: List[Dict]) -> List[Dict]:
    """
    Evalúa y ajusta un encuentro para que no sea Deadly+.
    Si es demasiado difícil, reduce HP/Daño.
    """
    if not pjs or not enemigos:
        return enemigos
        
    thresholds = calculate_party_thresholds(pjs)
    deadly_threshold = thresholds[3]
    
    # Calcular XP total del encuentro (aprox)
    total_xp = 0
    multiplier = 1.0
    num_enemies = sum(int(e.get("cantidad", 1)) if isinstance(e.get("cantidad"), int) else 1 for e in enemigos) # Simplificado parsing cantidad
    
    if num_enemies == 2: multiplier = 1.5
    elif num_enemies >= 3 and num_enemies <= 6: multiplier = 2.0
    elif num_enemies >= 7: multiplier = 2.5
    
    friendlies = []
    
    for e in enemigos:
        # Intentar determinar CR
        cr = e.get("cr_estimado", estimate_cr(e))
        e["cr_estimado"] = cr # Guardar para ref
        
        # Buscar XP
        cr_key = str(int(cr))
        if cr == 0.125: cr_key = "1/8"
        elif cr == 0.25: cr_key = "1/4"
        elif cr == 0.5: cr_key = "1/2"
        
        xp = CR_XP_TABLE.get(cr_key, 100) # Fallback
        
        qty = int(e.get("cantidad", 1)) if isinstance(e.get("cantidad"), int) else 1
        # Nota: Si cantidad es string "1d4", aquí fallará o será 1. 
        # Idealmente el generador ya debería haber resuelto esto, pero por seguridad usamos 1 si no es int.
        
        total_xp += xp * qty

    adjusted_xp = total_xp * multiplier
    
    logger.info(f"⚖️ Balanceo: XP Encuentro {int(adjusted_xp)} vs Deadly Threshold {deadly_threshold}")
    
    if adjusted_xp > deadly_threshold:
        logger.warning("⚠️ Encuentro DEADLY detectado. Aplicando nerfeo.")
        factor = deadly_threshold / adjusted_xp
        # No reducir a menos del 50% para no trivializar
        factor = max(0.5, factor)
        
        for e in enemigos:
            original_hp = e.get("hp", 10)
            e["hp"] = int(original_hp * factor)
            e["dano_original"] = e.get("dano")
            e["nota_balance"] = "Nerfeado por sistema de balance"
            logger.info(f"   -> {e['nombre']}: HP {original_hp} -> {e['hp']}")
            
    return enemigos
