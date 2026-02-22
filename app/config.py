import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración IA
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "mistral-nemo"
SAVE_DIR = "partidas_guardadas"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Configuración ComfyUI
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
COMFYUI_WOUT_OUTPUT = True  # Si es True, no espera a ver la imagen, solo dispara
COMFYUI_TIMEOUT = 120

# Prompts
SYSTEM_INSTRUCTIONS = """
ERES UN NOVELISTA DE FANTASÍA EXPERTO Y UN DUNGEON MASTER TEATRAL.
IDIOMA: SIEMPRE ESPAÑOL (Castellano neutro).
PERSPECTIVA: TERCERA PERSONA (Él/Ella/Ellos). NUNCA uses primera persona.
ESTILO: "MOSTRAR, NO CONTAR". Describe olores, luces, texturas.
REGLAS: Solo contenido oficial D&D 5e (SRD). PROHIBIDO inventar razas, clases o hechizos "homebrew".
ESTRUCTURA JSON: Tu respuesta debe ser puramente técnica (JSON válido).
"""

# Datos de Juego
CLASES_DND = {
    "Bárbaro": {"HitDie": 12, "Primary": ["FUE", "CON"], "Habs": [{"nombre":"Furia", "desc":"+2 daño/resis"}, {"nombre":"Defensa S.A.", "desc":"AC=10+DES+CON"}], "Gear": ["Gran Hacha", "2 Hachas de mano", "Paquete de explorador"]},
    "Bardo": {"HitDie": 8, "Primary": ["CAR", "DES"], "Habs": [{"nombre":"Inspiración", "desc":"1d6 a aliado"}, {"nombre":"Burla", "desc":"1d4 psíquico"}], "Gear": ["Estoque", "Instrumento", "Cuero", "Daga"]},
    "Clérigo": {"HitDie": 8, "Primary": ["SAB", "CON"], "Habs": [{"nombre":"Llama Sagrada", "desc":"1d8 radiante"}, {"nombre":"Curar", "desc":"1d8+Mod"}], "Gear": ["Maza", "Cota de escamas", "Símbolo", "Escudo"]},
    "Druida": {"HitDie": 8, "Primary": ["SAB", "CON"], "Habs": [{"nombre":"Forma Salvaje", "desc":"Bestia CR 1/4"}, {"nombre":"Enmarañar", "desc":"Area difícil"}], "Gear": ["Escudo madera", "Cimitarra", "Pieles", "Foco"]},
    "Guerrero": {"HitDie": 10, "Primary": ["FUE", "CON"], "Habs": [{"nombre":"Segundo Aliento", "desc":"1d10+Nvl HP"}, {"nombre":"Action Surge", "desc":"Acción extra"}], "Gear": ["Cota de malla", "Espadón", "Ballesta"]},
    "Monje": {"HitDie": 8, "Primary": ["DES", "SAB"], "Habs": [{"nombre":"Artes Marciales", "desc":"1d4 desarmado"}, {"nombre":"Defensa S.A.", "desc":"AC=10+DES+SAB"}], "Gear": ["Espada corta", "Dardos x10", "Paquete artista"]},
    "Paladín": {"HitDie": 10, "Primary": ["FUE", "CAR"], "Habs": [{"nombre":"Sentido Divino", "desc":"Detecta mal"}, {"nombre":"Lay on Hands", "desc":"Cura 15 HP"}], "Gear": ["Cota de malla", "Martillo", "Escudo", "Símbolo"]},
    "Explorador": {"HitDie": 10, "Primary": ["DES", "SAB"], "Habs": [{"nombre":"Marca Cazador", "desc":"+1d6 daño"}, {"nombre":"Explorador", "desc":"Ventaja rastreo"}], "Gear": ["Escamas", "2 Espadas cortas", "Arco largo"]},
    "Pícaro": {"HitDie": 8, "Primary": ["DES", "INT"], "Habs": [{"nombre":"Ataque Furtivo", "desc":"+2d6 daño"}, {"nombre":"Acción Astuta", "desc":"Dash/Hide bonus"}], "Gear": ["Cuero tachonado", "Estoque", "Arco corto", "Herramientas"]},
    "Hechicero": {"HitDie": 6, "Primary": ["CAR", "CON"], "Habs": [{"nombre":"Metamagia", "desc":"Modificar spell"}, {"nombre":"Chaos Bolt", "desc":"2d8+1d6 daño"}], "Gear": ["Ballesta", "Componentes", "Foco", "2 Dagas"]},
    "Brujo": {"HitDie": 8, "Primary": ["CAR", "CON"], "Habs": [{"nombre":"Eldritch Blast", "desc":"1d10 fuerza"}, {"nombre":"Pacto", "desc":"Recupera slots"}], "Gear": ["Cuero", "Ballesta", "Foco", "Daga"]},
    "Mago": {"HitDie": 6, "Primary": ["INT", "CON"], "Habs": [{"nombre":"Arcane Recovery", "desc":"Recarga slot"}, {"nombre":"Magic Missile", "desc":"3x 1d4+1"}], "Gear": ["Libro conjuros", "Componentes", "Bastón", "Túnica"]}
}

# ============================================
# MAPEO DE VARIACIONES DE CLASE
# ============================================

# Mapea variaciones comunes de nombres de clase a las clases oficiales D&D 5e
MAPEO_CLASES = {
    # Bárbaro
    "barbaro": "Bárbaro",
    "barbarian": "Bárbaro",
    "bárbara": "Bárbaro",
    "barbara": "Bárbaro",
    "berserker": "Bárbaro",
    
    # Bardo
    "bard": "Bardo",
    "barda": "Bardo",
    "juglar": "Bardo",
    "trovador": "Bardo",
    
    # Clérigo
    "clerigo": "Clérigo",
    "cleric": "Clérigo",
    "sacerdote": "Clérigo",
    "sacerdotisa": "Clérigo",
    "cura": "Clérigo",
    
    # Druida
    "druid": "Druida",
    "chamán": "Druida",
    "chaman": "Druida",
    "chamana": "Druida",
    
    # Guerrero
    "fighter": "Guerrero",
    "guerrera": "Guerrero",
    "luchador": "Guerrero",
    "luchadora": "Guerrero",
    "soldado": "Guerrero",
    "soldada": "Guerrero",
    
    # Monje
    "monk": "Monje",
    "monja": "Monje",
    
    # Paladín
    "paladin": "Paladín",
    "paladina": "Paladín",
    "caballero": "Paladín",
    "caballera": "Paladín",
    
    # Explorador (Ranger)
    "ranger": "Explorador",
    "exploradora": "Explorador",
    "cazador": "Explorador",  # ← FIX para tu warning
    "cazadora": "Explorador",
    "montaraz": "Explorador",
    "rastreador": "Explorador",
    "rastreadora": "Explorador",
    
    # Pícaro (Rogue)
    "rogue": "Pícaro",
    "picaro": "Pícaro",
    "pícara": "Pícaro",
    "picara": "Pícaro",
    "ladrón": "Pícaro",
    "ladrona": "Pícaro",
    "asesino": "Pícaro",
    "asesina": "Pícaro",
    
    # Hechicero
    "sorcerer": "Hechicero",
    "hechicera": "Hechicero",
    "mago de sangre": "Hechicero",
    "maga de sangre": "Hechicero",
    
    # Brujo
    "warlock": "Brujo",
    "bruja": "Brujo",
    "pactista": "Brujo",
    
    # Mago
    "wizard": "Mago",
    "maga": "Mago",  # ← FIX para tu warning
    "arcanista": "Mago",
    "hechicero arcano": "Mago",
    "hechicera arcana": "Mago",
}

def normalizar_clase(clase_raw: str) -> str:
    """
    Normaliza el nombre de una clase a su versión oficial D&D 5e.
    
    Args:
        clase_raw: Nombre de clase posiblemente variado
    
    Returns:
        Nombre oficial de clase o None si no se reconoce
    
    Examples:
        >>> normalizar_clase("Cazador")
        "Explorador"
        >>> normalizar_clase("maga")
        "Mago"
        >>> normalizar_clase("Fighter")
        "Guerrero"
    """
    if not clase_raw:
        return None
    
    # Normalizar: lowercase, sin acentos variables
    clase_lower = clase_raw.strip().lower()
    
    # Buscar en mapeo directo
    if clase_lower in MAPEO_CLASES:
        return MAPEO_CLASES[clase_lower]
    
    # Buscar en clases oficiales (case-insensitive)
    for clase_oficial in CLASES_DND.keys():
        if clase_oficial.lower() == clase_lower:
            return clase_oficial
    
    # No encontrada
    return None

ESTILOS = [
    {"nombre": "HORROR GÓTICO", "desc": "Terror victoriano, niebla, sangre.", "track_amb": "h2dJ-JUzhVs", "track_cbt": "6Joyj0dmkug"},
    {"nombre": "ALTA FANTASÍA", "desc": "Épica, dragones, luz vs oscuridad.", "track_amb": "bpOSxM0rNPM", "track_cbt": "sUIckV8Ea2E"},
    {"nombre": "MISTERIO NOIR", "desc": "Lluvia, corrupción, detectives.", "track_amb": "jX6kn9_U8qk", "track_cbt": "cH_rfGBwamc"},
    {"nombre": "PIRATAS", "desc": "Caribe, barcos fantasma, tormentas.", "track_amb": "QFxN2oDKk0E", "track_cbt": "nJ-bIeJ4zOY"},
    {"nombre": "STEAMPUNK", "desc": "Vapor, bronce, dirigibles.", "track_amb": "D75ZuaSR8nQ", "track_cbt": "jVhlJNJopOQ"},
    {"nombre": "CIENCIA FANTASÍA", "desc": "Ruinas alienígenas, magia perdida.", "track_amb": "UEavYXMjbgI", "track_cbt": "zW8FjoJ6MIc"},
    {"nombre": "EDAD PRIMIGENIA", "desc": "Bestias, chamanes, supervivencia.", "track_amb": "kXF3VYYa5TI", "track_cbt": "xNN7iTA57jM"},
    {"nombre": "CIBERPUNK", "desc": "Neón, lluvia ácida, alta tecnología.", "track_amb": "m_8QkXj8qj8", "track_cbt": "y2GEqLeTkLw"},
    {"nombre": "VIEJO OESTE", "desc": "Desierto, duelos al sol, cantinas.", "track_amb": "30YrJI1oUUk", "track_cbt": "vnf25WJ3jGk"},
    {"nombre": "BOSQUE FEÉRICO", "desc": "Hadas, naturaleza vibrante, engaños.", "track_amb": "xT3k5kI7lqA", "track_cbt": "pWb4_jJk3gQ"},
    {"nombre": "POST-APOCALIPSIS", "desc": "Yermos, radiación, chatarra.", "track_amb": "bLg5l3QzG_w", "track_cbt": "Q5d7g8h9j0k"},
    {"nombre": "TERROR CÓSMICO", "desc": "Locura, vacío, dioses antiguos.", "track_amb": "NoJ-g7Q3h2s", "track_cbt": "9wXk2mN5oPq"}
]

MICRO_SETTINGS = [
    "unas islas flotantes unidas por cadenas oxidadas sobre un abismo sin fin",
    "una ciudad construida dentro del cráneo de un titán muerto hace eones",
    "el Underdark, iluminado solo por hongos bioluminiscentes que susurran",
    "una torre infinita donde cada piso es un ecosistema distinto",
    "un bosque de cristal que vibra con una canción que vuelve loca a la gente"
]

PERSONAJES_EMERGENCIA = {
    "personajes": [
        {"nombre": "Thorgrim", "raza": "Enano", "clase": "Guerrero", "nivel": 1, "stats": {"FUE":16,"DES":12,"CON":15,"INT":10,"SAB":11,"CAR": 8}, "trasfondo": "Guardia veterano desgraciado", "motivacion": "Recuperar su honor", "secreto": "Se durmió durante una guardia crítica", "vinculo": "Siente que debe proteger a Elara como a una hija"},
        {"nombre": "Elara", "raza": "Elfa", "clase": "Mago", "nivel": 1, "stats": {"FUE": 8,"DES":14,"CON":12,"INT":16,"SAB":13,"CAR":10}, "trasfondo": "Aprendiz que huyó de su torre", "motivacion": "Descubrir magia prohibida", "secreto": "Robó un grimorio de su maestro", "vinculo": "Thorgrim le recuerda a su difunto padre"}
    ]
}
