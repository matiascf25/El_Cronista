import random
import urllib.parse
from typing import Dict, Any, List
from app.logger import setup_logger
from app.config import CLASES_DND
from app.components.dnd.dice import calcular_mod, formatear_modificador

logger = setup_logger("rules")

# Datos adicionales de D&D para personajes completos
RASGOS_PERSONALIDAD = [
    "Siempre tiene un plan para cada situación",
    "Nunca retrocede ante un desafío",
    "Colecciona historias y leyendas",
    "Desconfía de la magia arcana",
    "Protege a los inocentes sin dudarlo",
    "Busca gloria y reconocimiento",
    "Prefiere la diplomacia al combate",
    "Tiene un código de honor inquebrantable"
]

IDEALES = [
    "Honor: El deber está por encima de todo",
    "Libertad: Nadie debe vivir oprimido",
    "Conocimiento: El saber es poder",
    "Justicia: Los malvados deben pagar",
    "Familia: La lealtad a los cercanos es suprema",
    "Ambición: El poder debe ser alcanzado"
]

VINCULOS = [
    "Busca vengar la muerte de un ser querido",
    "Debe proteger un artefacto ancestral",
    "Tiene una deuda de honor con su mentor",
    "Busca redimirse de un error del pasado",
    "Protege su pueblo natal a toda costa",
    "Busca un artefacto perdido de su familia"
]

DEFECTOS = [
    "No puede resistirse a un misterio",
    "Desconfía de figuras de autoridad",
    "Tiene un vicio secreto (juego, alcohol)",
    "Es demasiado orgulloso para pedir ayuda",
    "Guarda rencor durante años",
    "Arriesga todo por la emoción"
]

IDIOMAS_DND = ["Común", "Élfico", "Enano", "Orco", "Gigante", "Dracónico", "Infernal", "Celestial", "Silvano"]

COMPETENCIAS_ARMADURAS = {
    "Bárbaro": ["Ligeras", "Medias", "Escudos"],
    "Bardo": ["Ligeras"],
    "Clérigo": ["Ligeras", "Medias", "Escudos"],
    "Druida": ["Ligeras", "Medias (no metálica)", "Escudos (no metálico)"],
    "Guerrero": ["Todas", "Escudos"],
    "Monje": ["Ninguna"],
    "Paladín": ["Todas", "Escudos"],
    "Explorador": ["Ligeras", "Medias", "Escudos"],
    "Pícaro": ["Ligeras"],
    "Hechicero": ["Ninguna"],
    "Brujo": ["Ligeras"],
    "Mago": ["Ninguna"]
}

COMPETENCIAS_ARMAS = {
    "Bárbaro": ["Simples", "Marciales"],
    "Bardo": ["Simples", "Ballestas de mano", "Espadas largas", "Estoques", "Espadas cortas"],
    "Clérigo": ["Simples"],
    "Druida": ["Garrotes", "Dagas", "Dardos", "Jabalinas", "Mazas", "Bastones", "Cimitarras", "Hoces", "Hondas", "Lanzas"],
    "Guerrero": ["Simples", "Marciales"],
    "Monje": ["Simples", "Espadas cortas"],
    "Paladín": ["Simples", "Marciales"],
    "Explorador": ["Simples", "Marciales"],
    "Pícaro": ["Simples", "Ballestas de mano", "Espadas largas", "Estoques", "Espadas cortas"],
    "Hechicero": ["Dagas", "Dardos", "Hondas", "Bastones", "Ballestas ligeras"],
    "Brujo": ["Simples"],
    "Mago": ["Dagas", "Dardos", "Hondas", "Bastones", "Ballestas ligeras"]
}

# Mapeo de habilidades a sus atributos base
HABILIDAD_A_ATRIBUTO = {
    "Acrobacias": "DES",
    "Aguante": "CON",
    "Arcanos": "INT",
    "Atletismo": "FUE",
    "Engaño": "CAR",
    "Historia": "INT",
    "Interpretación": "CAR",
    "Intimidación": "CAR",
    "Investigación": "INT",
    "Medicina": "SAB",
    "Naturaleza": "INT",
    "Percepción": "SAB",
    "Perspicacia": "SAB",
    "Persuasión": "CAR",
    "Religión": "INT",
    "Sigilo": "DES",
    "Supervivencia": "SAB",
    "Trato con Animales": "SAB"
}

# Hechizos por clase (D&D 5e SRD) — Trucos + Nivel 1-2
HECHIZOS_POR_CLASE = {
    "Bardo": [
        {"nombre": "Burla Vil", "nivel": 0, "desc": "1d4 psíquico, desventaja en ataque. Alcance 18m."},
        {"nombre": "Mano de Mago", "nivel": 0, "desc": "Creas una mano espectral. Alcance 9m."},
        {"nombre": "Palabra de Curación", "nivel": 1, "desc": "1d4+CAR HP a un aliado. Acción adicional."},
        {"nombre": "Sueño", "nivel": 1, "desc": "5d8 HP de criaturas caen dormidas."},
        {"nombre": "Disipar Magia", "nivel": 1, "desc": "Disipa un efecto mágico activo."},
        {"nombre": "Calor Metálico", "nivel": 2, "desc": "2d8 fuego a criatura con metal. Concentración."},
    ],
    "Clérigo": [
        {"nombre": "Llama Sagrada", "nivel": 0, "desc": "1d8 radiante. Salvación DES. Alcance 18m."},
        {"nombre": "Taumaturgia", "nivel": 0, "desc": "Manifestación divina menor (sonido, luz)."},
        {"nombre": "Curar Heridas", "nivel": 1, "desc": "1d8+SAB HP al tocar."},
        {"nombre": "Bendición", "nivel": 1, "desc": "3 aliados +1d4 a ataques y salvaciones."},
        {"nombre": "Escudo de Fe", "nivel": 1, "desc": "+2 AC. Concentración, 10 min."},
        {"nombre": "Arma Espiritual", "nivel": 2, "desc": "1d8+SAB fuerza. Acción adicional."},
        {"nombre": "Restaurar", "nivel": 2, "desc": "Cura enfermedad, veneno o condición."},
    ],
    "Druida": [
        {"nombre": "Producir Llama", "nivel": 0, "desc": "1d8 fuego. Luz 3m. Ataque a distancia."},
        {"nombre": "Druídica", "nivel": 0, "desc": "Creas un efecto natural menor."},
        {"nombre": "Enmarañar", "nivel": 1, "desc": "Área 6m: terreno difícil + restricción."},
        {"nombre": "Curar Heridas", "nivel": 1, "desc": "1d8+SAB HP al tocar."},
        {"nombre": "Forma Salvaje", "nivel": 0, "desc": "Te transformas en bestia CR 1/4 (2 usos)."},
        {"nombre": "Rayo Lunar", "nivel": 2, "desc": "2d10 radiante en columna 1.5m."},
    ],
    "Explorador": [
        {"nombre": "Marca del Cazador", "nivel": 1, "desc": "+1d6 daño a objetivo marcado. Concentración."},
        {"nombre": "Curar Heridas", "nivel": 1, "desc": "1d8+SAB HP al tocar."},
        {"nombre": "Detectar Magia", "nivel": 1, "desc": "Detectas auras mágicas en 9m. Ritual."},
    ],
    "Paladín": [
        {"nombre": "Castigo Divino", "nivel": 1, "desc": "+2d8 radiante al impactar cuerpo a cuerpo."},
        {"nombre": "Escudo de Fe", "nivel": 1, "desc": "+2 AC a aliado. Concentración, 10 min."},
        {"nombre": "Curar Heridas", "nivel": 1, "desc": "1d8+CAR HP al tocar."},
        {"nombre": "Detectar Mal y Bien", "nivel": 1, "desc": "Sabes dónde hay aberraciones, celestiales, etc."},
    ],
    "Hechicero": [
        {"nombre": "Rayo de Fuego", "nivel": 0, "desc": "1d10 fuego. Alcance 36m."},
        {"nombre": "Prestidigitación", "nivel": 0, "desc": "Efecto mágico menor (limpia, calienta, etc.)."},
        {"nombre": "Rayo de Escarcha", "nivel": 0, "desc": "1d8 frío. -3m velocidad. Alcance 18m."},
        {"nombre": "Armadura de Mago", "nivel": 1, "desc": "AC base 13+DES. 8 horas."},
        {"nombre": "Chaos Bolt", "nivel": 1, "desc": "2d8+1d6 daño aleatorio. Puede rebotar."},
        {"nombre": "Esfera Cromática", "nivel": 1, "desc": "3d8 daño de tipo elegido."},
        {"nombre": "Invisibilidad", "nivel": 2, "desc": "Invisible hasta atacar o lanzar hechizo."},
    ],
    "Brujo": [
        {"nombre": "Eldritch Blast", "nivel": 0, "desc": "1d10 fuerza. Alcance 36m."},
        {"nombre": "Prestidigitación", "nivel": 0, "desc": "Efecto mágico menor."},
        {"nombre": "Maleficio", "nivel": 1, "desc": "+1d6 necrosis al objetivo. Concentración."},
        {"nombre": "Armadura de Agathys", "nivel": 1, "desc": "+5 HP temp. 5 frío a quien te golpee."},
        {"nombre": "Paso Brumoso", "nivel": 2, "desc": "Teleportarte 9m. Acción adicional."},
    ],
    "Mago": [
        {"nombre": "Rayo de Fuego", "nivel": 0, "desc": "1d10 fuego. Alcance 36m."},
        {"nombre": "Prestidigitación", "nivel": 0, "desc": "Efecto mágico menor (limpia, calienta, etc.)."},
        {"nombre": "Mano de Mago", "nivel": 0, "desc": "Creas una mano espectral. Alcance 9m."},
        {"nombre": "Proyectil Mágico", "nivel": 1, "desc": "3 dardos × 1d4+1 fuerza. Impacto automático."},
        {"nombre": "Escudo", "nivel": 1, "desc": "Reacción: +5 AC hasta tu turno."},
        {"nombre": "Detectar Magia", "nivel": 1, "desc": "Detectas auras mágicas en 9m. Ritual."},
        {"nombre": "Telaraña", "nivel": 2, "desc": "Área 6m cubierta de telarañas. Restraint."},
        {"nombre": "Paso Brumoso", "nivel": 2, "desc": "Teleportarte 9m. Acción adicional."},
    ],
}

def sanitizar_pj(raw_pj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza y completa los datos de un personaje con información D&D completa
    
    Args:
        raw_pj: Datos crudos del personaje
    
    Returns:
        Personaje con TODOS los campos D&D necesarios
    """
    logger.info(f"Sanitizando personaje: {raw_pj.get('nombre', 'Sin nombre')}")
    
    try:
        from app.config import normalizar_clase

        # Pre-sanitización: Mapear stats inglés -> español si es necesario
        if 'stats' in raw_pj and isinstance(raw_pj['stats'], dict):
            stats_map = {
                "STR": "FUE", "DEX": "DES", "CON": "CON",
                "INT": "INT", "WIS": "SAB", "CHA": "CAR"
            }
            new_stats = {}
            for k, v in raw_pj['stats'].items():
                k_upper = k.upper()
                if k_upper in stats_map:
                    new_stats[stats_map[k_upper]] = v
                elif k_upper in ["FUE", "DES", "SAB", "CAR"]: # Ya en español
                    new_stats[k_upper] = v
            
            # Rellenar faltantes
            defaults = {"FUE": 10, "DES": 10, "CON": 10, "INT": 10, "SAB": 10, "CAR": 10}
            for k, v in defaults.items():
                if k not in new_stats:
                    new_stats[k] = v
            raw_pj['stats'] = new_stats

        # Normalizar clase usando el nuevo sistema
        clase_raw = raw_pj.get('clase', 'Guerrero')
        clase = normalizar_clase(clase_raw)
        
        if clase is None:
            # Solo loguear warning si realmente no se reconoce
            logger.warning(
                f"Clase '{clase_raw}' no reconocida en mapeo ni clases oficiales. "
                f"Usando 'Guerrero' por defecto. "
                f"Considera agregar '{clase_raw.lower()}' a MAPEO_CLASES en config.py"
            )
            clase = 'Guerrero'
        else:
            # Log success (debug level para no spam)
            if clase_raw != clase:
                logger.debug(f"Clase normalizada: '{clase_raw}' -> '{clase}'")
        
        raw_pj['clase'] = clase
        info = CLASES_DND[clase]
        
        # Nivel estricto (default 1)
        nivel = int(raw_pj.get('nivel', 1))
        raw_pj['nivel'] = nivel
        
        if 'stats' not in raw_pj or not isinstance(raw_pj['stats'], dict):
            logger.warning(f"Stats faltantes para {raw_pj.get('nombre')}, generando aleatorios")
            valores = [15, 14, 13, 12, 10, 8] # Standard Array fallback
            random.shuffle(valores)
            raw_pj['stats'] = {k: v for k, v in zip(["FUE","DES","CON","INT","SAB","CAR"], valores)}
        
        mods = {k: calcular_mod(v) for k, v in raw_pj['stats'].items()}
        raw_pj['modificadores'] = mods
        
        raw_pj['stats_display'] = {
            k: f"{v} ({formatear_modificador(mods[k])})" 
            for k, v in raw_pj['stats'].items()
        }
        
        # Bonus Competencia: ceil(nivel/4) + 1
        import math
        bonus_comp = math.ceil(nivel / 4.0) + 1
        raw_pj['bonus_competencia'] = bonus_comp
        
        # HP Calculation Strict: Base + (Level-1)*(Avg+Mod)
        con_mod = mods['CON']
        hit_die = info['HitDie']
        hp_base = hit_die + con_mod
        hp_level_up = (hit_die // 2 + 1 + con_mod) * (nivel - 1)
        raw_pj['hp'] = hp_base + hp_level_up
        raw_pj['hp_max'] = raw_pj['hp']
        raw_pj['dados_golpe'] = f"{nivel}d{hit_die}"
        
        raw_pj['ac'] = 10 + mods['DES']
        if clase in ["Guerrero", "Paladín"]:
            raw_pj['ac'] = 16
            raw_pj['ac_detalle'] = "16 (Cota de mallas)"
        elif clase == "Clérigo":
            raw_pj['ac'] = 14 + (2 if "Escudo" in str(raw_pj.get('equipo', [])) else 0)
            raw_pj['ac_detalle'] = f"{raw_pj['ac']} (Escamas + Escudo)"
        elif clase == "Bárbaro":
            raw_pj['ac'] = 10 + mods['DES'] + mods['CON']
            raw_pj['ac_detalle'] = f"{raw_pj['ac']} (Sin armadura: 10 + DES + CON)"
        elif clase == "Monje":
            raw_pj['ac'] = 10 + mods['DES'] + mods['SAB']
            raw_pj['ac_detalle'] = f"{raw_pj['ac']} (Sin armadura: 10 + DES + SAB)"
        else:
            raw_pj['ac_detalle'] = f"{raw_pj['ac']} (Armadura de cuero + DES)"
        
        raw_pj['velocidad'] = "9m (30 pies)" if raw_pj.get('raza', '').lower() != 'enano' else "7.5m (25 pies)"
        
        raw_pj['iniciativa'] = mods['DES']
        raw_pj['iniciativa_display'] = formatear_modificador(mods['DES'])
        
        # Habilidades: Mezclar base con las generadas por IA garantizando los rasgos CORE
        base_habs = info.get('Habs', [])
        generated_habs = raw_pj.get('habilidades', [])
        
        raw_pj['habilidades'] = base_habs.copy()
        nombres_base = {h['nombre'].lower() for h in base_habs}
        
        if isinstance(generated_habs, list):
            for h in generated_habs:
                if isinstance(h, str):
                    nombre_h = h
                    desc_h = "Rasgo adicional"
                elif isinstance(h, dict):
                    nombre_h = h.get('nombre', 'Rasgo Desconocido')
                    desc_h = h.get('desc', 'Rasgo adicional')
                else:
                    continue
                    
                if nombre_h.lower() not in nombres_base:
                    raw_pj['habilidades'].append({"nombre": nombre_h, "desc": desc_h})
                    nombres_base.add(nombre_h.lower())
        
        primary_stats = info.get('Primary', ['FUE', 'CON'])[:2]
        raw_pj['salvaciones_competentes'] = primary_stats
        
        raw_pj['salvaciones'] = {}
        for stat in ["FUE", "DES", "CON", "INT", "SAB", "CAR"]:
            es_competente = stat in primary_stats
            mod = mods[stat]
            valor = mod + (bonus_comp if es_competente else 0)
            
            raw_pj['salvaciones'][stat] = {
                "valor": valor,
                "display": formatear_modificador(valor),
                "competente": es_competente,
                "formula": f"{formatear_modificador(mod)} (mod)" + (f" {formatear_modificador(bonus_comp)} (comp)" if es_competente else "")
            }
        
        habilidades_clase = _seleccionar_habilidades_clase(clase)
        raw_pj['habilidades_competentes'] = habilidades_clase
        
        raw_pj['habilidades_valores'] = {}
        for hab, stat_base in HABILIDAD_A_ATRIBUTO.items():
            es_competente = hab in habilidades_clase
            mod = mods[stat_base]
            valor = mod + (bonus_comp if es_competente else 0)
            
            raw_pj['habilidades_valores'][hab] = {
                "valor": valor,
                "display": formatear_modificador(valor),
                "competente": es_competente,
                "stat_base": stat_base,
                "formula": f"{formatear_modificador(mod)} ({stat_base})" + (f" {formatear_modificador(bonus_comp)} (comp)" if es_competente else "")
            }
        
        raw_pj['competencias_armaduras'] = COMPETENCIAS_ARMADURAS.get(clase, ["Ninguna"])
        raw_pj['competencias_armas'] = COMPETENCIAS_ARMAS.get(clase, ["Simples"])
        
        num_idiomas = 2 + max(0, mods['INT'])
        idiomas_sample = random.sample(IDIOMAS_DND, min(num_idiomas, len(IDIOMAS_DND)))
        raw_pj['idiomas'] = idiomas_sample
        
        # ---------------------------------------------------------
        # SRD ENFORCEMENT: EQUIPO CANÓNICO
        # ---------------------------------------------------------
        if 'equipo' not in raw_pj or not raw_pj['equipo']:
            raw_pj['equipo'] = _generar_equipo_completo(clase, nivel)
        else:
            if len(raw_pj['equipo']) < 3:
                raw_pj['equipo'].extend(_generar_equipo_completo(clase, nivel)[:3])
                
        from app.components.dnd.database import db
        equipo_validado = []
        for eq in raw_pj['equipo']:
            eq_str = str(eq)
            eq_data = db.get_equipment(eq_str)
            if eq_data:
                detalles = ""
                if "damage" in eq_data:
                    dmg_dice = eq_data["damage"].get("damage_dice", "")
                    dmg_type = eq_data["damage"].get("damage_type", {}).get("name", "")
                    if dmg_dice: detalles += f" [{dmg_dice} {dmg_type}]"
                if "armor_class" in eq_data:
                    detalles += f" [AC: {eq_data['armor_class'].get('base', '')}]"
                equipo_validado.append(f"{eq_data['name']}{detalles}")
            else:
                equipo_validado.append(eq_str)
        raw_pj['equipo'] = equipo_validado
        
        # ---------------------------------------------------------
        # SRD ENFORCEMENT: HECHIZOS Y TRUCOS CANÓNICOS
        # ---------------------------------------------------------
        def _validar_lista_magia(lista_nombres):
            validados = []
            for h in lista_nombres:
                if not isinstance(h, str): continue
                spell_data = db.get_spell(h)
                if spell_data:
                    # Traer daño o efecto si existe
                    dmg = ""
                    if "damage" in spell_data and "damage_at_slot_level" in spell_data["damage"]:
                        try:
                            # Tomar el primer valor de daño disponible
                            dmg_val = list(spell_data['damage']['damage_at_slot_level'].values())[0]
                            dmg = f" ({dmg_val})"
                        except: pass
                    validados.append(f"{spell_data['name']}{dmg} [{spell_data.get('casting_time', '')}]")
                else:
                    validados.append(h)
            return validados
            
        hechizos_ia = raw_pj.get('hechizos', [])
        if not isinstance(hechizos_ia, list) or not hechizos_ia:
            hechizos_ia = HECHIZOS_POR_CLASE.get(clase, [])
        raw_pj['hechizos'] = _validar_lista_magia(hechizos_ia)
        
        trucos_ia = raw_pj.get('trucos', [])
        if not isinstance(trucos_ia, list): trucos_ia = []
        raw_pj['trucos'] = _validar_lista_magia(trucos_ia)
            
        # Rasgo de trasfondo
        if 'rasgo_trasfondo' not in raw_pj:
             raw_pj['rasgo_trasfondo'] = "Rasgo de personalidad único"
             
        # Las imágenes se inyectan asincrónicamente vía WebSockets cuando termina SDXL.
        # Desactivamos el "placeholder" estilo Bing para evitar flashazos de fotos de internet raras
        raw_pj['img'] = ""
        
        logger.info(f"✓ Personaje sanitizado: {raw_pj['nombre']} ({clase} Nv.{nivel}, HP:{raw_pj['hp']}, AC:{raw_pj['ac']})")
        
        return raw_pj
        
    except Exception as e:
        logger.error(f"Error crítico al sanitizar personaje: {e}", exc_info=True)
        return _personaje_emergencia_completo(raw_pj.get('nombre', 'PJ Genérico'))

def _generar_url_imagen_personaje(raza: str, clase: str, nombre: str) -> str:
    """Genera URL de imagen de personaje con estrategia optimizada por raza"""
    raza_clean = raza.strip()
    clase_clean = clase.strip()
    
    # ESTRATEGIA ESPECIAL PARA ENANOS
    if "enano" in raza_clean.lower() or "dwarf" in raza_clean.lower():
        logger.info(f"Usando estrategia especial de imagen para enano: {nombre}")
        
        queries_enano = [
            f"https://tse2.mm.bing.net/th?q={urllib.parse.quote('dnd dwarf warrior male portrait bearded face detailed fantasy art headshot')}&w=500&h=650&c=12&rs=1&p=0&dpr=2",
            f"https://tse1.mm.bing.net/th?q={urllib.parse.quote('fantasy dwarf fighter character portrait closeup beard')}&w=500&h=650&c=12&rs=1",
            f"https://tse3.mm.bing.net/th?q={urllib.parse.quote('dungeons dragons dwarf cleric face portrait beard armor')}&w=500&h=650&c=7&o=5&dpr=2&pid=1.7",
        ]
        
        index = hash(nombre) % len(queries_enano)
        return queries_enano[index]
    
    raza_keywords = {
        "Elfo": "elf elegant pointed ears fantasy",
        "Humano": "human adventurer warrior",
        "Mediano": "halfling small folk hobbit",
        "Orco": "half-orc strong tusks green",
        "Tiefling": "tiefling horns demonic tail",
        "Gnomo": "gnome small beard cheerful",
        "Dragonborn": "dragonborn dragon scales reptilian",
        "Semielfo": "half-elf elegant mixed heritage",
        "Serpiente": "yuan-ti snake humanoid scaled",
        "Medusa": "medusa snake hair gorgon"
    }
    
    clase_keywords = {
        "Guerrero": "fighter warrior armored plate mail",
        "Mago": "wizard mage robed spellcaster mystic",
        "Pícaro": "rogue thief hooded leather stealth",
        "Clérigo": "cleric priest holy religious armor",
        "Bárbaro": "barbarian berserker muscular tribal",
        "Bardo": "bard musician performer charismatic",
        "Druida": "druid nature wild shaman",
        "Monje": "monk martial artist robes disciplined",
        "Paladín": "paladin holy knight shining armor",
        "Explorador": "ranger hunter woodsman bow",
        "Hechicero": "sorcerer arcane magical energy",
        "Brujo": "warlock pact eldritch dark"
    }
    
    raza_key = raza_keywords.get(raza_clean, raza_clean.lower())
    clase_key = clase_keywords.get(clase_clean, clase_clean.lower())
    
    query_principal = f"dnd {raza_key} {clase_key} portrait character face centered detailed art headshot professional"
    
    queries = [
        f"https://tse2.mm.bing.net/th?q={urllib.parse.quote(query_principal)}&w=500&h=650&c=12&o=5&dpr=2&pid=1.7",
        f"https://tse1.mm.bing.net/th?q={urllib.parse.quote(f'{raza_clean} {clase_clean} fantasy portrait face closeup')}&w=450&h=600&c=7&rs=1&p=0",
        f"https://tse3.mm.bing.net/th?q={urllib.parse.quote(f'dnd character {raza_clean} {clase_clean} headshot detailed')}&w=500&h=650&c=12&o=5",
    ]
    
    index = hash(nombre) % len(queries)
    return queries[index]

def _seleccionar_habilidades_clase(clase: str) -> List[str]:
    """Selecciona 4 habilidades apropiadas para la clase"""
    habilidades_por_clase = {
        "Bárbaro": ["Atletismo", "Intimidación", "Percepción", "Supervivencia"],
        "Bardo": ["Interpretación", "Persuasión", "Engaño", "Arcanos"],
        "Clérigo": ["Perspicacia", "Religión", "Medicina", "Persuasión"],
        "Druida": ["Percepción", "Naturaleza", "Supervivencia", "Medicina"],
        "Guerrero": ["Atletismo", "Intimidación", "Percepción", "Supervivencia"],
        "Monje": ["Acrobacias", "Atletismo", "Sigilo", "Religión"],
        "Paladín": ["Atletismo", "Intimidación", "Persuasión", "Religión"],
        "Explorador": ["Atletismo", "Percepción", "Supervivencia", "Sigilo"],
        "Pícaro": ["Sigilo", "Acrobacias", "Engaño", "Percepción"],
        "Hechicero": ["Arcanos", "Engaño", "Persuasión", "Intimidación"],
        "Brujo": ["Arcanos", "Engaño", "Intimidación", "Investigación"],
        "Mago": ["Arcanos", "Historia", "Investigación", "Perspicacia"]
    }
    return habilidades_por_clase.get(clase, ["Atletismo", "Percepción", "Supervivencia", "Investigación"])

def _generar_equipo_completo(clase: str, nivel: int) -> List[str]:
    """Genera equipamiento completo y detallado basado en clase"""
    equipo_base = {
        "Bárbaro": ["Hacha de guerra grande (1d12)", "2 Hachas de mano (1d6)", "4 Jabalinas", "Mochila de explorador", "Pieles de animal"],
        "Bardo": ["Estoque (1d8)", "Armadura de cuero", "Daga (1d4)", "Laúd", "Mochila de artista", "Disfraz"],
        "Clérigo": ["Maza (1d6)", "Cota de escamas (AC 14)", "Escudo (+2 AC)", "Símbolo sagrado", "Libro de oraciones", "Mochila de sacerdote"],
        "Druida": ["Cimitarra (1d6)", "Armadura de cuero", "Escudo de madera", "Foco druídico", "Bolsa de hierbas", "Mochila de explorador"],
        "Guerrero": ["Espada larga (1d8/1d10)", "Cota de mallas (AC 16)", "Escudo (+2 AC)", "Ballesta ligera", "20 virotes", "Mochila"],
        "Monje": ["Espada corta (1d6)", "10 Dardos (1d4)", "Mochila de explorador", "Instrumentos artesanos"],
        "Paladín": ["Martillo de guerra (1d8)", "Cota de mallas (AC 16)", "Escudo (+2 AC)", "Símbolo sagrado", "Libro de oraciones", "5 Jabalinas"],
        "Explorador": ["Armadura de escamas (AC 14)", "2 Espadas cortas (1d6)", "Arco largo (1d8)", "Carcaj con 20 flechas", "Mochila de explorador"],
        "Pícaro": ["Estoque (1d8)", "Armadura de cuero tachonado (AC 12)", "Arco corto (1d6)", "Carcaj con 20 flechas", "Herramientas de ladrón", "Ganzúas"],
        "Hechicero": ["Ballesta ligera (1d8)", "Bolsa de componentes", "Foco arcano (cristal)", "2 Dagas (1d4)", "Mochila de erudito"],
        "Brujo": ["Armadura de cuero", "Ballesta ligera (1d8)", "Foco arcano (vara)", "Daga (1d4)", "Bolsa de componentes", "Grimorio"],
        "Mago": ["Bastón (1d6)", "Libro de conjuros", "Bolsa de componentes", "Foco arcano", "Túnica", "Mochila de erudito", "Tinta y pluma"]
    }
    
    equipo = equipo_base.get(clase, ["Equipo básico", "Mochila", "Cuerda (15m)", "Antorcha x10"])
    
    if nivel >= 3:
        equipo.append("Poción de curación (2d4+2 HP)")
    if nivel >= 5:
        equipo.append("50 pies de cuerda de seda")
        equipo.append("Ganchos de escalada")
    
    return equipo

def _generar_trasfondo_generico(clase: str, raza: str) -> str:
    """Genera un trasfondo genérico pero coherente"""
    trasfondos = {
        "Guerrero": f"Veterano de guerra {raza.lower()} que ha visto demasiadas batallas. Entrena diariamente para mantener sus habilidades.",
        "Mago": f"Erudito {raza.lower()} que pasó años estudiando en una torre arcana. Busca conocimientos perdidos.",
        "Pícaro": f"Antiguo ladrón {raza.lower()} de las calles que aprendió a sobrevivir con astucia y velocidad.",
        "Clérigo": f"Devoto {raza.lower()} que sirve a su deidad con fe inquebrantable. Busca llevar la luz a la oscuridad.",
        "Bárbaro": f"Guerrero tribal {raza.lower()} de las tierras salvajes. La civilización le resulta extraña.",
        "Bardo": f"Artista itinerante {raza.lower()} que recorre el mundo recopilando historias y leyendas.",
        "Druida": f"Guardián {raza.lower()} de la naturaleza que protege el equilibrio contra la civilización.",
        "Monje": f"Asceta {raza.lower()} entrenado en un monasterio remoto en las artes marciales y meditación.",
        "Paladín": f"Noble {raza.lower()} que juró un sagrado voto de proteger a los inocentes y destruir el mal.",
        "Explorador": f"Rastreador {raza.lower()} de las tierras salvajes, acostumbrado a la soledad y la supervivencia.",
        "Hechicero": f"Portador {raza.lower()} de magia innata que lucha por controlar el poder en su sangre.",
        "Brujo": f"Mortal {raza.lower()} que hizo un pacto con una entidad poderosa a cambio de poderes arcanos."
    }
    return trasfondos.get(clase, f"Aventurero {raza.lower()} con un pasado misterioso.")

def _calcular_oro_inicial(nivel: int) -> int:
    """Calcula oro inicial basado en nivel"""
    base = {1: 50, 2: 100, 3: 150, 4: 200, 5: 500}
    return base.get(nivel, nivel * 100)

def _personaje_emergencia_completo(nombre: str) -> Dict[str, Any]:
    """Genera un personaje de emergencia completo con todos los campos"""
    mods = {"FUE":3,"DES":1,"CON":2,"INT":0,"SAB":0,"CAR":-1}
    stats = {"FUE":16,"DES":12,"CON":14,"INT":10,"SAB":10,"CAR":8}
    
    return {
        "nombre": nombre,
        "raza": "Humano",
        "clase": "Guerrero",
        "nivel": 1,
        "stats": stats,
        "modificadores": mods,
        "stats_display": {k: f"{v} ({formatear_modificador(mods[k])})" for k, v in stats.items()},
        "hp": 30,
        "hp_max": 30,
        "ac": 16,
        "ac_detalle": "16 (Cota de mallas)",
        "velocidad": "9m (30 pies)",
        "iniciativa": 1,
        "iniciativa_display": "+1",
        "bonus_competencia": 2,
        "dados_golpe": "3d10",
        "salvaciones_competentes": ["FUE", "CON"],
        "salvaciones": {
            "FUE": {"valor": 5, "display": "+5", "competente": True, "formula": "+3 (mod) +2 (comp)"},
            "DES": {"valor": 1, "display": "+1", "competente": False, "formula": "+1 (mod)"},
            "CON": {"valor": 4, "display": "+4", "competente": True, "formula": "+2 (mod) +2 (comp)"},
            "INT": {"valor": 0, "display": "+0", "competente": False, "formula": "+0 (mod)"},
            "SAB": {"valor": 0, "display": "+0", "competente": False, "formula": "+0 (mod)"},
            "CAR": {"valor": -1, "display": "-1", "competente": False, "formula": "-1 (mod)"}
        },
        "habilidades_competentes": ["Atletismo", "Intimidación", "Percepción", "Supervivencia"],
        "habilidades_valores": {
            "Atletismo": {"valor": 5, "display": "+5", "competente": True, "stat_base": "FUE", "formula": "+3 (FUE) +2 (comp)"},
            "Percepción": {"valor": 2, "display": "+2", "competente": True, "stat_base": "SAB", "formula": "+0 (SAB) +2 (comp)"},
        },
        "competencias_armaduras": ["Todas", "Escudos"],
        "competencias_armas": ["Simples", "Marciales"],
        "idiomas": ["Común", "Orco"],
        "habilidades": [{"nombre":"Segundo Aliento", "desc":"1d10+3 HP"}, {"nombre":"Action Surge", "desc":"Acción extra"}],
        "equipo": ["Espada larga (1d8)", "Cota de mallas (AC 16)", "Escudo (+2 AC)", "Ballesta ligera", "Mochila"],
        "trasfondo": "Veterano de guerra que busca redención",
        "rasgo_personalidad": "Nunca retrocede ante un desafío",
        "ideal": "Honor: El deber está por encima de todo",
        "vinculo": "Protege a sus compañeros como familia",
        "defecto": "Es demasiado orgulloso para pedir ayuda",
        "oro": 150,
        "hechizos": [],
        "img": "https://tse2.mm.bing.net/th?q=dnd%20human%20fighter%20portrait%20face&w=500&h=650&c=12&dpr=2&pid=1.7"
    }
