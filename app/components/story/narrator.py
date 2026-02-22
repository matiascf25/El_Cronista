import urllib.parse
from typing import Dict, Any, List, Optional
from app.logger import setup_logger
from app.components.ai.client import generar_con_ia

logger = setup_logger("narrator")

def _generar_esquema_aventura(setting: str, estilo: Dict[str, str], pjs: list, nivel: int) -> Optional[Dict[str, Any]]:
    """Genera el esquema maestro de la aventura (Título, Sinopsis, 5 Actos)"""
    nombres = ", ".join([f"{p['nombre']} ({p['clase']})" for p in pjs])
    
    prompt = f"""Eres un DUNGEON MASTER EXPERTO diseñando el esquema de una aventura de D&D 5e.
MUNDO: {setting}
ESTILO: {estilo.get('desc', 'Fantasía heroica')}
PERSONAJES (Nivel {nivel}): {nombres}

OBJETIVO: Crea la ESTRUCTURA de una aventura de 5 ESCENAS (5 Actos).
NO generes diálogos ni textos largos, solo el ESQUELETO.

JSON REQUERIDO (ESPAÑOL):
{{
  "titulo": "Título de la aventura",
  "sinopsis": "Resumen general del conflicto (2-3 líneas)",
  "hook_principal": "Motivo por el que el grupo es contratado o involucrado",
  "esquema_escenas": [
    {{ "id": 1, "titulo": "Nombre Escena 1", "resumen": "Qué pasa aquí (1-2 líneas). Introducción." }},
    {{ "id": 2, "titulo": "Nombre Escena 2", "resumen": "Desarrollo/Viaje/Investigación." }},
    {{ "id": 3, "titulo": "Nombre Escena 3", "resumen": "Giro/Complicación/Dungeon." }},
    {{ "id": 4, "titulo": "Nombre Escena 4", "resumen": "Clímax previo/Revelación." }},
    {{ "id": 5, "titulo": "Nombre Escena 5", "resumen": "Confrontación Final y Resolución." }}
  ],
  "plot_twist": "Revelación final inesperada"
}}"""

    esquema = generar_con_ia(prompt, use_cache=True)
    if not esquema or 'esquema_escenas' not in esquema:
        logger.error("Fallo generando esquema, usando fallback")
        return None # El orquestador manejará el fallback
    return esquema

def _expandir_escena(esquema: Dict, resumen_previo: str, nivel: int, numero_escena: int, pjs: list) -> Optional[Dict[str, Any]]:
    """Genera el contenido detallado de una escena específica siguiendo el esquema"""
    escena_target = next((e for e in esquema['esquema_escenas'] if e['id'] == numero_escena), None)
    if not escena_target:
        return None

    nombres_pjs = ", ".join([p['nombre'] for p in pjs])
    
    prompt = f"""Eres un DUNGEON MASTER y ESCRITOR DE FANTASÍA EXPERTO.
CONTEXTO: Aventura "{esquema['titulo']}".
RESUMEN PREVIO: {resumen_previo}
ESCENA ACTUAL ({numero_escena}/5): "{escena_target['titulo']}" - {escena_target['resumen']}
NIVEL DEL GRUPO: {nivel} (CRÍTICO para balance)

OBJETIVO: Generar el contenido JSON detallado para la Escena {numero_escena}.

REGLAS DE GENERACIÓN:
1. NARRATIVA: Español, 3ra persona, sensorial (olores, luces, sonidos).
2. VISUAL PROMPT: INGLÉS. Keywords técnicas para ComfyUI (e.g. "cinematic lighting, 8k, detailed texture").
3. MECÁNICAS D&D 5e (CRÍTICO - REGLAS MATEMÁTICAS ESTRICTAS):
   - GENERAR SIEMPRE 1-3 ENEMIGOS en el campo "enemigos".
   - Sus stats DEBEN estar balanceados EXACTAMENTE para PJs de Nivel {nivel}. Un enemigo para este nivel suele tener aprox. {(nivel * 10) + 5} HP y AC {12 + (nivel//2)}.
   - El daño del enemigo debe escalar: ej. '1d6 + {nivel//2}' a NV 1, y '3d8 + {nivel}' a NV Alto.
   - GENERAR SIEMPRE 1-2 NPCs en el campo "npcs".
   - CDs de habilidad: Fácil=10, Media=15, Difícil={15 + nivel//2}.
   - El BOTÍN (loot) DEBE ser apropiado para Nivel {nivel}. Oro abundante y magia a nivel alto; miseria a nivel 1.
4. AMBIENTE AUDIO: Describe el paisaje sonoro.

JSON REQUERIDO (NO DEVOLVER MARDOWN, SOLO JSON PURO):
{{
  "id": {numero_escena},
  "nombre": "{escena_target['titulo']}",
  "narrativa": "Texto literario en español...",
  "visual_prompt": "ENGLISH visual description...",
  "ambiente_audio": "Sonidos de fondo...",
  "enemigos": [
      {{ "nombre": "Goblin Jefe", "hp": 20, "ac": 15, "ataque": "+4", "dano": "1d6+2", "tactica": "Ataca a distancia" }}
  ],
  "npcs": [ {{ "nombre": "Aldeano Asustado", "rol": "Víctima", "frase_entrada": "¡Ayuda por favor!" }} ],
  "interacciones": [
      {{ "accion": "Investigar huellas", "cd": 12, "exito": "Encuentras rastro", "fallo": "Pierdes tiempo" }}
  ],
  "botin": ["10 po", "Daga oxidada"],
  "transicion": "Pista a la siguiente escena"
}}"""

    return generar_con_ia(prompt, use_cache=True)

def _generar_historia(setting: str, estilo: Dict[str, str], pjs: list, nivel: int) -> Dict[str, Any]:
    """Genera la estructura dramática de la aventura Nivel {nivel}"""
    nombres = ", ".join([p['nombre'] for p in pjs])
    
    prompt = f"""Eres un DUNGEON MASTER EXPERTO escribiendo una aventura de D&D 5e.
MUNDO: {setting}
ESTILO: {estilo['desc']}
PERSONAJES (Nivel {nivel}): {nombres}

OBJETIVO: Crea una aventura NARRATIVAMENTE RICA en 5 ESCENAS conectadas para un grupo de NIVEL {nivel}.

REQUISITOS DE BALANCE (CRÍTICO Y MATEMÁTICO):
1. ENCUENTROS: Balanceados para 4 PJs de Nivel {nivel}. 
2. DIFICULTAD (CD): Escala las pruebas de habilidad: Fácil=10, Media=15, Difícil={15 + (nivel // 2)}.
3. ESTADÍSTICAS DEL ENEMIGO: Deben ser matemáticamente correctas para Nivel {nivel}. HP sugerido: {(nivel * 10) + 5}. AC sugerido: {12 + (nivel//2)}. Justifica ataque/daño. Ej: "Ataque +{(nivel // 2) + 2}".
4. BOTÍN: Escala rígidamente la riqueza y rareza de objetos mágicos al Nivel {nivel}.

REQUISITOS NARRATIVOS:
1. Usa DETALLES SENSORIALES: olores, sonidos, texturas, luz
2. TERCERA PERSONA siempre: "Los aventureros ven..." NO "Ves..."
3. Estilo LITERARIO: como novelista de fantasía, no como manual
4. CONEXIONES: cada escena menciona la siguiente

JSON REQUERIDO (ESPAÑOL, EXCEPTO visual_prompt):
{{
  "titulo": "Título épico",
  "sinopsis": "Resumen del conflicto",
  "escenas": [
    {{
      "id": 1,
      "nombre": "Nombre del lugar",
      "narrativa": "Descripción DETALLADA y SENSORIAL...",
      "visual_prompt": "DESCRIPTION IN ENGLISH...",
      "ambiente_audio": "Descripción sonora...",
      "enemigos": [ 
          {{ "nombre": "Goblin", "hp": 7, "ac": 15, "ataque": "+4 (Cimitarra)", "dano": "1d6+2", "justificacion": "DES +2, Comp +2" }}
      ],
      "npcs": [ {{
          "nombre": "Nombre completo del NPC",
          "rol": "Su función en la historia",
          "personalidad": "Descripción rica: manierismos, forma de hablar, motivaciones. 2-3 líneas.",
          "frase_entrada": "Primera línea de diálogo memorable que dice al grupo"
        }}
      ],
      "interacciones": [
          "accion": "Qué pueden hacer los PJs",
          "exito": "Qué descubren o consiguen si tienen éxito",
          "fallo": "Qué pasa si fallan (IMPORTANTE: agrega este campo)"
        }}
      ],
      "botin": ["Item 1 (con descripción breve)", "Item 2", "Item 3"],
      "hook_personaje": "Cómo conecta esta escena con la clase de uno de los PJs (Ej: 'El clérigo siente...')",
      "transicion": "Pista o evento que lleva a la siguiente escena. Ejemplo: 'Entre los escombros encuentran un mapa...'"
    }}
  ],
  "plot_twist": {{
    "titulo": "El Giro Final",
    "descripcion": "Revelación inesperada de 2-3 líneas que cambia la perspectiva de la aventura"
  }}
}}

IMPORTANTE: 
- 5 escenas COMPLETAS (no 3)
- VISUAL_PROMPT SIEMPRE EN INGLÉS con keywords técnicas
- AMBIENTE_AUDIO en cada escena
- Enemigos balanceados para Nivel 1
- SIEMPRE en ESPAÑOL (salvo visual_prompt) y TERCERA PERSONA"""
    
    historia = generar_con_ia(prompt)
    
    if not historia or 'escenas' not in historia or len(historia.get('escenas', [])) < 5:
        logger.warning("Fallo generación de historia o menos de 5 escenas, usando historia enriquecida fallback")
        return _historia_fallback_enriquecida()
    
    if 'plot_twist' not in historia:
        logger.warning("Historia generada sin plot_twist, agregando uno genérico")
        historia['plot_twist'] = {
            "titulo": "Revelación Inesperada",
            "descripcion": "Las apariencias engañan. Lo que parecía un simple encargo esconde un propósito mucho más oscuro..."
        }
    
    return historia

def _historia_fallback_enriquecida() -> Dict:
    """
    Historia de emergencia ENRIQUECIDA con 5 escenas narrativamente ricas
    """
    logger.info("Usando historia fallback ENRIQUECIDA (5 escenas)")
    return {
        "titulo": "El Secreto de las Ruinas de Sombraluna",
        "sinopsis": "Un misterioso patrón contrata a los aventureros para recuperar un artefacto de unas ruinas antiguas. Pero las ruinas esconden secretos que algunos preferirían mantener enterrados para siempre.",
        
        "escenas": [
            {
                "id": 1,
                "nombre": "La Taberna del Cuervo Sangriento",
                "narrativa": "El humo de las pipas de hierbas forma espirales perezosas bajo las vigas ennegrecidas de la taberna. El olor a cerveza agria y carne asada se mezcla con el murmullo constante de conversaciones susurradas. En un rincón oscuro, una figura encapuchada hace señas a los aventureros. Sus manos, pálidas como la cera, contrastan con el cuero negro de sus guantes mientras desliza una bolsa de monedas sobre la mesa manchada de vino. La luz de las velas baila en su rostro oculto, revelando apenas una sonrisa que no llega a sus ojos.",
                "visual_prompt": "cinematic lighting, top-down view, highly detailed fantasy art, dark medieval tavern interior, smoky atmosphere, mysterious cloaked figure in corner, candlelight, 8k, unreal engine 5 render style",
                "ambiente_audio": "Murmullo de taberna, choque de jarras, fuego crepitando, viento aullando fuera",
                "enemigos": [],
                "npcs": [
                    {
                        "nombre": "Gerick el Encapuchado",
                        "rol": "Contratante misterioso",
                        "personalidad": "Habla con voz suave y medida, nunca alza la mirada directamente. Juguetea nerviosamente con un medallón de plata que lleva al cuello. Parece saber más de lo que dice, y sus ojos se desvían cada vez que alguien menciona las ruinas. Oculta una desesperación apenas contenida.",
                        "frase_entrada": "He esperado mucho tiempo por aventureros con vuestra... particular reputación. Las Ruinas de Sombraluna guardan algo que me pertenece, y pagaré generosamente por su retorno."
                    }
                ],
                "interacciones": [
                    {
                        "accion": "Negociar el pago (Persuasión CD 13)",
                        "exito": "Gerick acepta pagar 100 po ahora y 500 po al completar la misión",
                        "fallo": "Se ofrece solo 50 po adelantadas y 300 al completar"
                    },
                    {
                        "accion": "Investigar a Gerick (Perspicacia CD 15)",
                        "exito": "Notan que el medallón que lleva tiene el mismo símbolo que aparece en el mapa de las ruinas. Está mintiendo sobre algo.",
                        "fallo": "Parece un cliente más, aunque nervioso"
                    },
                    {
                        "accion": "Preguntar a otros parroquianos sobre las ruinas (Investigación CD 12)",
                        "exito": "Un viejo marinero menciona que 'quien entra en Sombraluna cambia... si es que sale'. Habla de luces extrañas y voces en la niebla.",
                        "fallo": "La gente evita el tema y cambia de conversación rápidamente"
                    }
                ],
                "botin": [
                    "Adelanto en oro (50-100 po según negociación)",
                    "Mapa detallado de las ruinas con símbolos arcanos",
                    "Frasco de aceite bendito (regalo del tabernero supersticioso)"
                ],
                "hook_personaje": "El símbolo en el medallón de Gerick coincide con uno que el mago del grupo vio en sus estudios, relacionado con un culto prohibido hace siglos.",
                "transicion": "El mapa señala que las ruinas están a un día de viaje al norte, en los Páramos Desolados. Gerick insiste en que deben partir antes del amanecer, cuando 'las defensas están más débiles'."
            },
            
            {
                "id": 2,
                "nombre": "Los Páramos Desolados",
                "narrativa": "La niebla se extiende como un manto gris sobre la tierra yerma. El viento aúlla entre las rocas puntiagudas que emergen del suelo como dientes rotos. No hay vegetación, solo líquenes negros que se aferran a las piedras. El aire huele a azufre y a algo dulzón y podrido. A lo lejos, siluetas retorcidas que podrían ser árboles muertos... o algo peor. El camino marcado en el mapa serpentea entre formaciones rocosas, y cada paso resuena con un eco antinatural. Entonces, desde la niebla, emergen figuras humanoides de piel verdosa.",
                "visual_prompt": "cinematic lighting, top-down view, highly detailed fantasy art, desolate wasteland, thick fog, twisted jagged rocks, dead trees, goblin ambush emerging from mist, 8k, gloomy atmosphere",
                "ambiente_audio": "Viento silbante constante, graznidos lejanos, pasos crujiendo en tierra seca",
                "enemigos": [
                    {
                        "nombre": "Saqueadores Goblins",
                        "cantidad": "2d4",
                        "ac": 13,
                        "hp": 7,
                        "ataque": "+4",
                        "dano": "1d6+2",
                        "tactica": "Atacan desde las rocas con arcos cortos, gritando en su lengua gutural. Si hieren a alguien, se vuelven más audaces y cargan en manada. Si mueren dos, los demás huyen chillando. Uno lleva un cuerno para pedir refuerzos."
                    }
                ],
                "npcs": [],
                "interacciones": [
                    {
                        "accion": "Intimidar a los goblins (Intimidación CD 13)",
                        "exito": "Huyen aterrorizados, dejando caer parte de su botín robado",
                        "fallo": "Atacan con renovada ferocidad (+2 a daño durante 1 ronda)"
                    },
                    {
                        "accion": "Rastrear el origen de los goblins (Supervivencia CD 14)",
                        "exito": "Descubren que vienen de un campamento cerca de las ruinas. Algo los ha alterado recientemente.",
                        "fallo": "Las huellas se pierden en el terreno rocoso"
                    },
                    {
                        "accion": "Examinar el terreno (Percepción CD 13)",
                        "exito": "Notan que la niebla fluye en una dirección específica, como si algo la atrajera hacia las ruinas",
                        "fallo": "La niebla los desorienta, alargando el viaje 2 horas"
                    }
                ],
                "botin": [
                    "Flechas goblins (1d6+2 recuperables)",
                    "Amuleto tosco con el símbolo de Sombraluna (¡el mismo del mapa!)",
                    "Pedazo de pergamino antiguo con escritura élfica borrada"
                ],
                "hook_personaje": "El explorador nota que estas tierras fueron fértiles hace mucho tiempo. Algo las corrompió. En su juventud, su mentor le habló de una maldición...",
                "transicion": "Al caer la tarde, las ruinas emergen de la niebla: torres derruidas que se recortan contra el cielo morado del ocaso. Los muros están cubiertos de símbolos que brillan débilmente. Una entrada abierta exhala aire frío y húmedo."
            },
            
            {
                "id": 3,
                "nombre": "La Antecámara Olvidada",
                "narrativa": "La entrada conduce a una sala circular de piedra negra pulida que refleja la luz de las antorchas como agua oscura. El techo se pierde en las sombras, pero algo se mueve allá arriba: aleteos susurrantes y chillidos agudos. Las paredes están grabadas con frescos que representan figuras encapuchadas adorando a una luna llena teñida de rojo. En el centro de la sala, un altar de obsidiana sostiene un libro abierto. Las páginas se mueven solas, volteándose sin viento. El olor a incienso antiguo y a algo muerto hace mucho tiempo impregna el aire. Entonces, una voz incorpórea susurra en élfico antiguo: 'Los que buscan deben demostrar su valía...'",
                "visual_prompt": "cinematic lighting, top-down view, highly detailed fantasy art, ancient stone dungeon chamber, obsidian altar, glowing red runes, shadows, bats on ceiling, 8k, eerie atmosphere",
                "ambiente_audio": "Goteo de agua, aleteo de murciélagos, susurros ininteligibles, eco profundo",
                "enemigos": [
                    {
                        "nombre": "Espectros Guardianes",
                        "cantidad": "1d3",
                        "ac": 12,
                        "hp": 22,
                        "ataque": "+4",
                        "dano": "3d6 necrótico",
                        "tactica": "Emergen de las paredes cuando alguien toca el altar. Se mueven atravesando objetos sólidos. Gimen nombres de los vivos, intentando drenar su esencia vital. Vulnerables a ataques radiantes o de energía positiva. Si el libro es cerrado con un ritual apropiado, se disipan."
                    }
                ],
                "npcs": [
                    {
                        "nombre": "Eco del Guardián Élfico",
                        "rol": "Protección mágica antigua",
                        "personalidad": "No es realmente consciente, es un eco de memoria. Repite frases de advertencia: 'La luna sangra cuando los dignos fracasan', 'Tres llaves abren, tres secretos sellan'. Su voz resuena directamente en las mentes de quienes tienen afinidad arcana.",
                        "frase_entrada": "Pasad la prueba de conocimiento o uniros a quienes ya guardan estas estancias... eternamente."
                    }
                ],
                "interacciones": [
                    {
                        "accion": "Leer el libro del altar (Arcanos CD 15)",
                        "exito": "Es un grimorio de rituales lunares. Revela que las ruinas fueron un templo dedicado a Selûne que fue corrompido. Se necesitan tres llaves para acceder a la cripta inferior.",
                        "fallo": "Una descarga arcana inflige 2d6 de daño psíquico y causa visiones perturbadoras"
                    },
                    {
                        "accion": "Descifrar los frescos (Historia CD 14)",
                        "exito": "Los frescos cuentan la historia de un sumo sacerdote que traicionó a su diosa, invocando algo oscuro de 'más allá de las estrellas'. La traición ocurrió durante un eclipse.",
                        "fallo": "Los símbolos son demasiado antiguos para interpretarlos"
                    },
                    {
                        "accion": "Negociar con el Eco (Religión CD 16 o Persuasión CD 18)",
                        "exito": "El Eco reconoce que los aventureros no sirven a la oscuridad y revela un pasadizo oculto que evita una trampa mortal más adelante",
                        "fallo": "El Eco invoca más espectros"
                    }
                ],
                "botin": [
                    "Grimorio lunar (contiene 2 hechizos de adivinación)",
                    "Primera Llave: Símbolo de plata en forma de media luna",
                    "Polvo de huesos antiguos (componente de hechizo valioso)",
                    "Relicario élfico (vale 150 po para un coleccionista)"
                ],
                "hook_personaje": "El clérigo siente una conexión con el lugar. Su deidad susurra advertencias: 'Este lugar clama por redención'. Ganar experiencia inspiradora si consagra el altar.",
                "transicion": "El pasadizo oculto (o el principal, si no lo encontraron) desciende en una espiral hacia las profundidades. El aire se vuelve más frío. Grabados en las paredes muestran una cuenta regresiva lunar. Faltan tres días para... ¿un eclipse?"
            },
            
            {
                "id": 4,
                "nombre": "Los Túneles Susurrantes",
                "narrativa": "Los túneles se estrechan, obligando al grupo a agacharse. Las paredes de piedra transpiran una humedad fría que huele a tumba. Raíces retorcidas cuelgan del techo como tentáculos, y de ellas gotea una sustancia luminiscente verde que ilumina débilmente el camino. Los susurros están en todas partes ahora, un murmullo constante de voces que hablan en lenguas muertas. Las palabras son casi comprensibles, casi... y entonces, de las sombras, emerge una criatura humanoide cubierta de líquenes brillantes, con ojos vacíos que brillan con hambre antinatural. No está sola.",
                "visual_prompt": "cinematic lighting, top-down view, highly detailed fantasy art, narrow claustrophobic tunnels, glowing green lichen, roots varying form ceiling, undead guardians in shadows, 8k, horror atmosphere",
                "ambiente_audio": "Susurros constantes pan-direccionales, respiración agitada, goteo viscoso",
                "enemigos": [
                    {
                        "nombre": "Servidores Corrompidos",
                        "cantidad": "1d4+1",
                        "ac": 14,
                        "hp": 30,
                        "ataque": "+5",
                        "dano": "1d8+3 cortante + CD 12 CON o envenenado",
                        "tactica": "Fueron sacerdotes que cayeron con el templo. Atacan en silencio absoluto, moviéndose con coordinación antinatural. Intentan separar al grupo arrastrando víctimas a túneles laterales. Su toque marchita plantas y contamina agua. Vulnerables a fuego sagrado."
                    },
                    {
                        "nombre": "Enjambre de Murciélagos Corrompidos",
                        "cantidad": "1",
                        "ac": 12,
                        "hp": 22,
                        "ataque": "+4",
                        "dano": "2d4 perforante + ceguera temporal (CD 11 CON)",
                        "tactica": "Emergen del techo cuando se perturba el silencio. Atacan en masa, apagando fuentes de luz y desorientando. Se dispersan si se usa trueno o fuego en área."
                    }
                ],
                "npcs": [
                    {
                        "nombre": "Fantasma de Elara la Redentora",
                        "rol": "Sacerdotisa caída que busca expiación",
                        "personalidad": "Aparece como una joven elfa translúcida de ojos tristes. Habla con voz etérea y melancólica. Intentó detener la traición del sumo sacerdote pero falló. Ahora está atada a las ruinas. Se muestra más sustancial cerca de objetos consagrados a Selûne. Busca desesperadamente la redención.",
                        "frase_entrada": "Finalmente... alguien que puede escucharme. Hace tanto... Por favor, deben detenerlo antes del eclipse. Él despertará a lo que duerme abajo."
                    }
                ],
                "interacciones": [
                    {
                        "accion": "Hablar con Elara (Perspicacia CD 13 para ganar su confianza)",
                        "exito": "Revela que Gerick es descendiente del sumo sacerdote traidor y busca completar el ritual interrumpido hace siglos. La Segunda Llave está en su tumba. Señala la entrada oculta.",
                        "fallo": "Elara desaparece, sobrepasada por el dolor de sus recuerdos"
                    },
                    {
                        "accion": "Seguir los túneles susurrantes (Percepción CD 15)",
                        "exito": "Llevan a una cámara secreta con murales que explican el ritual oscuro. Ganar ventaja en el enfrentamiento final.",
                        "fallo": "Se pierden 30 minutos en un laberinto de túneles que vuelven al inicio"
                    },
                    {
                        "accion": "Purificar el área con magia divina (Religión CD 14)",
                        "exito": "Elara recupera fuerza suficiente para manifestarse físicamente y ayudar en un combate futuro",
                        "fallo": "La energía divina perturba el equilibrio, atrayendo más no-muertos"
                    }
                ],
                "botin": [
                    "Segunda Llave: Frasco con lágrimas de luna (líquido plateado luminoso)",
                    "Anillo de resistencia al veneno (en el dedo de un servidor caído)",
                    "Mapa etéreo que muestra el verdadero diseño de las ruinas",
                    "Diario de Elara (cuenta la verdadera historia de la traición)"
                ],
                "hook_personaje": "El bardo siente que la historia de Elara es una balada épica esperando ser contada. Si la ayudan a redimirse, ganará inspiración para componer 'La Balada de la Redentora de Sombraluna'.",
                "transicion": "Al fondo del túnel, una puerta sellada con tres cerraduras en forma de luna. Tres llaves. Dos ya están en posesión del grupo. Pero detrás de la puerta, se escuchan pasos. Alguien llegó primero..."
            },
            
            {
                "id": 5,
                "nombre": "La Cripta del Eclipse",
                "narrativa": "La puerta cede con un gemido de piedra contra piedra. La cripta es vasta, sus techos arqueados se pierden en una oscuridad antinatural que parece absorber la luz. En el centro, un círculo ritual grabado en el suelo pulsa con energía roja oscura. Gerick está allí, sin su capucha, revelando rasgos élficos marcados por cicatrices rituales. A su alrededor, velas negras arden con llamas que no dan calor. Sostiene la Tercera Llave. Detrás de él, un altar de obsidiana sobre el cual yace un sarcófago abierto... vacío. 'Llegas justo a tiempo', susurra Gerick, con una sonrisa que no es la suya. Sus ojos brillan con una luz que no es de este mundo. 'Ella necesita testigos para su despertar.' Las paredes comienzan a sangrar una oscuridad viscosa.",
                "visual_prompt": "cinematic lighting, top-down view, highly detailed fantasy art, dark ritual crypt, red glowing magic circle, evil cultist leader, empty sarcophagus, bleeding walls, 8k, dramatic confrontation",
                "ambiente_audio": "Zumbido grave de energía mágica, cánticos en latín, crujido de piedra, latido de corazón lento y fuerte",
                "enemigos": [
                    {
                        "nombre": "Gerick el Poseído",
                        "cantidad": "1",
                        "ac": 16,
                        "hp": 68,
                        "ataque": "+7",
                        "dano": "2d8+4 necrótico + CD 14 SAB o maldición",
                        "tactica": "Poseído por el espíritu del sumo sacerdote traidor. Lanza hechizos de nivel 3 (Bola de Fuego, Rayo de Escarcha, Disipar Magia). Invoca tentáculos de sombra del círculo ritual para agarrar enemigos (CD 15 FUE para escapar). En 50% HP, el sarcófago comienza a emanar energía oscura que lo cura 10 HP por turno a menos que se interrumpa el ritual. Debilidad: ataques radiantes y símbolos sagrados."
                    },
                    {
                        "nombre": "Tentáculos de la Entidad Dormida",
                        "cantidad": "1d3 (reaparecen cada 2 rondas)",
                        "ac": 13,
                        "hp": "15 cada uno",
                        "ataque": "+5",
                        "dano": "1d6+3 contundente + agarrar",
                        "tactica": "Emergen del círculo ritual. Agarran e intentan arrastrar víctimas hacia el sarcófago. Si logran meter a alguien en el sarcófago, esa persona debe hacer CD 16 SAB o ser poseída temporalmente. Destruir las velas negras reduce su número."
                    }
                ],
                "npcs": [
                    {
                        "nombre": "Elara (si fue ayudada antes)",
                        "rol": "Aliada espectral",
                        "personalidad": "Aparece en el momento más oscuro, canalizada por luz lunar filtrada. Puede lanzar Luz Sagrada una vez y dar ventaja en salvaciones contra posesión.",
                        "frase_entrada": "¡No mientras mi alma aún tenga voluntad! ¡Selûne, préstame tu luz una última vez!"
                    }
                ],
                "interacciones": [
                    {
                        "accion": "Interrumpir el ritual (Arcanos CD 17 o Religión CD 15)",
                        "exito": "Rompen el vínculo entre Gerick y el espíritu. Gerick cae inconsciente pero vivo. El combate se vuelve más fácil.",
                        "fallo": "El ritual se acelera. La entidad dormida comienza a manifestarse (combate más difícil)"
                    },
                    {
                        "accion": "Destruir las velas negras (acción de ataque)",
                        "exito": "Cada vela destruida reduce en 1 el número de tentáculos que aparecen",
                        "fallo": "Las llamas negras queman (1d6 fuego + 1d6 necrótico)"
                    },
                    {
                        "accion": "Apelar a lo que queda de Gerick (Persuasión CD 18)",
                        "exito": "Gerick lucha contra la posesión desde dentro, dándote 1 turno de ventaja en ataques",
                        "fallo": "El espíritu se burla y contraataca con un hechizo adicional"
                    },
                    {
                        "accion": "Cerrar el sarcófago (Atletismo CD 16 contra los tentáculos)",
                        "exito": "Sella la entidad, haciendo que Gerick pierda la mitad de su poder",
                        "fallo": "Los tentáculos contraatacan con ventaja"
                    }
                ],
                "botin": [
                    "Tercera Llave: Corona de Obsidiana (poderoso foco arcano)",
                    "Túnica del Sumo Sacerdote Caído (AC 12 + DES, resistencia a necrótico)",
                    "Grimorio del Culto Lunar (contiene 5 hechizos de nivel 1-3, algunos prohibidos)",
                    "Artefacto: 'Fragmento de la Luna Roja' - piedra que brilla con luz carmesí (¿qué hace?)",
                    "Cofre del tesoro del templo: 800 po, joyas por valor de 500 po, pergamino de Resurrección",
                    "El medallón de Gerick (si sobrevive, lo entrega agradecido; vale 200 po)"
                ],
                "hook_personaje": "El mago/hechicero siente la energía arcana del lugar. Si estudia los rituales aquí, puede aprender un hechizo prohibido nuevo. El paladín/clérigo siente que puede consagrar de nuevo el templo a Selûne, ganando una bendición permanente.",
                "transicion": "Con Gerick derrotado o liberado y el ritual interrumpido, las ruinas comienzan a temblar. La oscuridad antinatural se disipa. Los primeros rayos del amanecer se filtran por grietas en el techo. Elara, si fue redimida, se desvanece en paz con una sonrisa. Las ruinas pueden ser purificadas... o el fragmento de la Luna Roja podría ser estudiado para descubrir qué oscuridad se esconde más allá de las estrellas."
            }
        ],
        
        "plot_twist": {
            "titulo": "El Heredero Involuntario",
            "descripcion": "Gerick no sabía que era descendiente del sumo sacerdote traidor. El medallón que llevaba era una reliquia familiar que, al acercarse a las ruinas, despertó la conciencia ancestral dormida en su sangre. Fue usado como vasija para completar un ritual comenzado hace siglos. La verdadera pregunta es: ¿qué entidad está más allá de las estrellas esperando despertar? El Fragmento de la Luna Roja pulsa como si estuviera vivo..."
        }
    }

def _agregar_imagenes(historia: Dict):
    """Marca las escenas para que el frontend solicite imágenes (placeholder por ahora)"""
    # En la versión con ComfyUI, las imágenes se generan bajo demanda o en background.
    # Aquí podríamos pre-generar, pero por rendimiento lo dejaremos asíncrono.
    # Por ahora, dejamos un placeholder que activa el polling en el frontend si fuera necesario,
    # o simplemente dejamos que el DM lo active manualmente.
    pass
