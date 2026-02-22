import random
import re
from typing import Dict, Any, List
from app.logger import setup_logger

logger = setup_logger("dice")

def evaluar_formula_dados(formula: str) -> Dict[str, Any]:
    """Evalúa una fórmula de dados tipo D&D"""
    logger.info(f"Evaluando dados: {formula}")
    
    try:
        f = formula.lower().replace(' ', '')
        match = re.match(r'(\d*)d(\d+)([\+\-]\d+)?', f)
        
        if not match:
            logger.warning(f"Fórmula inválida: {formula}")
            return {"error": True, "mensaje": "Formato inválido. Usa: XdY+Z"}
        
        n = int(match.group(1) or 1)
        sides = int(match.group(2))
        mod = int(match.group(3) or 0)
        
        if n > 100 or sides > 1000:
            logger.warning(f"Fórmula excesiva: {n}d{sides}")
            return {"error": True, "mensaje": "Máximo: 100d1000"}
        
        rolls = [random.randint(1, sides) for _ in range(n)]
        total = sum(rolls) + mod
        
        explicacion = f"{rolls} {'+' if mod >= 0 else ''}{mod if mod != 0 else ''}"
        
        logger.info(f"✓ Resultado: {total} ({explicacion})")
        
        return {
            "resultado": total,
            "explicacion": explicacion.strip(),
            "formula": formula,
            "error": False,
            "rolls": rolls,
            "modificador": mod
        }
        
    except Exception as e:
        logger.error(f"Error al evaluar dados '{formula}': {e}")
        return {"error": True, "mensaje": str(e)}

def calcular_mod(valor: int) -> int:
    """Calcula el modificador de D&D desde un valor de atributo"""
    try:
        mod = (valor - 10) // 2
        logger.debug(f"Modificador calculado: {valor} -> {mod:+d}")
        return mod
    except Exception as e:
        logger.error(f"Error al calcular modificador para valor {valor}: {e}")
        return 0

def formatear_modificador(mod: int) -> str:
    """Formatea un modificador con signo: +3 o -1"""
    return f"{mod:+d}" if mod != 0 else "+0"
