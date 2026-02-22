
import asyncio
import logging
from app.components.ai.skill_images import ImageGeneratorSkill
from app.components.ai.comfy_client import ComfyClient

# Configurar logging a stdout
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("skill_images")
logger.setLevel(logging.DEBUG)

    print("🚀 Iniciando Test de Generación", flush=True)
    
    # Mock Manager
    class MockManager:
        async def send_to_session(self, session_id, data):
            print(f"📡 [MOCK MANAGER] Enviando a {session_id}: {data}", flush=True)

    # 1. Setup
    client = ComfyClient()
    client.timeout = 5 # Timeout corto para test
    manager = MockManager()
    skill = ImageGeneratorSkill(client, manager)
    
    # 2. Test Cases
    test_cases = [
        ("Llegáis a una cueva oscura.", "MAPA (Narrativa)"),
        ("Texto irrelevante.", "MAPA (Visual Prompt)", "dark cave entrance, fantasy painting", None),
        ("Texto irrelevante.", "RETRATO (Visual Prompt)", "fantasy portrait of a wizard", None),
        ("Texto escena 2.", "MAPA (Scene ID)", "castle ruins", 2)
    ]
    
    session_id = "test_session"
    
    for item in test_cases:
        if len(item) == 4:
            text, expected, vis_prompt, scene_id = item
            print(f"\n🧪 Probando Scene ID: {scene_id} (Esperado: {expected})")
            await skill.process_narrative(text, session_id, visual_prompt=vis_prompt, scene_id=scene_id)
        elif len(item) == 3:
            text, expected, vis_prompt = item
            print(f"\n🧪 Probando Visual Prompt: '{vis_prompt}' (Esperado: {expected})")
            await skill.process_narrative(text, session_id, visual_prompt=vis_prompt)
        else:
            text, expected = item
            print(f"\n🧪 Probando Narrativa: '{text}' (Esperado: {expected})", flush=True)
            await skill.process_narrative(text, session_id)
        
    print("\n✅ Test finalizado. Revisa los logs arriba.")

if __name__ == "__main__":
    asyncio.run(test_generation())
