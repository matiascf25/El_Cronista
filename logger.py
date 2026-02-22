"""
Sistema de Logging Centralizado para CRONISTA V80
Configuración de logs con rotación automática y niveles personalizables
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

# Crear directorio de logs si no existe
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Nivel de logging desde variable de entorno (default: INFO)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Formato detallado para logs
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str) -> logging.Logger:
    """
    Configura un logger con handlers para archivo y consola
    
    Args:
        name: Nombre del módulo (ej: 'utils', 'main', 'systems')
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVEL)
    
    # Formatter común
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Handler para archivo (con rotación)
    file_handler = RotatingFileHandler(
        LOG_DIR / f"{name}.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler para consola (solo WARNING y superior por defecto)
    console_handler = logging.StreamHandler(sys.stdout)
    console_level = os.getenv("CONSOLE_LOG_LEVEL", "WARNING").upper()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    
    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Logger para el sistema general
system_logger = setup_logger("system")

def log_startup_info():
    """Registra información del sistema al iniciar"""
    system_logger.info("=" * 60)
    system_logger.info("🎲 CRONISTA V80 - Sistema de Logging Inicializado")
    system_logger.info(f"Nivel de Log: {LOG_LEVEL}")
    system_logger.info(f"Directorio de Logs: {LOG_DIR.absolute()}")
    system_logger.info("=" * 60)

def log_request(method: str, path: str, status: int, duration: float):
    """
    Log estandarizado para requests HTTP
    
    Args:
        method: Método HTTP (GET, POST, etc)
        path: Ruta del endpoint
        status: Código de estado HTTP
        duration: Duración en segundos
    """
    level = logging.INFO if status < 400 else logging.WARNING
    system_logger.log(
        level,
        f"{method} {path} - Status: {status} - Duration: {duration:.3f}s"
    )
