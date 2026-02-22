"""
Datos del SRD D&D 5e para poblar la biblioteca.
Se ejecuta seed_library_if_empty() al iniciar si las tablas están vacías.
"""
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger("cronista.srd")

# ─── Enemigos SRD ────────────────────────────────────────

SRD_ENEMIES: List[Dict[str, Any]] = [
    # CR 0
    {"name": "Rata", "cr": 0, "hp": 1, "ac": 10, "attack": "+0", "damage": "1", "abilities_json": "[]", "tags": "bestia,cr0,subterráneo"},
    # CR 1/8
    {"name": "Bandido", "cr": 0.125, "hp": 11, "ac": 12, "attack": "+3", "damage": "1d6+1", "abilities_json": "[]", "tags": "humanoide,cr1/8,social"},
    {"name": "Guardia Tribal", "cr": 0.125, "hp": 11, "ac": 12, "attack": "+3", "damage": "1d6+1", "abilities_json": "[]", "tags": "humanoide,cr1/8"},
    # CR 1/4
    {"name": "Goblin", "cr": 0.25, "hp": 7, "ac": 15, "attack": "+4", "damage": "1d6+2", "abilities_json": json.dumps([{"nombre": "Escape Ágil", "desc": "Puede Desengancharse o Esconderse como acción bonus"}]), "tags": "goblinoide,cr1/4,emboscada"},
    {"name": "Kobold", "cr": 0.125, "hp": 5, "ac": 12, "attack": "+4", "damage": "1d4+2", "abilities_json": json.dumps([{"nombre": "Tácticas de Manada", "desc": "Ventaja en ataque si un aliado está a 5 pies del objetivo"}]), "tags": "reptil,cr1/8,trampas"},
    {"name": "Esqueleto", "cr": 0.25, "hp": 13, "ac": 13, "attack": "+4", "damage": "1d6+2", "abilities_json": json.dumps([{"nombre": "Vulnerabilidad", "desc": "Vulnerable a daño contundente"}]), "tags": "no-muerto,cr1/4,mazmorra"},
    {"name": "Zombie", "cr": 0.25, "hp": 22, "ac": 8, "attack": "+3", "damage": "1d6+1", "abilities_json": json.dumps([{"nombre": "Tenacidad No-Muerta", "desc": "Si el daño lo reduce a 0 HP, CD 5+daño CON para quedar con 1 HP"}]), "tags": "no-muerto,cr1/4,mazmorra"},
    {"name": "Lobo", "cr": 0.25, "hp": 11, "ac": 13, "attack": "+4", "damage": "2d4+2", "abilities_json": json.dumps([{"nombre": "Derribar", "desc": "El objetivo debe superar FUE CD 11 o cae derribado"}]), "tags": "bestia,cr1/4,bosque,manada"},
    # CR 1/2
    {"name": "Orco", "cr": 0.5, "hp": 15, "ac": 13, "attack": "+5", "damage": "1d12+3", "abilities_json": json.dumps([{"nombre": "Agresivo", "desc": "Puede moverse hasta su velocidad hacia un enemigo como acción bonus"}]), "tags": "humanoide,cr1/2,agresivo"},
    {"name": "Gnoll", "cr": 0.5, "hp": 22, "ac": 15, "attack": "+4", "damage": "1d8+2", "abilities_json": json.dumps([{"nombre": "Frenesí", "desc": "Ataque bonus como acción bonus al reducir a 0 HP a un enemigo"}]), "tags": "humanoide,cr1/2,salvaje"},
    {"name": "Oso Negro", "cr": 0.5, "hp": 19, "ac": 11, "attack": "+4", "damage": "1d6+2", "abilities_json": json.dumps([{"nombre": "Multiataques", "desc": "Dos ataques: mordisco y garras"}]), "tags": "bestia,cr1/2,bosque"},
    # CR 1
    {"name": "Ghoul", "cr": 1, "hp": 22, "ac": 12, "attack": "+4", "damage": "2d6+2", "abilities_json": json.dumps([{"nombre": "Parálisis", "desc": "El objetivo debe superar CON CD 10 o queda paralizado 1 minuto"}]), "tags": "no-muerto,cr1,mazmorra,parálisis"},
    {"name": "Araña Gigante", "cr": 1, "hp": 26, "ac": 14, "attack": "+5", "damage": "1d8+3", "abilities_json": json.dumps([{"nombre": "Veneno", "desc": "2d8 daño veneno, CON CD 11 mitad"}, {"nombre": "Trepar", "desc": "Trepa sin tirada"}]), "tags": "bestia,cr1,subterráneo,veneno"},
    {"name": "Espectro", "cr": 1, "hp": 22, "ac": 12, "attack": "+4", "damage": "3d6", "abilities_json": json.dumps([{"nombre": "Incorpóreo", "desc": "Puede moverse a través de criaturas y objetos"}, {"nombre": "Drenaje de Vida", "desc": "Reduce HP máximo del objetivo"}]), "tags": "no-muerto,cr1,incorpóreo"},
    {"name": "Capitán Bandido", "cr": 2, "hp": 65, "ac": 15, "attack": "+5", "damage": "2d6+3", "abilities_json": json.dumps([{"nombre": "Multiataques", "desc": "Tres ataques cuerpo a cuerpo"}]), "tags": "humanoide,cr2,líder"},
    # CR 2
    {"name": "Ogro", "cr": 2, "hp": 59, "ac": 11, "attack": "+6", "damage": "2d8+4", "abilities_json": "[]", "tags": "gigante,cr2,bruto"},
    {"name": "Hombre Lobo", "cr": 3, "hp": 58, "ac": 12, "attack": "+4", "damage": "2d4+2", "abilities_json": json.dumps([{"nombre": "Licantropía", "desc": "Inmune a daño no mágico ni plateado"}, {"nombre": "Cambio de Forma", "desc": "Humanoide, híbrido o lobo"}]), "tags": "licántropo,cr3,maldición"},
    # CR 3-5
    {"name": "Momia", "cr": 3, "hp": 58, "ac": 11, "attack": "+5", "damage": "2d6+3", "abilities_json": json.dumps([{"nombre": "Mirada Aterradora", "desc": "Asustado si falla SAB CD 11"}, {"nombre": "Puño Podrido", "desc": "Maldición: no recupera HP"}]), "tags": "no-muerto,cr3,maldición"},
    {"name": "Troll", "cr": 5, "hp": 84, "ac": 15, "attack": "+7", "damage": "2d6+4", "abilities_json": json.dumps([{"nombre": "Regeneración", "desc": "Recupera 10 HP al inicio del turno, anulado por fuego o ácido"}, {"nombre": "Multiataques", "desc": "Tres ataques: mordisco y dos garras"}]), "tags": "gigante,cr5,regeneración"},
    {"name": "Basilisco", "cr": 3, "hp": 52, "ac": 15, "attack": "+5", "damage": "2d6+3", "abilities_json": json.dumps([{"nombre": "Mirada Petrificante", "desc": "CON CD 12 o petrificado gradualmente"}]), "tags": "monstruosidad,cr3,petrificación"},
    # CR 5+
    {"name": "Elemental de Fuego", "cr": 5, "hp": 102, "ac": 13, "attack": "+6", "damage": "2d6+3", "abilities_json": json.dumps([{"nombre": "Forma de Fuego", "desc": "Prende fuego a objetos inflamables"}, {"nombre": "Inmunidad al Fuego", "desc": "Inmune a daño de fuego"}]), "tags": "elemental,cr5,fuego"},
    {"name": "Vampiro Engendro", "cr": 5, "hp": 82, "ac": 15, "attack": "+6", "damage": "1d8+3", "abilities_json": json.dumps([{"nombre": "Mordisco", "desc": "Drena 3d6 HP necróticos"}, {"nombre": "Regeneración", "desc": "10 HP/turno si tiene más de 0"}]), "tags": "no-muerto,cr5,vampiro"},
    {"name": "Dragón Joven Rojo", "cr": 10, "hp": 178, "ac": 18, "attack": "+10", "damage": "2d10+6", "abilities_json": json.dumps([{"nombre": "Aliento de Fuego", "desc": "Cono 30 pies, 16d6 fuego, DES CD 17 mitad"}, {"nombre": "Multiataques", "desc": "Mordisco + 2 garras"}]), "tags": "dragón,cr10,fuego,jefe"},
    {"name": "Liche", "cr": 21, "hp": 135, "ac": 17, "attack": "+12", "damage": "3d6", "abilities_json": json.dumps([{"nombre": "Lanzamiento de Hechizos", "desc": "Lanzador de nivel 18"}, {"nombre": "Filacteria", "desc": "No puede ser destruido permanentemente sin destruir su filacteria"}]), "tags": "no-muerto,cr21,jefe,mago"},
]

# ─── NPCs SRD ────────────────────────────────────────────

SRD_NPCS: List[Dict[str, Any]] = [
    {"name": "Tabernero", "race": "Humano", "class_name": "Plebeyos", "description": "Posadero robusto, conoce todos los rumores locales", "personality": "Jovial pero cauteloso con extraños", "stats_json": "{}", "tags": "social,pueblo,información"},
    {"name": "Herrero", "race": "Enano", "class_name": "Artesano", "description": "Maestro forjador con brazos como troncos", "personality": "Perfeccionista, habla poco pero es leal", "stats_json": "{}", "tags": "social,pueblo,comercio,equipo"},
    {"name": "Sacerdotisa", "race": "Humana", "class_name": "Clérigo", "description": "Sanadora del templo local, cubierta de cicatrices de guerra", "personality": "Compasiva pero con oscuro pasado", "stats_json": json.dumps({"FUE": 10, "DES": 12, "CON": 14, "INT": 13, "SAB": 16, "CAR": 14}), "tags": "social,templo,curación,quest-giver"},
    {"name": "Mercader Viajero", "race": "Halfling", "class_name": "Comerciante", "description": "Pequeño pero astuto, carga un carromato lleno de curiosidades", "personality": "Encantador, siempre busca un trato", "stats_json": "{}", "tags": "social,comercio,viajero,items"},
    {"name": "Guardia de la Ciudad", "race": "Humano", "class_name": "Guerrero", "description": "Veterano cansado que vigila las puertas", "personality": "Sospecha de adventureros, soborneable", "stats_json": json.dumps({"FUE": 14, "DES": 12, "CON": 13, "INT": 10, "SAB": 11, "CAR": 10}), "tags": "social,ciudad,autoridad"},
    {"name": "Noble Corrupto", "race": "Humano", "class_name": "Noble", "description": "Señor local que busca poder a cualquier costo", "personality": "Carismático en público, despiadado en privado", "stats_json": "{}", "tags": "social,ciudad,antagonista,político"},
    {"name": "Sabio Ermitaño", "race": "Elfo", "class_name": "Mago", "description": "Anciano elfo que vive en una torre llena de libros", "personality": "Distraído, habla en acertijos", "stats_json": json.dumps({"FUE": 8, "DES": 10, "CON": 10, "INT": 18, "SAB": 16, "CAR": 11}), "tags": "social,conocimiento,mago,quest-giver"},
    {"name": "Espía de la Cofradía", "race": "Humano", "class_name": "Pícaro", "description": "Se hace pasar por bardo itinerante", "personality": "Encantador, siempre escuchando", "stats_json": json.dumps({"FUE": 10, "DES": 16, "CON": 12, "INT": 14, "SAB": 13, "CAR": 15}), "tags": "social,espía,gremio,secretos"},
    {"name": "Druida del Bosque", "race": "Firbolg", "class_name": "Druida", "description": "Protector del bosque ancestral, desconfía de la civilización", "personality": "Habla poco, observa mucho", "stats_json": json.dumps({"FUE": 12, "DES": 10, "CON": 14, "INT": 12, "SAB": 17, "CAR": 11}), "tags": "social,bosque,naturaleza,quest-giver"},
    {"name": "Capitana Pirata", "race": "Humana", "class_name": "Guerrero/Pícaro", "description": "Legendaria corsaria con parche en el ojo y lengua afilada", "personality": "Audaz, leal a su tripulación", "stats_json": json.dumps({"FUE": 15, "DES": 16, "CON": 14, "INT": 13, "SAB": 12, "CAR": 16}), "tags": "social,mar,pirata,aliada"},
    {"name": "Aprendiz de Mago", "race": "Gnomo", "class_name": "Mago", "description": "Joven gnomo que causa explosiones accidentales", "personality": "Entusiasta, torpe, bien intencionado", "stats_json": "{}", "tags": "social,mago,cómico"},
    {"name": "Vampiresa Diplomática", "race": "Dhampir", "class_name": "Noble", "description": "Líder de un enclave vampírico que busca paz con los mortales", "personality": "Elegante, fría, sorprendentemente honesta", "stats_json": json.dumps({"FUE": 16, "DES": 18, "CON": 16, "INT": 17, "SAB": 15, "CAR": 20}), "tags": "social,no-muerto,diplomático,antagonista"},
    {"name": "Herredor Maldito", "race": "Humano", "class_name": "Herrero", "description": "Sus armas están malditas sin que él lo sepa", "personality": "Amable, preocupado por las quejas de sus clientes", "stats_json": "{}", "tags": "social,maldición,misterio,pueblo"},
    {"name": "Oracle Ciega", "race": "Tiefling", "class_name": "Clarividente", "description": "Ve el futuro pero no puede ver el presente", "personality": "Críptica, genuinamente quiere ayudar", "stats_json": json.dumps({"FUE": 8, "DES": 10, "CON": 12, "INT": 16, "SAB": 20, "CAR": 14}), "tags": "social,profecía,quest-giver,misterio"},
    {"name": "Gladiador Retirado", "race": "Medio-Orco", "class_name": "Guerrero", "description": "Campeón de la arena ahora maneja una taberna de mala muerte", "personality": "Rudo pero protector de los débiles", "stats_json": json.dumps({"FUE": 18, "DES": 14, "CON": 16, "INT": 10, "SAB": 12, "CAR": 13}), "tags": "social,guerrero,aliado,pueblo"},
]

# ─── Items SRD ───────────────────────────────────────────

SRD_ITEMS: List[Dict[str, Any]] = [
    # Armas cuerpo a cuerpo
    {"name": "Daga", "item_type": "arma", "rarity": "Común", "damage": "1d4", "properties": "Sutil, ligera, arrojadiza (6/18m)", "description": "Hoja corta y afilada", "value_gp": 2, "weight": 0.5, "tags": "arma,simple,cuerpo-a-cuerpo,sutil"},
    {"name": "Espada Corta", "item_type": "arma", "rarity": "Común", "damage": "1d6", "properties": "Sutil, ligera", "description": "Hoja recta de un filo", "value_gp": 10, "weight": 1.0, "tags": "arma,marcial,cuerpo-a-cuerpo,sutil"},
    {"name": "Espada Larga", "item_type": "arma", "rarity": "Común", "damage": "1d8", "properties": "Versátil (1d10)", "description": "Hoja ancha y pesada, el arma estándar del caballero", "value_gp": 15, "weight": 1.5, "tags": "arma,marcial,cuerpo-a-cuerpo"},
    {"name": "Espada Bastarda", "item_type": "arma", "rarity": "Común", "damage": "2d6", "properties": "Pesada, a dos manos", "description": "Enorme hoja que requiere ambas manos", "value_gp": 50, "weight": 3.0, "tags": "arma,marcial,cuerpo-a-cuerpo,pesada"},
    {"name": "Hacha de Guerra", "item_type": "arma", "rarity": "Común", "damage": "1d8", "properties": "Versátil (1d10)", "description": "Hacha de combate con filo de media luna", "value_gp": 10, "weight": 2.0, "tags": "arma,marcial,cuerpo-a-cuerpo"},
    {"name": "Maza", "item_type": "arma", "rarity": "Común", "damage": "1d6", "properties": "-", "description": "Cabeza de hierro macizo sobre mango de madera", "value_gp": 5, "weight": 2.0, "tags": "arma,simple,cuerpo-a-cuerpo,contundente"},
    {"name": "Lanza", "item_type": "arma", "rarity": "Común", "damage": "1d6", "properties": "Arrojadiza (6/18m), versátil (1d8)", "description": "Punta de acero en asta de madera", "value_gp": 1, "weight": 1.5, "tags": "arma,simple,cuerpo-a-cuerpo"},
    # Armas a distancia
    {"name": "Arco Corto", "item_type": "arma", "rarity": "Común", "damage": "1d6", "properties": "A dos manos, munición (24/96m)", "description": "Arco compacto de madera flexible", "value_gp": 25, "weight": 1.0, "tags": "arma,simple,distancia"},
    {"name": "Arco Largo", "item_type": "arma", "rarity": "Común", "damage": "1d8", "properties": "Pesada, a dos manos, munición (45/180m)", "description": "Arco alto de tejo o fresno", "value_gp": 50, "weight": 1.0, "tags": "arma,marcial,distancia,pesada"},
    {"name": "Ballesta Ligera", "item_type": "arma", "rarity": "Común", "damage": "1d8", "properties": "Munición (24/96m), carga, a dos manos", "description": "Mecanismo de disparo con virotes", "value_gp": 25, "weight": 2.5, "tags": "arma,simple,distancia"},
    # Armaduras
    {"name": "Armadura de Cuero", "item_type": "armadura", "rarity": "Común", "damage": "", "properties": "CA 11 + mod DES", "description": "Cuero endurecido y curtido", "value_gp": 10, "weight": 5.0, "tags": "armadura,ligera"},
    {"name": "Cota de Malla", "item_type": "armadura", "rarity": "Común", "damage": "", "properties": "CA 16, FUE 13, Desventaja Sigilo", "description": "Anillos de metal entrelazados", "value_gp": 75, "weight": 27.5, "tags": "armadura,pesada"},
    {"name": "Escudo", "item_type": "armadura", "rarity": "Común", "damage": "", "properties": "+2 CA", "description": "Escudo de madera o metal", "value_gp": 10, "weight": 3.0, "tags": "armadura,escudo"},
    # Pociones
    {"name": "Poción de Curación", "item_type": "poción", "rarity": "Común", "damage": "", "properties": "Cura 2d4+2 HP", "description": "Líquido rojo centelleante que restaura vitalidad", "value_gp": 50, "weight": 0.25, "tags": "poción,curación,consumible"},
    {"name": "Poción de Curación Mayor", "item_type": "poción", "rarity": "Infrecuente", "damage": "", "properties": "Cura 4d4+4 HP", "description": "Líquido carmesí brillante con propiedades curativas potentes", "value_gp": 150, "weight": 0.25, "tags": "poción,curación,consumible"},
    {"name": "Poción de Invisibilidad", "item_type": "poción", "rarity": "Muy Raro", "damage": "", "properties": "Invisible 1 hora o hasta atacar/lanzar hechizo", "description": "Líquido transparente que parece vacío", "value_gp": 500, "weight": 0.25, "tags": "poción,utilidad,consumible"},
    # Objetos de aventura
    {"name": "Cuerda de Seda (15m)", "item_type": "objeto", "rarity": "Común", "damage": "", "properties": "2 HP, CD 17 para romper", "description": "Cuerda fina pero muy resistente", "value_gp": 10, "weight": 2.5, "tags": "equipo,aventura"},
    {"name": "Antorcha", "item_type": "objeto", "rarity": "Común", "damage": "", "properties": "Luz 6m/12m tenue, arde 1 hora", "description": "Palo con resina inflamable", "value_gp": 0, "weight": 0.5, "tags": "equipo,aventura,luz"},
    {"name": "Kit de Sanador", "item_type": "herramienta", "rarity": "Común", "damage": "", "properties": "10 usos, estabilizar sin tirada", "description": "Vendas, ungüentos y férulas", "value_gp": 5, "weight": 1.5, "tags": "herramienta,curación"},
    {"name": "Ganzúas", "item_type": "herramienta", "rarity": "Común", "damage": "", "properties": "Competencia para abrir cerraduras", "description": "Set de ganzúas de acero fino", "value_gp": 25, "weight": 0.5, "tags": "herramienta,pícaro,cerraduras"},
]

# ─── Encuentros SRD ──────────────────────────────────────

SRD_ENCOUNTERS: List[Dict[str, Any]] = [
    {
        "name": "Emboscada Goblin",
        "description": "Un grupo de goblins embosca a los viajeros en un camino estrecho del bosque",
        "difficulty": "Fácil",
        "enemies_json": json.dumps([
            {"nombre": "Goblin", "cantidad": 4, "hp": 7, "ac": 15, "ataque": "+4", "dano": "1d6+2"}
        ]),
        "environment": "Bosque con rocas y matorrales",
        "loot": "2d10 monedas de plata, mapa tosco",
        "tags": "bosque,emboscada,goblinoide,fácil"
    },
    {
        "name": "Guarida Kobold",
        "description": "Cavernas llenas de trampas donde habita una tribu de kobolds",
        "difficulty": "Media",
        "enemies_json": json.dumps([
            {"nombre": "Kobold", "cantidad": 6, "hp": 5, "ac": 12, "ataque": "+4", "dano": "1d4+2"},
            {"nombre": "Kobold Alado", "cantidad": 2, "hp": 7, "ac": 13, "ataque": "+4", "dano": "1d4+2"}
        ]),
        "environment": "Cueva con trampas de foso y rocas sueltas",
        "loot": "Huevos de dragón falsos, 3d6 monedas de oro",
        "tags": "cueva,trampas,reptil,media"
    },
    {
        "name": "Cripta de No-Muertos",
        "description": "Una cripta antigua donde los muertos se levantan para defender su descanso",
        "difficulty": "Media",
        "enemies_json": json.dumps([
            {"nombre": "Esqueleto", "cantidad": 4, "hp": 13, "ac": 13, "ataque": "+4", "dano": "1d6+2"},
            {"nombre": "Zombie", "cantidad": 2, "hp": 22, "ac": 8, "ataque": "+3", "dano": "1d6+1"}
        ]),
        "environment": "Cripta con sarcófagos y altar profanado",
        "loot": "Amuleto sagrado, poción de curación",
        "tags": "mazmorra,no-muerto,cripta,media"
    },
    {
        "name": "Guarida del Ogro",
        "description": "Un ogro hambriento ha tomado una cueva como guarida, acumulando tesoros robados",
        "difficulty": "Difícil",
        "enemies_json": json.dumps([
            {"nombre": "Ogro", "cantidad": 1, "hp": 59, "ac": 11, "ataque": "+6", "dano": "2d8+4"},
            {"nombre": "Goblin", "cantidad": 3, "hp": 7, "ac": 15, "ataque": "+4", "dano": "1d6+2"}
        ]),
        "environment": "Cueva grande con huesos y carromatos destrozados",
        "loot": "4d10 monedas de oro, espada mágica +1",
        "tags": "cueva,gigante,difícil,jefe"
    },
    {
        "name": "Bosque Envenenado",
        "description": "Arañas gigantes han tejido sus redes entre los árboles, convirtiendo el bosque en trampa mortal",
        "difficulty": "Difícil",
        "enemies_json": json.dumps([
            {"nombre": "Araña Gigante", "cantidad": 3, "hp": 26, "ac": 14, "ataque": "+5", "dano": "1d8+3"}
        ]),
        "environment": "Bosque denso cubierto de telarañas, visibilidad reducida",
        "loot": "Seda de araña (50 po), veneno extraíble",
        "tags": "bosque,bestia,veneno,difícil"
    },
    {
        "name": "Asalto al Puente",
        "description": "Orcos controlan un puente estratégico y cobran peaje a los viajeros",
        "difficulty": "Media",
        "enemies_json": json.dumps([
            {"nombre": "Orco", "cantidad": 3, "hp": 15, "ac": 13, "ataque": "+5", "dano": "1d12+3"}
        ]),
        "environment": "Puente de piedra sobre un barranco profundo",
        "loot": "Bolsa de peaje con 5d10 monedas de oro",
        "tags": "exterior,humanoide,social,media"
    },
    {
        "name": "La Tumba del Caballero",
        "description": "El espíritu de un caballero caído defiende su tumba junto a sus soldados no-muertos",
        "difficulty": "Difícil",
        "enemies_json": json.dumps([
            {"nombre": "Espectro", "cantidad": 1, "hp": 22, "ac": 12, "ataque": "+4", "dano": "3d6"},
            {"nombre": "Esqueleto", "cantidad": 4, "hp": 13, "ac": 13, "ataque": "+4", "dano": "1d6+2"}
        ]),
        "environment": "Tumba subterránea con armaduras vacías y estandartes raídos",
        "loot": "Espada del Caballero (+1), escudo heráldico",
        "tags": "mazmorra,no-muerto,jefe,difícil"
    },
    {
        "name": "Manada de Lobos",
        "description": "Una manada de lobos hambrientos acecha al grupo durante la noche",
        "difficulty": "Fácil",
        "enemies_json": json.dumps([
            {"nombre": "Lobo", "cantidad": 5, "hp": 11, "ac": 13, "ataque": "+4", "dano": "2d4+2"}
        ]),
        "environment": "Llanura o bosque durante la noche, niebla baja",
        "loot": "Pieles de lobo (3 po cada una)",
        "tags": "exterior,bestia,nocturno,fácil"
    },
    {
        "name": "Ritual de Ghouls",
        "description": "Ghouls realizan un oscuro ritual en un cementerio abandonado",
        "difficulty": "Difícil",
        "enemies_json": json.dumps([
            {"nombre": "Ghoul", "cantidad": 4, "hp": 22, "ac": 12, "ataque": "+4", "dano": "2d6+2"}
        ]),
        "environment": "Cementerio con lápidas rotas y altar profanado",
        "loot": "Libro de rituales oscuros, gemas (3x 25 po)",
        "tags": "cementerio,no-muerto,parálisis,difícil"
    },
    {
        "name": "El Troll del Puente",
        "description": "Un temible troll ha reclamado un antiguo puente como su territorio de caza",
        "difficulty": "Letal",
        "enemies_json": json.dumps([
            {"nombre": "Troll", "cantidad": 1, "hp": 84, "ac": 15, "ataque": "+7", "dano": "2d6+4"}
        ]),
        "environment": "Puente de piedra cubierto de musgo sobre río turbulento",
        "loot": "Tesoro acumulado: 8d10 po, anillo de protección",
        "tags": "exterior,gigante,regeneración,letal,jefe"
    },
]


def seed_library_if_empty():
    """Puebla la biblioteca con datos SRD si las tablas están vacías."""
    from app.database import get_session
    from app.db_models import LibraryEnemy, LibraryNPC, LibraryItem, LibraryEncounter
    from sqlmodel import select, func

    with get_session() as db:
        # Verificar si ya hay datos
        enemy_count = db.exec(select(func.count()).select_from(LibraryEnemy)).one()
        if enemy_count > 0:
            logger.info("📚 Biblioteca ya tiene datos, saltando seed")
            return

        logger.info("📚 Sembrando biblioteca con datos SRD D&D 5e...")

        # Enemigos
        for data in SRD_ENEMIES:
            db.add(LibraryEnemy(**data))

        # NPCs
        for data in SRD_NPCS:
            db.add(LibraryNPC(**data))

        # Items
        for data in SRD_ITEMS:
            db.add(LibraryItem(**data))

        # Encuentros
        for data in SRD_ENCOUNTERS:
            db.add(LibraryEncounter(**data))

        db.commit()
        logger.info(f"✅ SRD sembrado: {len(SRD_ENEMIES)} enemigos, {len(SRD_NPCS)} NPCs, {len(SRD_ITEMS)} items, {len(SRD_ENCOUNTERS)} encuentros")
