import random
from typing import Dict, Any, List

def roll_dice(num: int, sides: int, multiplier: int = 1) -> int:
    return sum(random.randint(1, sides) for _ in range(num)) * multiplier

def get_individual_loot(cr: int) -> Dict[str, Any]:
    roll = random.randint(1, 100)
    coins = {"cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0}
    
    if cr <= 4:
        if roll <= 30: coins["cp"] = roll_dice(5, 6)
        elif roll <= 60: coins["sp"] = roll_dice(4, 6)
        elif roll <= 70: coins["ep"] = roll_dice(3, 6)
        elif roll <= 95: coins["gp"] = roll_dice(3, 6)
        else: coins["pp"] = roll_dice(1, 6)
    elif cr <= 10:
        if roll <= 30: 
            coins["cp"] = roll_dice(4, 6, 100)
            coins["ep"] = roll_dice(1, 6, 10)
        elif roll <= 60: 
            coins["sp"] = roll_dice(6, 6, 10)
            coins["gp"] = roll_dice(2, 6, 10)
        elif roll <= 70: 
            coins["ep"] = roll_dice(3, 6, 10)
            coins["gp"] = roll_dice(2, 6, 10)
        elif roll <= 95: 
            coins["gp"] = roll_dice(4, 6, 10)
        else:
            coins["gp"] = roll_dice(2, 6, 10)
            coins["pp"] = roll_dice(3, 6)
    elif cr <= 16:
        if roll <= 20:
            coins["sp"] = roll_dice(4, 6, 100)
            coins["gp"] = roll_dice(1, 6, 100)
        elif roll <= 35:
            coins["ep"] = roll_dice(1, 6, 100)
            coins["gp"] = roll_dice(1, 6, 100)
        elif roll <= 75:
            coins["gp"] = roll_dice(2, 6, 100)
            coins["pp"] = roll_dice(1, 6, 10)
        else:
            coins["gp"] = roll_dice(2, 6, 100)
            coins["pp"] = roll_dice(2, 6, 10)
    else: # CR 17+
        if roll <= 15:
            coins["ep"] = roll_dice(2, 6, 1000)
            coins["gp"] = roll_dice(8, 6, 100)
        elif roll <= 55:
            coins["gp"] = roll_dice(1, 6, 1000)
            coins["pp"] = roll_dice(1, 6, 100)
        else:
            coins["gp"] = roll_dice(1, 6, 1000)
            coins["pp"] = roll_dice(2, 6, 100)

    valuable_parts = []
    if coins["cp"] > 0: valuable_parts.append(f"{coins['cp']} pc")
    if coins["sp"] > 0: valuable_parts.append(f"{coins['sp']} pp")
    if coins["ep"] > 0: valuable_parts.append(f"{coins['ep']} pe")
    if coins["gp"] > 0: valuable_parts.append(f"{coins['gp']} po")
    if coins["pp"] > 0: valuable_parts.append(f"{coins['pp']} ppt")

    text = "Monedas: " + ", ".join(valuable_parts) if valuable_parts else "Bolsillos vacíos."

    return {
        "coins": coins,
        "valuables": [],
        "magic_items": [],
        "formatted_text": text
    }

def get_hoard_loot(cr: int) -> Dict[str, Any]:
    # Simplificación de la DMG Treasure Hoards
    roll = random.randint(1, 100)
    coins = {"cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0}
    valuables = []
    magic_items = []
    
    if cr <= 4:
        coins["cp"] = roll_dice(6, 6, 100)
        coins["sp"] = roll_dice(3, 6, 100)
        coins["gp"] = roll_dice(2, 6, 10)
        if roll <= 6: pass
        elif roll <= 16: valuables.append(f"{roll_dice(2, 6)} gemas de 10 po")
        elif roll <= 26: valuables.append(f"{roll_dice(2, 4)} gemas de 25 po")
        elif roll <= 36: valuables.append(f"{roll_dice(2, 6)} gemas de 50 po")
        elif roll <= 44:
            valuables.append(f"{roll_dice(2, 6)} gemas de 10 po")
            magic_items.append(f"Tirar {roll_dice(1, 6)} veces en Tabla Mágica A")
        elif roll <= 52:
            valuables.append(f"{roll_dice(2, 4)} gemas de 25 po")
            magic_items.append(f"Tirar {roll_dice(1, 6)} veces en Tabla Mágica A")
        elif roll <= 60:
            valuables.append(f"{roll_dice(2, 6)} gemas de 50 po")
            magic_items.append(f"Tirar {roll_dice(1, 6)} veces en Tabla Mágica A")
        elif roll <= 65:
            valuables.append(f"{roll_dice(2, 6)} gemas de 10 po")
            magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla Mágica B")
        elif roll <= 70:
            valuables.append(f"{roll_dice(2, 4)} gemas de 25 po")
            magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla Mágica B")
        elif roll <= 75:
            valuables.append(f"{roll_dice(2, 6)} gemas de 50 po")
            magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla Mágica B")
        elif roll <= 78:
            valuables.append(f"{roll_dice(2, 6)} gemas de 10 po")
            magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla Mágica C")
        elif roll <= 80:
            valuables.append(f"{roll_dice(2, 4)} gemas de 25 po")
            magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla Mágica C")
        elif roll <= 85:
            valuables.append(f"{roll_dice(2, 6)} gemas de 50 po")
            magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla Mágica C")
        elif roll <= 92:
            valuables.append(f"{roll_dice(2, 4)} gemas de 25 po")
            magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla Mágica F")
        elif roll <= 97:
            valuables.append(f"{roll_dice(2, 6)} gemas de 50 po")
            magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla Mágica F")
        elif roll <= 99:
            valuables.append(f"{roll_dice(2, 4)} gemas de 25 po")
            magic_items.append(f"Tirar 1 vez en Tabla Mágica G")
        else:
            valuables.append(f"{roll_dice(2, 6)} gemas de 50 po")
            magic_items.append(f"Tirar 1 vez en Tabla Mágica G")
            
    elif cr <= 10:
        coins["cp"] = roll_dice(2, 6, 100)
        coins["sp"] = roll_dice(2, 6, 1000)
        coins["gp"] = roll_dice(6, 6, 100)
        coins["pp"] = roll_dice(3, 6, 10)
        if roll <= 4: pass
        elif roll <= 10: valuables.append(f"{roll_dice(2, 4)} gemas de 25 po")
        elif roll <= 16: valuables.append(f"{roll_dice(3, 6)} gemas de 50 po")
        elif roll <= 22: valuables.append(f"{roll_dice(3, 6)} gemas de 100 po")
        elif roll <= 28: valuables.append(f"{roll_dice(2, 4)} objetos de arte de 250 po")
        else:
            val_roll = random.randint(1,4)
            if val_roll == 1: valuables.append(f"{roll_dice(2, 4)} gemas de 25 po")
            elif val_roll == 2: valuables.append(f"{roll_dice(3, 6)} gemas de 50 po")
            elif val_roll == 3: valuables.append(f"{roll_dice(3, 6)} gemas de 100 po")
            else: valuables.append(f"{roll_dice(2, 4)} objetos de arte de 250 po")
            
            if roll <= 44: magic_items.append(f"Tirar {roll_dice(1, 6)} veces en Tabla A")
            elif roll <= 64: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla B")
            elif roll <= 74: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla C")
            elif roll <= 80: magic_items.append(f"Tirar 1 vez en Tabla D")
            elif roll <= 94: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla F")
            elif roll <= 98: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla G")
            else: magic_items.append(f"Tirar 1 vez en Tabla H")
            
    elif cr <= 16:
        coins["gp"] = roll_dice(4, 6, 1000)
        coins["pp"] = roll_dice(5, 6, 100)
        val_idx = random.randint(1,4)
        if val_idx == 1: valuables.append(f"{roll_dice(2, 4)} objetos de arte de 250 po")
        elif val_idx == 2: valuables.append(f"{roll_dice(2, 4)} objetos de arte de 750 po")
        elif val_idx == 3: valuables.append(f"{roll_dice(3, 6)} gemas de 500 po")
        else: valuables.append(f"{roll_dice(3, 6)} gemas de 1000 po")
        
        if roll <= 3: pass
        elif roll <= 15: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla A, B")
        elif roll <= 29: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla C")
        elif roll <= 50: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla D")
        elif roll <= 66: magic_items.append(f"Tirar 1 vez en Tabla E")
        elif roll <= 74: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla F, G")
        elif roll <= 82: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla H")
        elif roll <= 92: magic_items.append(f"Tirar 1 vez en Tabla I")
        else: magic_items.append(f"Tirar múltiples veces en Tablas D, E o I")
        
    else: # CR 17+
        coins["gp"] = roll_dice(12, 6, 1000)
        coins["pp"] = roll_dice(8, 6, 1000)
        val_idx = random.randint(1,4)
        if val_idx == 1: valuables.append(f"{roll_dice(3, 6)} gemas de 1000 po")
        elif val_idx == 2: valuables.append(f"{roll_dice(1, 8)} objetos de arte de 2500 po")
        elif val_idx == 3: valuables.append(f"{roll_dice(1, 4)} objetos de arte de 7500 po")
        else: valuables.append(f"{roll_dice(1, 8)} gemas de 5000 po")
        
        if roll <= 2: pass
        elif roll <= 14: magic_items.append(f"Tirar {roll_dice(1, 8)} veces en Tabla C")
        elif roll <= 46: magic_items.append(f"Tirar {roll_dice(1, 6)} veces en Tabla D")
        elif roll <= 68: magic_items.append(f"Tirar {roll_dice(1, 6)} veces en Tabla E")
        elif roll <= 73: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla G")
        elif roll <= 80: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla H")
        else: magic_items.append(f"Tirar {roll_dice(1, 4)} veces en Tabla I")

    coin_parts = []
    if coins["cp"] > 0: coin_parts.append(f"{coins['cp']} pc")
    if coins["sp"] > 0: coin_parts.append(f"{coins['sp']} pp")
    if coins["ep"] > 0: coin_parts.append(f"{coins['ep']} pe")
    if coins["gp"] > 0: coin_parts.append(f"{coins['gp']} po")
    if coins["pp"] > 0: coin_parts.append(f"{coins['pp']} ppt")

    text_parts = []
    if coin_parts:
        text_parts.append("💰 Recompensa Metálica: " + ", ".join(coin_parts))
    if valuables:
        text_parts.append("💎 Valores: " + ", ".join(valuables))
    if magic_items:
        text_parts.append("✨ Objetos Mágicos: " + ", ".join(magic_items))

    text = "\n".join(text_parts) if text_parts else "El escondite estaba extrañamente vacío."

    return {
        "coins": coins,
        "valuables": valuables,
        "magic_items": magic_items,
        "formatted_text": text
    }

def generate_loot(cr: int, loot_type: str = "individual") -> Dict[str, Any]:
    if loot_type == "hoard":
        return get_hoard_loot(cr)
    return get_individual_loot(cr)
