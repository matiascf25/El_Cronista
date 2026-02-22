
import asyncio
import time
from typing import Dict, Optional, Any
from app.logger import setup_logger
from app.components.ai.comfy_client import ComfyClient
from app.components.ai.client import generar_con_ia

logger = setup_logger("skill_images")

PROMPT_MAESTRO_SYSTEM = """
Actúa como un experto en Prompt Engineering para SDXL Lightning. Tu objetivo es recibir descripciones de una partida de D&D y devolver un JSON con dos campos: 'positive_prompt' (en inglés, detallado, incluyendo estilos de pintura fantástica) y 'negative_prompt' (evitando deformidades y texto). Si la descripción es un lugar, prioriza la vista cenital. Si es una persona, prioriza el encuadre de busto.
"""

class ImageGeneratorSkill:
    def __init__(self, comfy_client: ComfyClient, manager_instance: Any):
        self.comfy_client = comfy_client
        self.manager = manager_instance
        self.map_trigger = "zovya, (top-down battlemap:1.3), dnd style, (square grid overlay:1.2)"
        self.portrait_trigger = "(fantasy portrait:1.2), looking at camera, cinematic lighting, 8k"
        # Semáforo: max 1 generación simultánea para evitar OOM
        self._semaphore = asyncio.Semaphore(1)

    async def process_narrative(self, ai_output: str, session_id: str, visual_prompt: Optional[str] = None, scene_id: Optional[Any] = None):
        """
        Analiza el texto de Nemo Mistral y dispara la generación.
        Si hay visual_prompt (de generator.py), se prioriza.
        """
        try:
            logger.info(f"🤔 Analizando narrativa para imágenes ({len(ai_output)} chars) [SceneID: {scene_id}]")
            
            # Prioridad: Visual Prompt explícito (viene del generador de historia)
            if visual_prompt:
                logger.info(f"  -> Usando Visual Prompt explícito: {visual_prompt[:50]}...")
                # Por lo general, los visual prompts de escenas son ambientales -> MAPA
                if any(k in visual_prompt.lower() for k in ["portrait", "face", "character", "personaje", "rostro"]):
                     await self.generate_portrait(visual_prompt, session_id, scene_id=scene_id)
                else:
                     await self.generate_map(visual_prompt, session_id, scene_id=scene_id)
                return

            # Fallback: Análisis de narrativa
            narrative_lower = ai_output.lower()
            
            map_keywords = [
                "llegáis a", "entráis en", "el lugar es", "la habitación", "el bosque", "la cueva",
                "el camino", "la torre", "el calabozo", "las ruinas", "el templo", "mapa", "entorno",
                "castillo", "ciudad", "pueblo", "montaña", "pantano", "desierto", "mar", "barco"
            ]
            
            portrait_keywords = [
                "aparece", "dice:", "grita", "susurra", "un hombre", "una mujer", "npc",
                "el encapuchado", "la elfa", "el enano", "el orco", "frente a vosotros", "rostro",
                "mirada", "ojos", "sonrisa", "gesto", "viste", "lleva"
            ]
            
            if any(kw in narrative_lower for kw in map_keywords):
                logger.info("  -> Detectado: MAPA 🗺️")
                await self.generate_map(ai_output, session_id, scene_id=scene_id)
                return
                
            elif any(kw in narrative_lower for kw in portrait_keywords):
                logger.info("  -> Detectado: RETRATO 👤")
                await self.generate_portrait(ai_output, session_id, scene_id=scene_id)
                return
            
            logger.info("  -> Ningún trigger de imagen detectado.")
            
        except Exception as e:
            logger.error(f"Error en process_narrative: {e}", exc_info=True)

    async def _refine_prompt_with_llm(self, description: str) -> Dict[str, str]:
        """Usa el 'Prompt Maestro' para obtener prompts optimizados."""
        try:
            result = generar_con_ia(
                task_prompt=f"Descripción de la escena: {description}",
                json_mode=True,
                contexto=PROMPT_MAESTRO_SYSTEM
            )
            
            if isinstance(result, dict) and "positive_prompt" in result:
                return result
            else:
                logger.warning("Falló la generación de prompt maestro, usando fallback.")
                return {"positive_prompt": description, "negative_prompt": ""}
        except Exception as e:
            logger.error(f"Error en Prompt Maestro: {e}")
            return {"positive_prompt": description, "negative_prompt": ""}

    async def generate_map(self, description: str, session_id: str, scene_id: Optional[Any] = None):
        """Genera un mapa de batalla (con semáforo anti-OOM)."""
        try:
            async with self._semaphore:
                logger.info(f"🗺️ Generando mapa para sesión {session_id} [SceneID: {scene_id}]")
                
                refined_prompt = f"{self.map_trigger}, {description}, highly detailed, 8k"
                
                prompt_id = await self.comfy_client.send_request(refined_prompt, workflow="map_v1.json")
                await self._wait_and_broadcast(prompt_id, session_id, "map", refined_prompt, scene_id=scene_id)
            
        except Exception as e:
            logger.error(f"Error generando mapa: {e}")

    async def generate_portrait(self, description: str, session_id: str, scene_id: Optional[Any] = None, pj_index: Optional[int] = None):
        """Genera un retrato de personaje (con semáforo anti-OOM)."""
        try:
            async with self._semaphore:
                logger.info(f"👤 Generando retrato para sesión {session_id} [PJ: {pj_index}]")
                
                refined_prompt = f"{self.portrait_trigger}, {description}, detailed face, 8k"
                
                prompt_id = await self.comfy_client.send_request(refined_prompt, workflow="portrait")
                await self._wait_and_broadcast(prompt_id, session_id, "portrait", refined_prompt, scene_id=scene_id, pj_index=pj_index)
            
        except Exception as e:
            logger.error(f"Error generando retrato: {e}")

    async def _wait_and_broadcast(self, prompt_id: str, session_id: str, image_type: str, prompt_text: str, scene_id: Optional[Any] = None, pj_index: Optional[int] = None):
        """Espera la imagen y notifica al cliente."""
        start_time = time.time()
        while time.time() - start_time < self.comfy_client.timeout:
            history = self.comfy_client.get_history(prompt_id)
            if prompt_id in history:
                outputs = history[prompt_id]['outputs']
                for node_id in outputs:
                    node_output = outputs[node_id]
                    if 'images' in node_output:
                        for image in node_output['images']:
                            filename = image['filename']
                            subfolder = image['subfolder']
                            folder_type = image['type']
                            
                            image_url = self.comfy_client.get_image_url(filename, subfolder, folder_type)
                            
                            logger.info(f"✅ Imagen ({image_type}) lista: {filename}")
                            
                            # Broadcast usando el manager
                            payload = {
                                "type": "image_generated",
                                "subtype": image_type,
                                "url": image_url,
                                "prompt": prompt_text
                            }
                            if scene_id is not None:
                                payload["scene_id"] = scene_id
                            if pj_index is not None:
                                payload["pj_index"] = pj_index
                                
                            await self.manager.send_to_session(session_id, payload)
                            return
            await asyncio.sleep(2) # Polling no bloqueante
        
        logger.warning(f"⏰ Timeout esperando imagen {image_type} (prompt_id: {prompt_id})")
