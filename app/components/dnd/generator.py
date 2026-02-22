from typing import Dict, Any, List
from app.logger import setup_logger
from app.config import PERSONAJES_EMERGENCIA
from app.components.dnd.rules import sanitizar_pj
from app.components.ai.client import generar_con_ia
from app.components.story.narrator import _generar_historia, _agregar_imagenes, _generar_esquema_aventura, _expandir_escena

logger = setup_logger("generator")

from app.state import image_skill
# Diccionario de Keywords Raciales para ComfyUI
RACIAL_PROMPTS = {
    "humano": "human, versatile features, determined expression",
    "human": "human, versatile features, determined expression",
    "elfo": "elf, pointed ears, angular features, high cheekbones, elegant, ethereal",
    "elf": "elf, pointed ears, angular features, high cheekbones, elegant, ethereal",
    "enano": "dwarf, stocky build, thick beard (if male), heavy brow, weathered skin, sturdy",
    "dwarf": "dwarf, stocky build, thick beard (if male), heavy brow, weathered skin, sturdy",
    "mediano": "halfling, small stature, cheerful, round face, curly hair, nimble",
    "halfling": "halfling, small stature, cheerful, round face, curly hair, nimble",
    "orco": "orc, green skin, tusks, muscular, tribal scars, fierce",
    "mid-orc": "half-orc, tusks, strong jaw, muscular, greyish skin",
    "semiorco": "half-orc, tusks, strong jaw, muscular, greyish skin",
    "tiefling": "tiefling, horns, tail, red or purple skin, demonic heritage, glowing eyes",
    "gnomo": "gnome, small, large eyes, expressive, wild hair, eccentric",
    "draconido": "dragonborn, scales, dragon head, snout, reptilian eyes",
    "dragonborn": "dragonborn, scales, dragon head, snout, reptilian eyes",
}

async def crear_datos_aventura(session_id: str, setting: str, estilo: Dict[str, str], nivel: int = 1, background_tasks=None, connection_manager=None) -> Dict[str, Any]:
    """Genera una aventura completa con personajes e historia en cascada (Async + WS Streaming)"""
    logger.info(f"🎲 Iniciando generación de aventura en cascada (Nivel {nivel})")
    
    # Helper para enviar updates
    async def send_update(msg: str, progress: int):
        if connection_manager:
            await connection_manager.send_to_session(
                session_id,
                {"type": "loading_progress", "message": msg, "progress": progress}
            )
    
    await send_update("Generando personajes...", 10)
    
    # 1. PERSONAJES
    logger.info("Paso 1/3: Generando personajes...")
    # Ejecutamos generación de PJs (síncrona)
    pjs = _generar_personajes(setting, nivel)
    logger.info(f"✓ {len(pjs)} personajes generados")
    
    await send_update(f"Personajes generados. Creando trama...", 30)
    
    # 2. ESQUEMA DE HISTORIA
    logger.info("Paso 2/3: Generando esquema de historia...")
    esquema = _generar_esquema_aventura(setting, estilo, pjs, nivel)
    
    if not esquema:
        logger.warning("Fallo generando esquema, usando método legacy")
        historia = _generar_historia(setting, estilo, pjs, nivel)
        await send_update("Historia generada (modo legacy)...", 90)
    else:
        logger.info(f"✓ Esquema generado: {esquema['titulo']}")
        await send_update(f"Esquema: {esquema['titulo']}. Expandiendo escenas...", 40)
        
        historia = {
            "titulo": esquema['titulo'],
            "sinopsis": esquema['sinopsis'],
            "plot_twist": esquema['plot_twist'],
            "escenas": []
        }
        
        # 3. EXPANSIÓN DE ESCENAS (CASCADA)
        resumen_acumulado = f"Sinopsis: {esquema['sinopsis']}. "
        
        for i in range(1, 6):
            logger.info(f"  > Expandiendo Escena {i}/5...")
            await send_update(f"Escribiendo Escena {i}/5...", 40 + (i * 10))
            
            # Ejecutar expansión (síncrona, puede bloquear un poco, idealmente envolver en threadpool si es muy lento)
            escena = _expandir_escena(esquema, resumen_acumulado, nivel, i, pjs)
            
            if escena:
                # INTEGRACIÓN SRD: Reemplazar stats locas de la IA por matemáticas canónicas
                try:
                    from app.components.dnd.database import db
                    if 'enemigos' in escena and isinstance(escena['enemigos'], list):
                        for enemigo in escena['enemigos']:
                            nombre = enemigo.get('nombre', '')
                            srd_data = db.get_monster(nombre)
                            if srd_data:
                                logger.info(f"🦇 Inyectando stats hardcore SRD para {nombre} -> {srd_data['name']}")
                                enemigo['nombre'] = srd_data['name'] # Nombre oficial
                                enemigo['hp'] = srd_data.get('hit_points', enemigo.get('hp'))
                                enemigo['ac'] = srd_data.get('armor_class', enemigo.get('ac'))
                                
                                # Extraer ataques para UI
                                acciones = srd_data.get('actions', [])
                                if acciones:
                                    ataques = []
                                    danos = []
                                    for act in acciones[:2]:
                                        ataque_str = f"+{act.get('attack_bonus', 0)} ({act.get('name', '')})"
                                        ataques.append(ataque_str)
                                        # Resumir el texto de daño
                                        desc = act.get('desc', '')
                                        # Buscar la palabra 'Hit:' o 'Impacto:'
                                        if 'Hit:' in desc:
                                            desc = desc.split('Hit:')[1].strip()
                                        danos.append(desc)
                                    
                                    enemigo['ataque'] = " / ".join(ataques)
                                    enemigo['dano'] = " | ".join(danos)
                                    enemigo['srd_matcheado'] = True
                                    
                    # INTEGRACIÓN SRD: Validar botín
                    if 'botin' in escena and isinstance(escena['botin'], list):
                        botin_validado = []
                        for item in escena['botin']:
                            if not isinstance(item, str): continue
                            eq_data = db.get_equipment(item)
                            if eq_data:
                                # Agregar stats al texto del botín si es un arma o armadura
                                detalles = ""
                                if "damage" in eq_data:
                                    dmg_dice = eq_data["damage"].get("damage_dice", "")
                                    dmg_type = eq_data["damage"].get("damage_type", {}).get("name", "")
                                    if dmg_dice: detalles += f" [{dmg_dice} {dmg_type}]"
                                if "armor_class" in eq_data:
                                    detalles += f" [AC: {eq_data['armor_class'].get('base', '')}]"
                                botin_validado.append(f"{eq_data['name']}{detalles}")
                            else:
                                botin_validado.append(item)
                        escena['botin'] = botin_validado
                        
                except Exception as e:
                    logger.error(f"Error inyectando SRD en generador: {e}")

                historia['escenas'].append(escena)
                resumen_acumulado += f"Escena {i}: {escena.get('narrativa', '')[:200]}... "
            else:
                logger.error(f"Fallo generando Escena {i}")
    
    # Check si algo falló catastroficamente
    if not historia.get('escenas'):
        logger.error("No se generaron escenas válidas, usando fallback completo")
        historia = _generar_historia(setting, estilo, pjs, nivel)

    logger.info(f"✓ Historia completada con {len(historia.get('escenas', []))} escenas")
    await send_update("Finalizando detalles y magia...", 95)
    
    # 4. IMÁGENES
    logger.info("Paso 3/3: Disparando generación de imágenes...")
    if background_tasks:
        # Mapas combinados
        for idx, escena in enumerate(historia.get("escenas", [])):
            if "narrativa" in escena:
                background_tasks.add_task(
                    image_skill.process_narrative, 
                    escena["narrativa"], 
                    session_id,
                    escena.get("visual_prompt"),
                    idx
                )
        # Retratos de PJs via ComfyUI
        for idx, pj in enumerate(pjs):
            raza = pj.get('raza', 'human')
            clase = pj.get('clase', 'warrior')
            # nombre = pj.get('nombre', 'Adventurer') # Unused var
            genero = pj.get('genero', 'neutral') 
            
            portrait_prompt = _generate_portrait_prompt(raza, clase, genero, pj.get('descripcion_fisica', ''))
            
            background_tasks.add_task(
                image_skill.generate_portrait,
                portrait_prompt,
                session_id,
                pj_index=idx
            )
            
    logger.info("✓ Tareas de imagen encoladas")
    await send_update("¡Aventura lista!", 100)
    
    logger.info("🎉 Aventura generada exitosamente")
    return {"pjs": pjs, "historia": historia}

def _generate_portrait_prompt(raza: str, clase: str, genero: str, extra_desc: str) -> str:
    """Genera un prompt optimizado para ComfyUI basado en raza y clase"""
    raza_lower = raza.lower()
    
    # Buscar keywords raciales (Búsqueda parcial)
    racial_keywords = ""
    for k, v in RACIAL_PROMPTS.items():
        if k in raza_lower:
            racial_keywords = v
            break
    
    if not racial_keywords:
        racial_keywords = f"{raza}, distinctive features"

    # Base style
    style = "cinematic lighting, fantasy portrait, high detail, intricate armor, dnd style, digital art, 8k, masterpiece"
    
    return f"{racial_keywords}, {clase}, {genero}, {extra_desc}, {style}"

def _generar_personajes(setting: str, nivel: int) -> list:
    """Genera lista de personajes para la aventura"""
    from app.config import CLASES_DND
    
    # Get exact class names
    clases_validas = ", ".join(CLASES_DND.keys())

    prompt = f"""Genera 4 PJs de NIVEL {nivel} para: {setting}. IDIOMA: ESPAÑOL.
    
    CLASES VÁLIDAS (USA EXACTAMENTE ESTOS NOMBRES):
    {clases_validas}
    
    REGLA 0 (CRÍTICA): El campo "clase" DEBE ser exactamente uno de: {clases_validas}
    NO uses variaciones como "Cazador", "Maga", "Fighter" - usa SOLO los nombres listados arriba.

    REGLA 1 (Stats): Usa 'Standard Array' (15, 14, 13, 12, 10, 8) distribuidos según la clase.
    REGLA 2 (HP): Calcula HP = (Dado de Golpe + Mod CON) * {nivel}.
    REGLA 3 (Mecánicas): Incluye Transfondo oficial (ej: Acólito), Hechizos (si aplica) y Rasgos por nivel.

    JSON: {{ "personajes": [ {{ 
        "nombre": "Nombre", 
        "raza": "Raza (SRD)", 
        "clase": "Clase (SRD)",
        "genero": "Masculino/Femenino/Neutro", 
        "nivel": {nivel},
        "stats": {{ "STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10 }},
        "hp_max": 10,
        "bonus_competencia": 2,
        "trasfondo": "Acólito (u otro oficial)",
        "rasgo_trasfondo": "Nombre del rasgo de trasfondo",
        "motivacion": "Hook", 
        "secreto": "Secret",
        "vinculo": "Relación con el PJ N",
        "habilidades": ["Rasgo Nvl 1", "Rasgo Nvl {nivel}"],
        "trucos": ["Solo si usa magia"],
        "hechizos": ["Nivel 1: ...", "Nivel 2: ... (si aplica)"],
        "descripcion_fisica": "Breve descripción visual (pelo, ojos, piel)"
    }} ] }}
    
    IMPORTANTE: Asegura que al menos 2 PJs tengan un vínculo compartido en el campo 'vinculo'."""
    
    data_pjs = generar_con_ia(prompt, use_cache=True)
    
    if not data_pjs or 'personajes' not in data_pjs:
        logger.warning("Fallo generación de PJs, usando personajes de emergencia")
        data_pjs = PERSONAJES_EMERGENCIA
    
    raw_pjs = data_pjs.get('personajes', [])
    for p in raw_pjs:
        p['nivel'] = nivel
        
    pjs_finales = [sanitizar_pj(p) for p in raw_pjs]
    
    if not pjs_finales:
        logger.error("No se pudieron generar PJs, usando fallback completo")
        pjs_finales = [sanitizar_pj(p) for p in PERSONAJES_EMERGENCIA['personajes']]
    
    return pjs_finales
