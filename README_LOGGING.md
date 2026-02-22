# 🎲 CRONISTA V80.1 - Sistema de Logging Mejorado

## 📋 Cambios Implementados

### ✅ Nueva Funcionalidad: Logging Completo

El sistema ahora incluye logging profesional con las siguientes características:

- **Logging por Módulo**: Cada componente tiene su propio logger
- **Rotación Automática**: Los archivos de log se rotan automáticamente (máx 5MB)
- **Niveles Configurables**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Logging a Archivo y Consola**: Doble salida configurable
- **Timestamps**: Todas las entradas tienen fecha/hora precisa
- **Manejo de Excepciones**: Stack traces completos para debugging

---

## 🚀 Instalación

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
# Copiar template de configuración
cp .env.example .env

# Editar .env con tus valores
nano .env
```

**Archivo `.env` mínimo:**

```env
# IA
OLLAMA_URL=http://localhost:11434/api/generate
MODELO=mistral-nemo

# Logging
LOG_LEVEL=INFO
CONSOLE_LOG_LEVEL=WARNING

# Servidor
HOST=0.0.0.0
PORT=8000
```

### 3. Asegurar que Ollama está corriendo

```bash
# En una terminal separada
ollama serve

# Descargar el modelo si no lo tienes
ollama pull mistral-nemo
```

### 4. Ejecutar la Aplicación

```bash
python main.py
```

---

## 📁 Estructura de Archivos

```
cronista_v80/
├── config.py           # Configuración y datos del juego
├── logger.py           # ⭐ NUEVO: Sistema de logging
├── main.py             # ⭐ ACTUALIZADO: API con logging
├── models.py           # Modelos Pydantic
├── systems.py          # ⭐ ACTUALIZADO: Sistemas con logging
├── utils.py            # ⭐ ACTUALIZADO: Utilidades con logging
├── requirements.txt    # ⭐ ACTUALIZADO: Dependencias
├── .env.example        # ⭐ NUEVO: Template de configuración
├── .env                # TUS configuraciones (NO subir a git)
├── templates/
│   ├── launcher.html
│   ├── dm_screen.html
│   └── player_screen.html
├── logs/               # ⭐ NUEVO: Directorio de logs (generado automáticamente)
│   ├── main.log
│   ├── utils.log
│   ├── combat.log
│   ├── journal.log
│   ├── websocket.log
│   └── system.log
└── partidas_guardadas/
```

---

## 📊 Niveles de Logging

### Configuración en `.env`

```env
# LOG_LEVEL: Nivel mínimo para archivos de log
# Opciones: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# CONSOLE_LOG_LEVEL: Nivel mínimo para salida en consola
# Recomendado: WARNING (para no saturar la terminal)
CONSOLE_LOG_LEVEL=WARNING
```

### ¿Qué significa cada nivel?

| Nivel    | Cuándo usar | Ejemplo |
|----------|-------------|---------|
| **DEBUG** | Debugging detallado | "Modificador calculado: 16 → +3" |
| **INFO** | Operaciones normales | "✓ Personaje sanitizado: Thorgrim" |
| **WARNING** | Advertencias recuperables | "Stats faltantes, generando aleatorios" |
| **ERROR** | Errores que afectan funcionalidad | "Error parseando JSON de IA" |
| **CRITICAL** | Fallos graves del sistema | "Base de datos no disponible" |

---

## 🔍 Cómo Usar los Logs

### Ver Logs en Tiempo Real

```bash
# Ver todos los logs del sistema principal
tail -f logs/main.log

# Ver solo errores
tail -f logs/main.log | grep ERROR

# Ver logs de combate
tail -f logs/combat.log

# Ver múltiples archivos
tail -f logs/*.log
```

### Buscar Errores Específicos

```bash
# Buscar todos los errores en los últimos logs
grep -r "ERROR" logs/

# Buscar por sesión específica
grep "session_123" logs/*.log

# Buscar tiradas de dados
grep "🎲" logs/main.log
```

### Limpiar Logs Antiguos

```bash
# Eliminar todos los logs
rm logs/*.log

# Eliminar logs de más de 7 días
find logs/ -name "*.log" -mtime +7 -delete
```

---

## 🐛 Debugging con Logs

### Escenario 1: La IA no responde

**Síntomas**: El oráculo o la generación de aventuras se queda colgada

**Debugging**:

```bash
# Ver logs de utils (donde está la función de IA)
tail -f logs/utils.log

# Buscar timeouts
grep "Timeout" logs/utils.log
```

**Logs esperados**:
```
2026-02-09 14:30:15 | INFO     | utils               | generar_con_ia  | Generando contenido con IA (JSON=True)
2026-02-09 14:30:45 | INFO     | utils               | generar_con_ia  | ✓ Respuesta recibida de Ollama (1234 caracteres)
```

**Si ves**:
```
2026-02-09 14:30:15 | ERROR    | utils               | generar_con_ia  | Timeout al contactar Ollama (60s)
```

**Solución**: Aumentar `OLLAMA_TIMEOUT` en `.env`:
```env
OLLAMA_TIMEOUT=120
```

---

### Escenario 2: Error en Combate

**Síntomas**: El combate no inicia o crashea

**Debugging**:

```bash
tail -f logs/combat.log
```

**Logs esperados**:
```
2026-02-09 15:20:10 | INFO     | combat              | start_combat    | ⚔️ Iniciando combate - Sesión: default_session
2026-02-09 15:20:10 | INFO     | combat              | start_combat    | PJs: 4, Grupos enemigos: 2
2026-02-09 15:20:10 | DEBUG    | combat              | start_combat    | PJ agregado: Thorgrim (Ini: 18)
```

**Si ves**:
```
2026-02-09 15:20:10 | ERROR    | combat              | start_combat    | PJ con datos incompletos: 'hp'
```

**Solución**: Verificar que los PJs tienen todos los campos necesarios

---

### Escenario 3: WebSocket no conecta

**Debugging**:

```bash
tail -f logs/websocket.log
```

**Logs esperados**:
```
2026-02-09 16:00:00 | INFO     | websocket           | connect         | ✓ Cliente conectado - Sesión: default_session
2026-02-09 16:00:05 | DEBUG    | websocket           | send_to_session | Mensaje enviado a default_session: scene
```

---

## 🎯 Ejemplos de Uso del Logger

### En tu propio código

```python
from logger import setup_logger

# Crear logger para tu módulo
logger = setup_logger("mi_modulo")

# Usar el logger
logger.debug("Información de debugging")
logger.info("Operación exitosa")
logger.warning("Advertencia: algo inusual")
logger.error("Error recuperable")
logger.critical("Error crítico del sistema")

# Con información de excepción
try:
    # ... código que puede fallar
    resultado = funcion_peligrosa()
except Exception as e:
    logger.error(f"Error en función: {e}", exc_info=True)
    # exc_info=True incluye el stack trace completo
```

---

## 🔧 Configuración Avanzada

### Cambiar Formato de Logs

Editar `logger.py`:

```python
# Formato actual
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s"

# Formato simplificado
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

# Formato con archivo y línea
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
```

### Cambiar Tamaño de Rotación

En `logger.py`, función `setup_logger()`:

```python
file_handler = RotatingFileHandler(
    LOG_DIR / f"{name}.log",
    maxBytes=10 * 1024 * 1024,  # 10 MB en lugar de 5 MB
    backupCount=5,               # Mantener 5 backups en lugar de 3
    encoding='utf-8'
)
```

---

## 📈 Monitoreo en Producción

### Ver Métricas en Tiempo Real

```bash
# Contador de errores por minuto
watch -n 60 'grep ERROR logs/*.log | wc -l'

# Últimas 20 líneas de cada log
watch -n 5 'tail -n 20 logs/main.log'
```

### Alertas Simples

```bash
# Script de alerta por email (ejemplo básico)
#!/bin/bash
ERROR_COUNT=$(grep ERROR logs/*.log | wc -l)
if [ $ERROR_COUNT -gt 10 ]; then
    echo "ALERTA: $ERROR_COUNT errores detectados" | mail -s "Cronista Alert" admin@example.com
fi
```

---

## 🚨 Troubleshooting

### Problema: Los logs no se crean

**Causa**: Permisos de escritura

**Solución**:
```bash
mkdir -p logs
chmod 755 logs
```

---

### Problema: Logs muy grandes

**Causa**: LOG_LEVEL=DEBUG genera mucha información

**Solución**: Cambiar a INFO en `.env`:
```env
LOG_LEVEL=INFO
```

---

### Problema: No veo logs en la consola

**Causa**: CONSOLE_LOG_LEVEL muy alto

**Solución**: Bajar el nivel en `.env`:
```env
CONSOLE_LOG_LEVEL=INFO
```

---

## 📝 Best Practices

### ✅ DO (Hacer)

- Revisar logs después de cada sesión importante
- Usar `logger.info()` para eventos importantes
- Usar `logger.debug()` para información de debugging
- Incluir `exc_info=True` en bloques catch
- Mantener LOG_LEVEL=INFO en producción

### ❌ DON'T (No hacer)

- No hacer `print()` - usa `logger` en su lugar
- No ignorar warnings - investigarlos
- No dejar DEBUG activo en producción (muy verboso)
- No eliminar logs antes de revisar errores
- No hardcodear configuración - usar `.env`

---

## 🎓 Siguientes Pasos

1. **Familiarízate con los logs**: Ejecuta una sesión y observa `logs/main.log`
2. **Ajusta niveles**: Experimenta con diferentes `LOG_LEVEL`
3. **Monitorea en tiempo real**: Usa `tail -f` durante el desarrollo
4. **Debugging efectivo**: Cuando algo falle, revisa los logs primero

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa `logs/main.log` y `logs/system.log`
2. Busca líneas con `ERROR` o `CRITICAL`
3. Copia el stack trace completo
4. Verifica configuración en `.env`

---

**¡El logging está listo! Ahora puedes ver exactamente qué está pasando en tu aplicación en todo momento.** 🚀
