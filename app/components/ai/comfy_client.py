
import json
import urllib.request
import urllib.parse
import uuid
import time
import os
import random
from typing import Dict, Any, Optional
from app.logger import setup_logger
from app.config import COMFYUI_URL, COMFYUI_TIMEOUT

logger = setup_logger("comfy_client")

class ComfyClient:
    def __init__(self):
        self.url = COMFYUI_URL
        self.timeout = COMFYUI_TIMEOUT
        self.workflows = self._load_workflows()

    def _load_workflows(self) -> Dict[str, Any]:
        """Carga los workflows desde archivos JSON locales."""
        workflows = {}
        try:
            base_dir = os.path.dirname(__file__)
            path_map = os.path.join(base_dir, "workflow_map.json")
            path_portrait = os.path.join(base_dir, "workflow_portrait.json")
            path_default = os.path.join(base_dir, "workflow_default.json")

            if os.path.exists(path_map):
                with open(path_map, "r") as f:
                    workflows["map_v1.json"] = json.load(f)
                    workflows["map"] = workflows["map_v1.json"] # Alias
            
            if os.path.exists(path_portrait):
                with open(path_portrait, "r") as f:
                    workflows["portrait"] = json.load(f)
            
            if os.path.exists(path_default):
                with open(path_default, "r") as f:
                    workflows["default"] = json.load(f)
                    
            logger.info(f"Workflows cargados: {list(workflows.keys())}")
        except Exception as e:
            logger.error(f"Error cargando workflows: {e}")
        return workflows

    def queue_prompt(self, prompt_workflow: Dict) -> Dict:
        """Envía un prompt a la cola de ComfyUI."""
        p = {"prompt": prompt_workflow, "client_id": str(uuid.uuid4())}
        data = json.dumps(p).encode('utf-8')
        try:
            req = urllib.request.Request(f"{self.url}/prompt", data=data)
            return json.loads(urllib.request.urlopen(req).read())
        except Exception as e:
            logger.error(f"Error enviando prompt a ComfyUI: {e}")
            raise

    def get_history(self, prompt_id: str) -> Dict:
        """Obtiene el historial de una ejecución."""
        try:
            with urllib.request.urlopen(f"{self.url}/history/{prompt_id}") as response:
                return json.loads(response.read())
        except Exception as e:
            # logger.warn(f"Error obteniendo historial: {e}") # Verbose polling
            return {}

    def get_image_url(self, filename: str, subfolder: str, folder_type: str) -> str:
        """Construye la URL para ver la imagen."""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        return f"{self.url}/view?{url_values}"

    async def send_request(self, prompt_text: str, workflow: str = "default") -> str:
        """
        Método de alto nivel para preparar y enviar un workflow.
        Retorna el prompt_id.
        """
        template = self.workflows.get(workflow, self.workflows.get("default"))
        if not template:
            raise ValueError(f"Workflow '{workflow}' no encontrado")

        # Copia profunda del workflow
        workflow_data = json.loads(json.dumps(template))
        
        # Inyectar prompt y semilla (Lógica de image_generator.py)
        self._inject_prompt_and_seed(workflow_data, prompt_text)
        
        response = self.queue_prompt(workflow_data)
        return response['prompt_id']

    def _inject_prompt_and_seed(self, workflow: Dict, prompt_text: str):
        """Lógica inteligente para modificar el workflow en memoria."""
        ksampler_id = None
        positive_node_id = None
        
        # 1. Buscar KSampler y setear semilla
        for node_id, node in workflow.items():
            if node.get("class_type") in ["KSampler", "KSamplerAdvanced"]:
                ksampler_id = node_id
                if "inputs" in workflow[node_id]:
                    workflow[node_id]["inputs"]["seed"] = random.randint(1, 1000000000000)
                    # Intentar buscar conexión a positivo
                    positive_input = workflow[node_id]["inputs"].get("positive")
                    if isinstance(positive_input, list) and len(positive_input) > 0:
                        positive_node_id = str(positive_input[0])
                break
        
        # 2. Setear Prompt Positivo
        text_set = False
        if positive_node_id and positive_node_id in workflow:
            if "inputs" in workflow[positive_node_id]:
                base_text = workflow[positive_node_id]["inputs"].get("text", "")
                # Concatenar para no perder el prompt base del JSON
                new_text = f"{base_text}, {prompt_text}" if base_text else prompt_text
                workflow[positive_node_id]["inputs"]["text"] = new_text
                text_set = True
        
        # Fallback: Buscar cualquier CLIPTextEncode si falla la conexión
        if not text_set:
            for node_id, node in workflow.items():
                if node.get("class_type") == "CLIPTextEncode":
                    if "inputs" in node and "text" in node["inputs"]:
                        workflow[node_id]["inputs"]["text"] = prompt_text
                        break
