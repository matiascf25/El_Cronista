# 🔄 GUÍA DE MIGRACIÓN - CRONISTA V80 → V80.1

## Resumen de Cambios

Has recibido **5 archivos nuevos** y **3 archivos actualizados**:

### 📄 Archivos NUEVOS (agregar a tu proyecto):
1. ✨ `logger.py` - Sistema de logging
2. ✨ `.env.example` - Template de configuración
3. ✨ `requirements.txt` - Dependencias actualizadas
4. ✨ `README_LOGGING.md` - Documentación completa
5. ✨ `.gitignore` - Protección de archivos sensibles
6. ✨ `test_logging.py` - Script de prueba

### 🔧 Archivos ACTUALIZADOS (reemplazar):
1. 🔄 `utils.py` - Con logging completo
2. 🔄 `main.py` - Con logging y middleware
3. 🔄 `systems.py` - Con logging en combate/journal

### 📦 Archivos SIN CAMBIOS (no tocar):
- `config.py` ✓
- `models.py` ✓
- `dm_screen.html` ✓
- `launcher.html` ✓
- `player_screen.html` ✓

---

## 🚀 Migración en 3 Pasos

### Paso 1: Copiar Archivos Nuevos

```bash
# Desde donde descargaste los archivos nuevos:
cp logger.py /tu/proyecto/cronista/
cp .env.example /tu/proyecto/cronista/
cp requirements.txt /tu/proyecto/cronista/
cp README_LOGGING.md /tu/proyecto/cronista/
cp .gitignore /tu/proyecto/cronista/
cp test_logging.py /tu/proyecto/cronista/
```

### Paso 2: Respaldar y Reemplazar Archivos Actualizados

```bash
# Ir a tu directorio del proyecto
cd /tu/proyecto/cronista/

# IMPORTANTE: Hacer backup primero
cp utils.py utils.py.backup
cp main.py main.py.backup
cp systems.py systems.py.backup

# Copiar versiones nuevas
cp /ruta/descarga/utils.py .
cp /ruta/descarga/main.py .
cp /ruta/descarga/systems.py .
```

### Paso 3: Configurar e Instalar

```bash
# 1. Crear archivo .env desde el template
cp .env.example .env

# 2. Editar .env con tu configuración
nano .env  # o usa tu editor favorito

# 3. Instalar dependencias nuevas
pip install -r requirements.txt

# 4. Probar que todo funciona
python test_logging.py
```

---

## ⚙️ Configuración Mínima de .env

Edita `.env` con estos valores:

```env
# IA
OLLAMA_URL=http://localhost:11434/api/generate
MODELO=mistral-nemo
OLLAMA_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
CONSOLE_LOG_LEVEL=WARNING

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

---

## ✅ Verificación Post-Migración

### 1. Estructura de Archivos

Tu proyecto debería verse así:

```
cronista_v80/
├── logger.py              # ✨ NUEVO
├── .env.example           # ✨ NUEVO
├── .env                   # ✨ NUEVO (crear desde .env.example)
├── .gitignore             # ✨ NUEVO
├── requirements.txt       # ✨ NUEVO
├── README_LOGGING.md      # ✨ NUEVO
├── test_logging.py        # ✨ NUEVO
├── utils.py               # 🔄 ACTUALIZADO
├── main.py                # 🔄 ACTUALIZADO
├── systems.py             # 🔄 ACTUALIZADO
├── config.py              # ✓ Sin cambios
├── models.py              # ✓ Sin cambios
├── templates/
│   ├── launcher.html      # ✓ Sin cambios
│   ├── dm_screen.html     # ✓ Sin cambios
│   └── player_screen.html # ✓ Sin cambios
└── partidas_guardadas/
```

### 2. Ejecutar Test de Logging

```bash
python test_logging.py
```

**Salida esperada:**

```
============================================================
🧪 TEST DE SISTEMA DE LOGGING
============================================================

1. Verificando archivos...
   ✓ logger.py
   ✓ config.py
   ✓ utils.py
   ✓ systems.py
   ✓ main.py

2. Importando módulo de logging...
   ✓ Módulo logger importado correctamente

3. Creando logger de prueba...
   ✓ Logger 'test' creado

4. Probando niveles de logging...
   ✓ DEBUG
   ✓ INFO
   ✓ WARNING
   ✓ ERROR

5. Verificando directorio de logs...
   ✓ Directorio logs/ existe
   ✓ 1 archivo(s) de log encontrado(s):
     - test.log (450 bytes)

...

✅ TODOS LOS TESTS PASARON
```

### 3. Ejecutar la Aplicación

```bash
# Asegúrate de que Ollama está corriendo
ollama serve

# En otra terminal, ejecuta el servidor
python main.py
```

**Salida esperada:**

```
============================================================
🎲 CRONISTA V80.1 (CON LOGGING MEJORADO)
============================================================
DM: http://localhost:8000/
PLAYER: http://0.0.0.0:8000/player
Logs: ./logs/
============================================================
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Verificar Logs

```bash
# Ver log principal en tiempo real
tail -f logs/main.log

# Crear una nueva aventura y observar los logs
# (En otra terminal, abre http://localhost:8000/ y crea una aventura)

# Deberías ver algo como:
# 2026-02-09 14:30:15 | INFO     | main     | new_game        | 📝 Iniciando generación de nueva aventura
# 2026-02-09 14:30:15 | INFO     | utils    | crear_datos_aventura | 🎲 Iniciando generación de aventura
```

---

## 🔍 Comparación: Antes vs Ahora

### ❌ ANTES (V80)

```python
# utils.py - Sin logging
def generar_con_ia(task_prompt, json_mode=True):
    try:
        r = requests.post(OLLAMA_URL, json={...})
        return r.json()['response']
    except:
        return None  # ¿Qué falló? No lo sabemos
```

### ✅ AHORA (V80.1)

```python
# utils.py - Con logging detallado
def generar_con_ia(task_prompt, json_mode=True):
    logger.info(f"Generando contenido con IA (JSON={json_mode})")
    
    try:
        response = requests.post(OLLAMA_URL, json={...}, timeout=60)
        response.raise_for_status()
        
        logger.info(f"✓ Respuesta recibida ({len(text)} caracteres)")
        return data
        
    except requests.Timeout:
        logger.error(f"Timeout al contactar Ollama (60s): {OLLAMA_URL}")
        return None
        
    except requests.ConnectionError:
        logger.error(f"No se pudo conectar a Ollama: {OLLAMA_URL}")
        logger.warning("Verifica que Ollama esté corriendo")
        return None
```

**Ahora sabes EXACTAMENTE qué pasó y por qué.**

---

## 📊 Nueva Funcionalidad

### Ver Logs en Tiempo Real

```bash
# Durante una sesión de juego
tail -f logs/main.log
```

### Buscar Errores

```bash
# Ver todos los errores
grep ERROR logs/*.log

# Ver errores de las últimas 24 horas
find logs/ -mtime -1 -name "*.log" -exec grep ERROR {} +
```

### Debugging de Problemas

```bash
# Si el combate falla
tail logs/combat.log

# Si la generación de aventuras falla
tail logs/utils.log

# Si hay problemas de conexión
tail logs/websocket.log
```

---

## 🆘 Troubleshooting de Migración

### Problema: "ModuleNotFoundError: No module named 'logger'"

**Causa**: No copiaste `logger.py` al directorio correcto

**Solución**:
```bash
# Verifica que logger.py esté en el mismo directorio que main.py
ls -la logger.py
```

---

### Problema: "Error loading .env file"

**Causa**: No creaste el archivo `.env`

**Solución**:
```bash
cp .env.example .env
nano .env  # Editar con tus valores
```

---

### Problema: "Permission denied: logs/"

**Causa**: Sin permisos de escritura

**Solución**:
```bash
mkdir -p logs
chmod 755 logs
```

---

### Problema: La app funciona pero no veo logs

**Causa**: `LOG_LEVEL` muy alto

**Solución**: Editar `.env`:
```env
LOG_LEVEL=DEBUG  # Temporal, para ver todo
```

---

## 🎯 Beneficios Inmediatos

Después de migrar, tendrás:

✅ **Debugging 10x más rápido**: Sabes exactamente qué falló y dónde
✅ **Monitoreo en tiempo real**: `tail -f logs/main.log`
✅ **Historial completo**: Todos los eventos quedan registrados
✅ **Stack traces**: Errores con contexto completo
✅ **Configuración flexible**: Cambia niveles sin editar código
✅ **Logs rotados**: No se llenan el disco

---

## 📋 Checklist Final

Marca cada paso al completarlo:

- [ ] Copié todos los archivos NUEVOS
- [ ] Reemplacé los 3 archivos ACTUALIZADOS
- [ ] Creé `.env` desde `.env.example`
- [ ] Instalé dependencias: `pip install -r requirements.txt`
- [ ] Ejecuté `python test_logging.py` exitosamente
- [ ] Verifiqué que se crea el directorio `logs/`
- [ ] Ejecuté `python main.py` sin errores
- [ ] Probé crear una aventura y vi los logs

---

**¡Listo! Ahora tienes logging profesional en CRONISTA V80.1** 🎉

Si tienes algún problema, revisa `README_LOGGING.md` para documentación completa.
