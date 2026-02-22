import uvicorn
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Add current directory to path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 CRONISTA V80.1 - LAUNCHER SHIM")
    print("=" * 60)
    print("Iniciando aplicación modularizada desde app/main.py...")
    
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        log_level="info"
    )
