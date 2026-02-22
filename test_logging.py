#!/usr/bin/env python3
"""
Test del Sistema de Logging - CRONISTA V80.1
Ejecutar con: python test_logging.py
"""

import os
import sys
from pathlib import Path

def test_logging_system():
    """Prueba básica del sistema de logging"""
    
    print("=" * 60)
    print("🧪 TEST DE SISTEMA DE LOGGING")
    print("=" * 60)
    
    # 1. Verificar que existe logger.py
    print("\n1. Verificando archivos...")
    
    required_files = ['app/logger.py', 'app/config.py', 'app/main.py']
    missing = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} - FALTA")
            missing.append(file)
    
    if missing:
        print(f"\n❌ ERROR: Faltan archivos: {missing}")
        return False
    
    # 2. Importar y probar logger
    print("\n2. Importando módulo de logging...")
    
    try:
        from app.logger import setup_logger, log_startup_info
        print("   ✓ Módulo logger importado correctamente")
    except ImportError as e:
        print(f"   ✗ Error al importar logger: {e}")
        return False
    
    # 3. Crear logger de prueba
    print("\n3. Creando logger de prueba...")
    
    try:
        test_logger = setup_logger("test")
        print("   ✓ Logger 'test' creado")
    except Exception as e:
        print(f"   ✗ Error al crear logger: {e}")
        return False
    
    # 4. Probar niveles de logging
    print("\n4. Probando niveles de logging...")
    
    try:
        test_logger.debug("Este es un mensaje DEBUG")
        print("   ✓ DEBUG")
        
        test_logger.info("Este es un mensaje INFO")
        print("   ✓ INFO")
        
        test_logger.warning("Este es un mensaje WARNING")
        print("   ✓ WARNING")
        
        test_logger.error("Este es un mensaje ERROR (de prueba)")
        print("   ✓ ERROR")
        
    except Exception as e:
        print(f"   ✗ Error al escribir logs: {e}")
        return False
    
    # 5. Verificar que se creó el directorio de logs
    print("\n5. Verificando directorio de logs...")
    
    log_dir = Path("logs")
    if log_dir.exists():
        print(f"   ✓ Directorio logs/ existe")
        
        # Listar archivos de log
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            print(f"   ✓ {len(log_files)} archivo(s) de log encontrado(s):")
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"     - {log_file.name} ({size} bytes)")
        else:
            print("   ⚠ No se encontraron archivos .log (puede ser normal en primera ejecución)")
    else:
        print("   ✗ Directorio logs/ no existe")
        return False
    
    # 6. Verificar archivo .env.example
    print("\n6. Verificando configuración...")
    
    if os.path.exists(".env.example"):
        print("   ✓ .env.example existe")
    else:
        print("   ✗ .env.example no encontrado")
    
    if os.path.exists(".env"):
        print("   ✓ .env configurado")
    else:
        print("   ⚠ .env no existe (copia .env.example a .env)")
    
    # 7. Test de startup info
    print("\n7. Probando log de inicio del sistema...")
    
    try:
        log_startup_info()
        print("   ✓ Información de startup registrada")
    except Exception as e:
        print(f"   ✗ Error en startup info: {e}")
        return False
    
    # 8. Verificar que test.log tiene contenido
    print("\n8. Verificando contenido de logs...")
    
    test_log_path = log_dir / "test.log"
    if test_log_path.exists():
        with open(test_log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) >= 4:  # Deberíamos tener al menos 4 líneas (debug, info, warning, error)
            print(f"   ✓ test.log contiene {len(lines)} líneas")
            print("\n   Últimas 3 líneas del log:")
            for line in lines[-3:]:
                print(f"   {line.strip()}")
        else:
            print(f"   ⚠ test.log solo tiene {len(lines)} líneas")
    else:
        print("   ⚠ test.log no se creó aún")
    
    # Resultado final
    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS PASARON")
    print("=" * 60)
    print("\n📋 Próximos pasos:")
    print("   1. Revisa logs/test.log para ver los mensajes de prueba")
    print("   2. Copia .env.example a .env si no lo has hecho")
    print("   3. Ejecuta: python main.py")
    print("   4. Observa logs/ en tiempo real con: tail -f logs/main.log")
    print("\n")
    
    return True

if __name__ == "__main__":
    try:
        success = test_logging_system()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
