import urllib.request
import urllib.error
import json
import sys

COMFYUI_URL = "http://127.0.0.1:8188"

def check_comfy_connection():
    print(f"📡 Verificando conexión con ComfyUI en {COMFYUI_URL}...")
    try:
        with urllib.request.urlopen(f"{COMFYUI_URL}/system_stats") as response:
            if response.status == 200:
                print("✅ Conexión EXITOSA.")
                return True
    except urllib.error.URLError:
        print("❌ ERROR: No se puede conectar a ComfyUI.")
        print("   -> Asegúrate de que ComfyUI esté corriendo.")
        print(f"   -> Verifica que la URL sea correcta: {COMFYUI_URL}")
        return False
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        return False

def get_comfy_object_info():
    try:
        with urllib.request.urlopen(f"{COMFYUI_URL}/object_info") as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"❌ Error obteniendo info de objetos: {e}")
        return {}

def check_models(object_info):
    print("\n🔍 Verificando Modelos requeridos por tus workflows...")
    
    # Checkpoints
    required_checkpoints = ["realvisxlV50_v50LightningBakedvae.safetensors", "v1-5-pruned-emaonly.ckpt"]
    available_checkpoints = []
    
    if "CheckpointLoaderSimple" in object_info:
        available_checkpoints = object_info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
    
    print(f"  📂 Checkpoints disponibles en ComfyUI: {len(available_checkpoints)}")
    for ckpt in required_checkpoints:
        if ckpt in available_checkpoints:
             print(f"     ✅ Encontrado: {ckpt}")
        else:
             print(f"     ❌ FALTANTE: {ckpt}")
             print("        (Debes descargarlo y ponerlo en ComfyUI/models/checkpoints/)")

    # LoRAs
    required_loras = ["SDXL-Battlemaps.safetensors", "dnd_character_portraits_by_caith.safetensors"]
    available_loras = []
    
    if "LoraLoader" in object_info:
        available_loras = object_info["LoraLoader"]["input"]["required"]["lora_name"][0]
        
    print(f"\n  📂 LoRAs disponibles en ComfyUI: {len(available_loras)}")
    for lora in required_loras:
        if lora in available_loras:
             print(f"     ✅ Encontrado: {lora}")
        else:
             print(f"     ❌ FALTANTE: {lora}")
             print("        (Debes descargarlo y ponerlo en ComfyUI/models/loras/)")

if __name__ == "__main__":
    if check_comfy_connection():
        info = get_comfy_object_info()
        check_models(info)
        print("\n💡 Si falta algún modelo, ComfyUI rechazará el workflow.")
    else:
        sys.exit(1)
