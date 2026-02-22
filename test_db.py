import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.components.dnd.database import db

def run_tests():
    print("--- TESTING SRD DATABASE MANAGER ---")
    
    monster_query = "Un ogro brutal"
    print(f"\n1. Querying Monster: '{monster_query}'")
    ogro = db.get_monster(monster_query)
    if ogro:
        print(f"SUCCESS: Found Canonical Monster -> {ogro['name']} (CR {ogro['cr']}, HP: {ogro['hp']})")
    else:
        print("FAILED to find Ogro")

    spell_query = "Lanzar bola de fuego al centro"
    print(f"\n2. Querying Spell: '{spell_query}'")
    fireball = db.get_spell(spell_query)
    if fireball:
        print(f"SUCCESS: Found Canonical Spell -> {fireball['name']} (Daño: {fireball['level']} nivel)")
    else:
        print("FAILED to find Bola de Fuego")

if __name__ == "__main__":
    run_tests()
