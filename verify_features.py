import sys
import os
import asyncio
from app.components.ai.memory import get_narrative_context
from app.components.combat.balance import adjust_encounter
from app.state import journal

# Agregar mock de sesiones
from app.config import PERSONAJES_EMERGENCIA

async def test_features():
    print("🧪 INICIANDO VERIFICACIÓN DE CARACTERÍSTICAS V80.2")
    print("=" * 60)
    
    # 1. VERIFICACIÓN DE MEMORIA NARRATIVA
    print("\n📚 TEST 1: Memoria Narrativa")
    session_id = "test_session_1"
    
    # Simular eventos
    journal.register_event(session_id, "start", "La aventura comienza en una taberna.")
    journal.register_event(session_id, "combat", "El grupo derrotó a los goblins.")
    journal.register_event(session_id, "plot", "El rey ha sido envenenado.")
    
    context = get_narrative_context(session_id)
    print(f"Contexto recuperado:\n{context}")
    
    if "envenenado" in context and "goblins" in context:
        print("✅ PASS: Memoria recupera eventos correctamente")
    else:
        print("❌ FAIL: Memoria no recuperó los eventos esperados")
        
    # 2. VERIFICACIÓN DE BALANCEO
    print("\n⚖️ TEST 2: Balanceo de Encuentros")
    
    # Grupo nivel 1 (muy débil)
    pjs_low_level = [
        {"nombre": "A", "nivel": 1},
        {"nombre": "B", "nivel": 1},
        {"nombre": "C", "nivel": 1},
        {"nombre": "D", "nivel": 1}
    ]
    
    # Encuentro mortal: 4 Orcos (CR 1/2 c/u = 400 XP) vs Nvl 1 (Deadly a partir de 400)
    # 4 Orcos HP 15 = 60 HP total. Daño 1d12+3 (9.5 prom)
    enemigos_deadly = [
        {"nombre": "Orco Jefe", "cantidad": 4, "hp": 15, "dano": "1d12+3", "cr_estimado": 0.5}
    ]
    
    print("  -> Probando encuentro Deadly...")
    adjusted = adjust_encounter(enemigos_deadly, pjs_low_level)
    
    hp_adjusted = adjusted[0]["hp"]
    print(f"  -> HP Original: 15, Ajustado: {hp_adjusted}")
    
    if hp_adjusted < 15:
        print("✅ PASS: El sistema nerfeó el HP de un encuentro mortal")
    else:
        print("❌ FAIL: El sistema NO ajustó el HP")
        
    # 3. VERIFICACIÓN MOCK COMFYUI (Simulada)
    print("\n🎨 TEST 3: ComfyUI (Cliente Mock)")
    from app.components.ai.image_generator import queue_prompt
    
    # Solo verificamos que el módulo exista y la función sea llamable
    # No podemos probar conexión real sin el servidor corriendo
    if callable(queue_prompt):
        print("✅ PASS: Cliente ComfyUI importable y función definida")

    from app.components.ai.image_generator import WORKFLOWS
    print(f"  -> Workflows cargados: {list(WORKFLOWS.keys())}")
    
    if "map" in WORKFLOWS and "portrait" in WORKFLOWS:
        print("✅ PASS: Workflows de Mapa y Retrato cargados correctamente")
        
        # Test de parsing dinámico
        print("\n🔍 TEST 4: Parsing Dinámico de Nodos")
        for wf_name, wf in WORKFLOWS.items():
            if wf_name == "default": continue
            
            print(f"  -> Analizando '{wf_name}'...")
            ksa = None
            pos = None
            
            for nid, node in wf.items():
                if node.get("class_type") in ["KSampler", "KSamplerAdvanced"]:
                    ksa = nid
                    # Buscar positivo
                    inputs = node.get("inputs", {})
                    if "positive" in inputs and isinstance(inputs["positive"], list):
                        pos = str(inputs["positive"][0])
                    break
            
            if ksa:
                print(f"     ✅ KSampler encontrado (ID: {ksa})")
            else:
                print(f"     ❌ KSampler NO encontrado")

            if pos and pos in wf:
                print(f"     ✅ Prompt Positivo encontrado (ID: {pos})")
            else:
                print(f"     ❌ Prompt Positivo NO encontrado (o no conectado)")

    else:
        print("❌ FAIL: Faltan workflows")
    
    print("\n" + "=" * 60)
    print("🏁 VERIFICACIÓN COMPLETADA")

if __name__ == "__main__":
    asyncio.run(test_features())
