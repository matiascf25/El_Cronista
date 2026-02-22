import uvicorn
import os
import json
import random
import time
from datetime import datetime
from typing import Optional, Dict, List, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import requests
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Módulos Propios (Refactorizados)
from app.config import ESTILOS, MICRO_SETTINGS, SAVE_DIR, OLLAMA_URL, MODELO, SYSTEM_INSTRUCTIONS
from app.models import OracleRequest, SaveRequest, DiceRollRequest, CombatAction, JournalEntryRequest, NewGameRequest
from app.state import manager, journal, combat_tracker, SESSIONS, vtt_state
from app.components.dnd.generator import crear_datos_aventura
from app.components.dnd.dice import evaluar_formula_dados
from app.components.combat.balance import adjust_encounter
from app.components.ai.client import sanitizar_texto
from app.logger import setup_logger, log_startup_info, log_request
from app.components.ai.memory import get_narrative_context
from app.state import image_skill
from fastapi import BackgroundTasks

# Base de datos
from app.database import init_db, get_session
from app.db_models import Campaign, JournalEntryDB
from sqlmodel import select
from app.components.dnd import library

# Logger para este módulo
logger = setup_logger("main")

# Inicializar FastAPI
app = FastAPI(
    title="CRONISTA V80",
    description="Sistema de gestión de campañas D&D 5e con IA",
    version="80.1"
)

# ============================================
# RATE LIMITING
# ============================================
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

logger.info("Rate limiting enabled (default: 100 req/min)")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates = Jinja2Templates(directory="templates")

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para registrar todas las requests HTTP"""
    start_time = time.time()
    
    # Log de request entrante
    logger.debug(f"→ {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log de respuesta
        log_request(request.method, request.url.path, response.status_code, duration)
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error procesando request {request.method} {request.url.path}: {e}", exc_info=True)
        log_request(request.method, request.url.path, 500, duration)
        
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Error interno del servidor"}
        )

# Handler global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura todas las excepciones no manejadas"""
    logger.error(f"Excepción no capturada: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Error inesperado en el servidor",
            "detail": str(exc) if os.getenv("DEBUG", "False") == "True" else None
        }
    )

# --- RUTAS DE PÁGINAS ---

@app.get("/", response_class=HTMLResponse)
async def launcher(request: Request):
    """Página de inicio/launcher"""
    logger.info("Acceso a página launcher")
    return templates.TemplateResponse("launcher.html", {"request": request})

@app.get("/dm", response_class=HTMLResponse)
async def dm_interface(request: Request):
    """Interfaz del Dungeon Master"""
    logger.info("Acceso a interfaz DM")
    
    sid = "default_session"
    
    if sid not in SESSIONS or "adventure" not in SESSIONS[sid]:
        logger.warning("Intento de acceder a DM sin aventura activa, redirigiendo")
        return RedirectResponse(url="/")
    
    adv = SESSIONS[sid]["adventure"]
    estilo = SESSIONS[sid].get("current_style", ESTILOS[0])
    
    logger.debug(f"Cargando aventura: {adv.get('historia', {}).get('titulo', 'Sin título')}")
    
    return templates.TemplateResponse("dm_screen.html", {
        "request": request,
        "adv": adv,
        "estilo": estilo,
        "estilos_todos": ESTILOS
    })

@app.get("/player", response_class=HTMLResponse)
async def player_interface(request: Request):
    """Interfaz de visualización para jugadores"""
    logger.info("Acceso a interfaz jugador")
    
    sid = "default_session"
    pjs_json = "[]"
    
    # Intentar cargar los PJs de la sesión actual
    if sid in SESSIONS and "adventure" in SESSIONS[sid]:
        pjs_json = json.dumps(SESSIONS[sid]["adventure"]["pjs"])
        logger.debug(f"Cargando {len(SESSIONS[sid]['adventure']['pjs'])} personajes")
    else:
        logger.warning("No hay aventura activa para mostrar personajes")
    
    return templates.TemplateResponse("player_screen.html", {
        "request": request, 
        "pjs_data": pjs_json
    })

# --- RUTAS DE API ---

async def run_async_generation(sid: str, setting: str, estilo: Dict[str, str], nivel: int, background_tasks: BackgroundTasks):
    """Wrapper para ejecutar la generación en background y guardar el resultado"""
    try:
        # 1. Generar (Async + Streaming)
        data = await crear_datos_aventura(
            session_id=sid, 
            setting=setting, 
            estilo=estilo, 
            nivel=nivel, 
            background_tasks=background_tasks,
            connection_manager=manager
        )
        
        if not data or 'pjs' not in data or 'historia' not in data:
            logger.error("Datos de aventura incompletos en background task")
            await manager.send_to_session(sid, {"type": "error", "message": "Fallo en generación"})
            return

        # 2. Guardar en Sesión
        if sid not in SESSIONS:
            SESSIONS[sid] = {}
        
        SESSIONS[sid]["adventure"] = data
        SESSIONS[sid]["current_style"] = estilo
        
        # 3. Registrar y Guardar DB
        journal.register_event(sid, "campaign_start", f"Aventura iniciada: {data['historia']['titulo']}")
        
        # Guardado en SQLite
        title = data['historia']['titulo']
        style_name = estilo.get("nombre", "")
        data_blob = json.dumps(SESSIONS[sid], ensure_ascii=False)
        
        with get_session() as db:
            stmt = select(Campaign).where(Campaign.session_id == sid)
            existing = db.exec(stmt).first()
            if existing:
                existing.title = title
                existing.style = style_name
                existing.data_json = data_blob
                existing.updated_at = datetime.utcnow()
                db.add(existing)
            else:
                db.add(Campaign(session_id=sid, title=title, style=style_name, data_json=data_blob))
            db.commit()

        logger.info(f"✅ Aventura BG completada y guardada: {title}")
        
        # 4. Notificar cliente para recargar/iniciar
        await manager.send_to_session(sid, {
            "type": "adventure_ready", 
            "title": title,
            "data": data # Opcional, si el cliente puede cargar sin reload
        })
        
    except Exception as e:
        logger.error(f"Error en background generation: {e}", exc_info=True)
        await manager.send_to_session(sid, {"type": "error", "message": f"Error crítico: {str(e)}"})


# ============================================
# PYDANTIC MODELS (Request Validation)
# ============================================

class NewGameRequest(BaseModel):
    """Request body for creating a new game/campaign"""
    setting: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Campaign setting description",
        example="Una ciudad gótica asediada por vampiros"
    )
    style: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Style name from ESTILOS config",
        example="HORROR GÓTICO"
    )
    nivel: int = Field(
        default=1,
        ge=1,
        le=20,
        description="Starting level for PCs"
    )
    
    @validator('style')
    def validate_style_exists(cls, v):
        from app.config import ESTILOS
        valid_styles = [e['nombre'] for e in ESTILOS]
        if v not in valid_styles:
            raise ValueError(f"Style must be one of: {', '.join(valid_styles)}")
        return v


class SaveGameRequest(BaseModel):
    """Request body for saving a game"""
    session_id: str = Field(..., min_length=1, max_length=100)
    aventura: Dict[str, Any] = Field(
        ...,
        description="Complete adventure data to save"
    )


class LoadGameRequest(BaseModel):
    """Query parameters for loading a game"""
    session_id: str = Field(..., min_length=1, max_length=100)


class OracleRequest(BaseModel):
    """Request body for Oracle AI enrichment"""
    session_id: str = Field(..., min_length=1, max_length=100)
    texto_origen: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text to enrich with AI"
    )
    tipo: str = Field(
        default="narrativa",
        pattern=r'^(narrativa|dialogo|descripcion|combate)$',
        description="Type of enrichment"
    )


class DiceRollRequest(BaseModel):
    """Request body for dice rolls"""
    session_id: str = Field(..., min_length=1, max_length=100)
    formula: str = Field(
        ...,
        pattern=r'^\d+d\d+([+-]\d+)?$',
        description="Dice formula (e.g., 2d6+3, 1d20)",
        example="1d20+5"
    )
    
    @validator('formula')
    def validate_reasonable_dice(cls, v):
        # Extract numbers
        import re
        match = re.match(r'^(\d+)d(\d+)', v)
        if match:
            num_dice = int(match.group(1))
            sides = int(match.group(2))
            if num_dice > 100:
                raise ValueError("Maximum 100 dice allowed")
            if sides > 1000:
                raise ValueError("Maximum 1000 sides allowed")
        return v


class CombatActionRequest(BaseModel):
    """Request body for combat actions"""
    session_id: str = Field(..., min_length=1, max_length=100)
    action: str = Field(
        ...,
        pattern=r'^(start|damage|heal|next|end)$',
        description="Combat action type"
    )
    target: Optional[str] = Field(
        None,
        max_length=100,
        description="Target combatant name (required for damage/heal)"
    )
    amount: Optional[int] = Field(
        None,
        ge=0,
        le=999,
        description="Damage or healing amount"
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional data for specific actions (e.g. start combat)"
    )
    
    @validator('target')
    def validate_target_for_action(cls, v, values):
        action = values.get('action')
        if action in ['damage', 'heal'] and not v:
            raise ValueError(f"target required for action '{action}'")
        return v
    
    @validator('amount')
    def validate_amount_for_action(cls, v, values):
        action = values.get('action')
        if action in ['damage', 'heal'] and v is None:
            raise ValueError(f"amount required for action '{action}'")
        return v


class JournalEntryRequest(BaseModel):
    """Request body for adding journal entries"""
    session_id: str = Field(..., min_length=1, max_length=100)
    event_type: str = Field(
        ...,
        pattern=r'^(roleplay|combat|discovery|rest|travel)$',
        description="Type of event"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Event description"
    )


# ─── VTT Models ──────────────────────────────────────────

class ProjectSceneRequest(BaseModel):
    """Request body for projecting a scene to VTT"""
    session_id: str = Field(..., min_length=1, max_length=100)
    scene_id: int = Field(
        ...,
        ge=0,
        le=4,
        description="Scene index (0-4 for 5 scenes)"
    )
    
    @validator('scene_id')
    def validate_scene_exists(cls, v, values):
        # Note: This validation happens at runtime in endpoint
        # Can't access SESSIONS here (circular import)
        return v


class CreateTokenRequest(BaseModel):
    """Request body for creating a VTT token"""
    session_id: str = Field(..., min_length=1, max_length=100)
    token_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique token identifier"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name for token"
    )
    x: int = Field(
        default=128,
        ge=0,
        le=768,
        description="X coordinate in pixels"
    )
    y: int = Field(
        default=128,
        ge=0,
        le=768,
        description="Y coordinate in pixels"
    )
    color: str = Field(
        default="#00ff00",
        pattern=r'^#[0-9A-Fa-f]{6}$',
        description="Hex color code",
        example="#00ff00"
    )
    img: Optional[str] = Field(
        None,
        description="URL for token image"
    )
    token_type: str = Field(
        default="pj",
        pattern=r'^(pj|enemigo)$',
        description="Token type: pj (player) or enemigo (enemy)"
    )


class DeleteTokenRequest(BaseModel):
    """Request body for deleting a token"""
    session_id: str = Field(..., min_length=1, max_length=100)
    token_id: str = Field(..., min_length=1, max_length=50)


class ClearMapRequest(BaseModel):
    """Request body for clearing all tokens from map"""
    session_id: str = Field(..., min_length=1, max_length=100)



# ... (imports remain same)

@app.post("/new")
@limiter.limit("3/minute")
async def new_game(request: Request, body: NewGameRequest, background_tasks: BackgroundTasks):
    """Crea una nueva aventura aleatoria (Async Background)"""
    logger.info("📝 Iniciando solicitud de aventura (Async)")
    
    try:
        nivel = body.nivel
        requested_setting = body.setting
        
        # Si no se pasó setting, elegir uno random
        setting = requested_setting if requested_setting else random.choice(MICRO_SETTINGS)
        
        # Buscar el estilo seleccionado en la configuración
        estilo_nombre = body.style
        estilo = next((e for e in ESTILOS if e['nombre'] == estilo_nombre), ESTILOS[0])
        sid = "default_session"
        
        logger.info(f"Setting: {setting} | Estilo: {estilo['nombre']} | Nivel: {nivel}")
        
        # Lanzar tarea en background
        background_tasks.add_task(run_async_generation, sid, setting, estilo, nivel, background_tasks)
        
        return {
            "status": "processing", 
            "message": "Generando aventura...", 
            "setting": setting,
            "style": estilo['nombre']
        }
        
    except Exception as e:
        logger.error(f"Error al iniciar aventura: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error al iniciar generación: {str(e)}"
        }

@app.post("/save")
@limiter.limit("20/minute")
async def save_game(request: Request, req: SaveGameRequest):
    """Guarda el estado actual de la partida en SQLite"""
    sid = req.session_id
    logger.info(f"💾 Guardando partida para sesión: {sid}")
    
    try:
        if sid not in SESSIONS:
            logger.warning(f"Sesión {sid} no existe")
            return {"status": "error", "message": "Sesión no encontrada"}
            
        # Preparar datos
        session_data = SESSIONS[sid]
        title = session_data.get("adventure", {}).get("historia", {}).get("titulo", "Sin Título")
        style = session_data.get("adventure", {}).get("estilo", {})
        style_name = style.get("nombre", "Unknown") if isinstance(style, dict) else "Unknown"
        
        # Serializar
        data_blob = json.dumps(session_data, ensure_ascii=False)
        
        # Guardar en DB
        with get_session() as db:
            # Buscar si ya existe
            stmt = select(Campaign).where(Campaign.session_id == sid)
            existing = db.exec(stmt).first()
            
            if existing:
                existing.title = title
                existing.style = style_name
                existing.data_json = data_blob
                existing.updated_at = datetime.utcnow()
                db.add(existing)
                logger.info(f"✅ Partida actualizada en DB (id={existing.id})")
            else:
                campaign = Campaign(
                    session_id=sid,
                    title=title,
                    style=style_name,
                    data_json=data_blob,
                )
                db.add(campaign)
                logger.info(f"✅ Partida creada en DB")
            
            db.commit()
        
        return {"status": "ok", "storage": "sqlite"}
        
    except Exception as e:
        logger.error(f"Error al guardar partida: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.get("/load")
@limiter.limit("60/minute")
async def load_game(request: Request, session_id: str = "default_session"):
    """Carga una partida guardada (SQLite primero, fallback a JSON legacy)"""
    logger.info(f"📂 Cargando partida para sesión: {session_id}")
    
    try:
        # 1. Intentar cargar desde SQLite
        with get_session() as db:
            stmt = select(Campaign).where(Campaign.session_id == session_id)
            campaign = db.exec(stmt).first()
            
            if campaign:
                data = json.loads(campaign.data_json)
                SESSIONS[session_id] = data
                logger.info(f"✅ Partida cargada desde SQLite (id={campaign.id})")
                return {"status": "ok", "source": "sqlite", "title": campaign.title}
        
        # 2. Fallback: Cargar desde JSON legacy
        fname = f"{SAVE_DIR}/partida_{session_id}.json"
        if os.path.exists(fname):
            with open(fname, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            SESSIONS[session_id] = data
            logger.info(f"✅ Partida cargada desde JSON legacy: {fname}")
            
            # Auto-migrar a SQLite
            title = "Importada"
            adventure = data.get("adventure", {})
            if isinstance(adventure, dict):
                historia = adventure.get("historia", {})
                if isinstance(historia, dict):
                    title = historia.get("titulo", "Importada")
            
            with get_session() as db:
                campaign = Campaign(
                    session_id=session_id,
                    title=title,
                    data_json=json.dumps(data, ensure_ascii=False),
                )
                db.add(campaign)
                db.commit()
                logger.info(f"🔄 Partida legacy auto-migrada a SQLite")
            
            return {"status": "ok", "source": "json_legacy", "migrated": True}
        
        logger.warning(f"No hay partida guardada para: {session_id}")
        return {"status": "error", "message": "No hay partida guardada"}
        
    except Exception as e:
        logger.error(f"Error al cargar partida: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.post("/oracle")
@limiter.limit("10/minute")
async def oracle(request: Request, req: OracleRequest, background_tasks: BackgroundTasks):
    """Expande texto narrativo usando IA"""
    logger.info(f"🔮 Oráculo invocado para sesión: {req.session_id}")
    
    try:
        # Sanitizar y validar
        texto_limpio = sanitizar_texto(req.texto_origen)
        
        if len(texto_limpio) > int(os.getenv("MAX_TEXT_LENGTH", "2000")):
            logger.warning(f"Texto demasiado largo para oráculo: {len(texto_limpio)} chars")
            return {
                "status": "error",
                "message": "Texto demasiado largo (máx 2000 caracteres)"
            }
        
        prompt = f"Expande este texto narrativo de D&D (3ra persona, español):\n{texto_limpio}"
        
        # Obtener memoria narrativa
        contexto = get_narrative_context(req.session_id)
        if contexto:
            logger.debug(f"Inyectando contexto narrativo ({len(contexto)} chars)")
        
        logger.debug(f"Enviando a Ollama: {len(prompt)} caracteres")
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO, 
                "prompt": f"{SYSTEM_INSTRUCTIONS}\n\nCONTEXTO:\n{contexto}\n\nTAREA:\n{prompt}", 
                "stream": False
            },
            timeout=int(os.getenv("OLLAMA_TIMEOUT", "60"))
        )
        response.raise_for_status()
        
        result = response.json().get('response', '')
        
        # Limpiar respuesta de bloques Markdown (```json ... ```)
        cleaned_result = result.strip()
        if cleaned_result.startswith("```"):
            # Eliminar primera línea (```json) y última (```)
            lines = cleaned_result.split('\n')
            if len(lines) >= 2:
                # Filtrar líneas de cierre
                if lines[0].startswith("```"): lines = lines[1:]
                if lines[-1].strip() == "```": lines = lines[:-1]
                cleaned_result = "\n".join(lines).strip()
        
        # Intentar parsear si es JSON
        try:
            if cleaned_result.startswith("{"):
                json_res = json.loads(cleaned_result)
                # Buscar campos comunes
                if "evento" in json_res and "descripcion" in json_res["evento"]:
                    result = json_res["evento"]["descripcion"]
                elif "descripcion" in json_res:
                    result = json_res["descripcion"]
                elif "narrativa" in json_res:
                    result = json_res["narrativa"]
                elif "response" in json_res:
                    result = json_res["response"]
                else:
                    # Fallback: Usar el primer valor string largo que encontremos
                    for v in json_res.values():
                        if isinstance(v, str) and len(v) > 50:
                            result = v
                            break
        except json.JSONDecodeError:
            pass # No es JSON, usar tal cual
        
        if not result:
            logger.error("Oráculo devolvió respuesta vacía")
            return {"status": "error", "message": "La IA no generó respuesta"}
        
        logger.info(f"✅ Oráculo completado: {len(result)} caracteres generados")
        
        return {"status": "ok", "new_text": result}
        
    except requests.Timeout:
        logger.error("Timeout en llamada a Oráculo")
        return {"status": "error", "message": "Timeout al conectar con IA"}
        
    except requests.RequestException as e:
        logger.error(f"Error de red en Oráculo: {e}")
        return {"status": "error", "message": "Error al conectar con IA"}
        
    except Exception as e:
        logger.error(f"Error en Oráculo: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.post("/combat")
@limiter.limit("120/minute")
async def combat_api(request: Request, action: CombatActionRequest):
    """Gestiona todas las acciones de combate"""
    sid = action.session_id
    action_type = action.action
    
    logger.info(f"⚔️ Acción de combate: {action_type} (sesión: {sid})")
    
    try:
        res = {}
        
        if action_type == "start":
            enemigos = action.data.get("enemigos", [])
            pjs = SESSIONS[sid]["adventure"]["pjs"]
            
            # Aplicar balanceo
            logger.info("Verificando balance del encuentro...")
            enemigos = adjust_encounter(enemigos, pjs)
            
            logger.info(f"Iniciando combate con {len(enemigos)} grupos de enemigos")
            
            res = combat_tracker.start_combat(sid, enemigos, pjs)
            journal.register_event(sid, "combat_start", "Combate iniciado")
            
        elif action_type == "next_turn":
            res = combat_tracker.next_turn(sid)
            logger.debug(f"Turno avanzado - Ronda {res.get('ronda', 0)}")
            
        elif action_type == "add_enemy":
            enemigo = action.data.get("enemigo")
            if not enemigo:
                raise ValueError("Datos del enemigo faltantes")
            res = combat_tracker.add_combatant(sid, enemigo)
            
        elif action_type == "damage":
            target = action.data.get("target")
            amount = int(action.data.get("amount", 0))
            
            logger.info(f"Aplicando {amount} daño a {target}")
            res = combat_tracker.apply_damage(sid, target, amount)
            
        elif action_type == "heal":
            target = action.data.get("target")
            amount = int(action.data.get("amount", 0))
            
            logger.info(f"Curando {amount} HP a {target}")
            res = combat_tracker.heal(sid, target, amount)
            
        elif action_type == "end":
            logger.info("Finalizando combate")
            res = combat_tracker.end_combat(sid)
            journal.register_event(sid, "combat_end", "Combate finalizado")
        
        else:
            logger.warning(f"Acción de combate no reconocida: {action_type}")
            return {"status": "error", "message": f"Acción no válida: {action_type}"}
        
        # Enviar actualización a todos los clientes conectados
        await manager.send_to_session(
            sid,
            {"type": "combat_update", "combat": combat_tracker.get_state(sid)}
        )
        
        return res
        
    except KeyError as e:
        logger.error(f"Clave faltante en datos de combate: {e}")
        return {"status": "error", "message": f"Datos incompletos: {e}"}
        
    except ValueError as e:
        logger.error(f"Valor inválido en combate: {e}")
        return {"status": "error", "message": f"Valor inválido: {e}"}
        
    except Exception as e:
        logger.error(f"Error en sistema de combate: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.post("/journal/add")
async def journal_add(entry: JournalEntryRequest):
    """Agrega un evento al journal de la sesión"""
    logger.info(f"📖 Agregando entrada al journal: {entry.event_type}")
    
    try:
        journal.register_event(entry.session_id, entry.event_type, entry.description)
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error al agregar entrada al journal: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.get("/journal/summary")
async def journal_get(session_id: str = "default_session"):
    """Obtiene el historial de eventos del journal"""
    logger.info(f"📖 Obteniendo journal para sesión: {session_id}")
    
    try:
        events = journal.get_log(session_id)
        logger.debug(f"Journal contiene {len(events)} eventos")
        
        return {"events": events}
        
    except Exception as e:
        logger.error(f"Error al obtener journal: {e}", exc_info=True)
        return {"events": []}

@app.post("/roll")
@limiter.limit("60/minute")
async def roll(request: Request, req: DiceRollRequest):
    """Evalúa una tirada de dados y envía el resultado"""
    logger.info(f"🎲 Tirando dados: {req.formula}")
    
    try:
        res = evaluar_formula_dados(req.formula)
        
        if res.get("error"):
            logger.warning(f"Fórmula de dados inválida: {req.formula}")
            return res
        
        # Enviar resultado a la sesión
        await manager.send_to_session(
            req.session_id,
            {"type": "dice_result", "data": res}
        )
        
        logger.info(f"✅ Resultado: {res['resultado']}")
        
        return res
        
    except Exception as e:
        logger.error(f"Error al tirar dados: {e}", exc_info=True)
        return {"error": True, "mensaje": str(e)}

@app.websocket("/ws/{session_id}")
async def ws_endpoint(
    websocket: WebSocket, 
    session_id: str,
    client_type: str = Query(default="player", regex="^(dm|player|launcher)$"),
    client_name: str = Query(default="Player", max_length=50)
):
    """
    WebSocket endpoint multi-cliente.
    Query params:
        client_type: "dm" or "player"
        client_name: Nombre visible del cliente
    """
    await manager.connect(session_id, websocket, client_type, client_name)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            # logger.debug(f"WS [{client_type}] mensaje: {msg_type}")

            # ── Clientes: Solicitar lista ──
            if msg_type == "request_clients":
                clients = manager.get_connected_clients(session_id)
                await websocket.send_json({
                    "type": "clients_list",
                    "clients": clients,
                    "total": len(clients)
                })

            # ── Escena (reenviar a todos) ──
            elif msg_type == "scene":
                logger.info(f"Reenviando escena: {data.get('title', 'Sin título')}")
                await manager.send_to_session(session_id, data)

            # ── VTT: Solicitar estado del mapa ──
            elif msg_type == "request_map_state":
                session_state = vtt_state.get_session(session_id)
                await websocket.send_json({
                    "type": "map_state",
                    "background": session_state["background"],
                    "tokens": vtt_state.get_all_tokens(session_id),
                })
                # logger.info(f"Estado de mapa enviado a {session_id}")

            # ── VTT: Token movido por un cliente ──
            elif msg_type == "token_moved":
                token_id = data.get("token_id")
                x = data.get("x", 0)
                y = data.get("y", 0)
                if vtt_state.update_token_position(session_id, token_id, x, y):
                    await manager.broadcast_except(session_id, {
                        "type": "token_updated",
                        "token_id": token_id,
                        "x": x,
                        "y": y,
                    }, exclude_ws=websocket)
                    # logger.info(f"Token movido: {token_id} → ({x}, {y})")

            # ── Otros mensajes (toggle_party, blackout, etc.) ──
            else:
                # Reenviar a todos para compatibilidad con comandos existentes
                await manager.send_to_session(session_id, data)

    except WebSocketDisconnect:
        # Get metadata before disconnecting
        disconnected_meta = manager.disconnect(session_id, websocket)
        
        # Broadcast disconnection to remaining clients
        if disconnected_meta:
            await manager.send_to_session(session_id, {
                "type": "client_disconnected",
                "client_name": disconnected_meta.get("name", "Unknown"),
                "client_type": disconnected_meta.get("type", "unknown"),
                "total_connections": manager.get_connection_count(session_id),
                "timestamp": datetime.now().isoformat()
            })

    except Exception as e:
        logger.error(f"Error en WebSocket: {e}", exc_info=True)
        manager.disconnect(session_id, websocket)

@app.get("/api/connections/{session_id}")
async def get_connections(session_id: str):
    """
    Get list of currently connected clients for a session.
    Useful for DM screen to show who's online.
    """
    clients = manager.get_connected_clients(session_id)
    
    return {
        "session_id": session_id,
        "total_connections": len(clients),
        "clients": clients
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    init_db()
    log_startup_info()
    logger.info(f"Modelo IA: {MODELO}")
    logger.info(f"URL Ollama: {OLLAMA_URL}")
    logger.info(f"Directorio guardados: {SAVE_DIR} (legacy)")
    logger.info(f"Base de datos: cronista.db (SQLite)")

# ─── Campañas (listar / eliminar) ────────────────────────

@app.get("/campaigns")
async def list_campaigns():
    """Lista todas las campañas guardadas."""
    with get_session() as db:
        stmt = select(Campaign).order_by(Campaign.updated_at.desc())
        campaigns = db.exec(stmt).all()
        return [
            {
                "id": c.id,
                "session_id": c.session_id,
                "title": c.title,
                "style": c.style,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
            }
            for c in campaigns
        ]

@app.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: int):
    """Elimina una campaña por ID."""
    with get_session() as db:
        campaign = db.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaña no encontrada")
        db.delete(campaign)
        db.commit()
        logger.info(f"🗑️ Campaña eliminada: {campaign.title} (id={campaign_id})")
        return {"status": "ok", "deleted": campaign.title}

# ─── Importar JSON legacy ────────────────────────────────

@app.post("/import/json")
async def import_json_save():
    """Importa todas las partidas JSON de partidas_guardadas/ a SQLite."""
    imported = 0
    for fname in os.listdir(SAVE_DIR):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(SAVE_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            sid = fname.replace("partida_", "").replace(".json", "")
            title = "Importada"
            adventure = data.get("adventure", {})
            if isinstance(adventure, dict):
                historia = adventure.get("historia", {})
                if isinstance(historia, dict):
                    title = historia.get("titulo", "Importada")
            
            with get_session() as db:
                existing = db.exec(select(Campaign).where(Campaign.session_id == sid)).first()
                if not existing:
                    campaign = Campaign(
                        session_id=sid,
                        title=title,
                        data_json=json.dumps(data, ensure_ascii=False),
                    )
                    db.add(campaign)
                    db.commit()
                    imported += 1
        except Exception as e:
            logger.error(f"Error importando {fname}: {e}")
    
    logger.info(f"📥 Importadas {imported} partidas JSON a SQLite")
    return {"status": "ok", "imported": imported}

# ─── Biblioteca: NPCs ────────────────────────────────────

@app.get("/library/npcs")
async def api_list_npcs(tag: Optional[str] = None):
    npcs = library.listar_npcs(tag)
    return [
        {
            "id": n.id, "name": n.name, "race": n.race,
            "class_name": n.class_name, "description": n.description,
            "personality": n.personality,
            "stats": json.loads(n.stats_json) if n.stats_json else {},
            "tags": n.tags,
        }
        for n in npcs
    ]

@app.post("/library/npcs")
async def api_create_npc(data: dict):
    npc = library.crear_npc(data)
    return {"status": "ok", "id": npc.id, "name": npc.name}

@app.put("/library/npcs/{npc_id}")
async def api_update_npc(npc_id: int, data: dict):
    npc = library.actualizar_npc(npc_id, data)
    if not npc:
        raise HTTPException(status_code=404, detail="NPC no encontrado")
    return {"status": "ok", "id": npc.id, "name": npc.name}

@app.delete("/library/npcs/{npc_id}")
async def api_delete_npc(npc_id: int):
    if not library.eliminar_npc(npc_id):
        raise HTTPException(status_code=404, detail="NPC no encontrado")
    return {"status": "ok"}

# ─── Biblioteca: Enemigos ────────────────────────────────

@app.get("/library/enemies")
async def api_list_enemies(tag: Optional[str] = None):
    enemies = library.listar_enemies(tag)
    return [
        {
            "id": e.id, "name": e.name, "cr": e.cr,
            "hp": e.hp, "ac": e.ac, "attack": e.attack,
            "damage": e.damage,
            "abilities": json.loads(e.abilities_json) if e.abilities_json else [],
            "tags": e.tags,
        }
        for e in enemies
    ]

@app.post("/library/enemies")
async def api_create_enemy(data: dict):
    enemy = library.crear_enemy(data)
    return {"status": "ok", "id": enemy.id, "name": enemy.name}

@app.put("/library/enemies/{enemy_id}")
async def api_update_enemy(enemy_id: int, data: dict):
    enemy = library.actualizar_enemy(enemy_id, data)
    if not enemy:
        raise HTTPException(status_code=404, detail="Enemigo no encontrado")
    return {"status": "ok", "id": enemy.id, "name": enemy.name}

@app.delete("/library/enemies/{enemy_id}")
async def api_delete_enemy(enemy_id: int):
    if not library.eliminar_enemy(enemy_id):
        raise HTTPException(status_code=404, detail="Enemigo no encontrado")
    return {"status": "ok"}

# ─── Biblioteca: Encuentros ──────────────────────────────

@app.get("/library/encounters")
async def api_list_encounters(tag: Optional[str] = None):
    encounters = library.listar_encounters(tag)
    return [
        {
            "id": enc.id, "name": enc.name, "description": enc.description,
            "difficulty": enc.difficulty,
            "enemies": json.loads(enc.enemies_json) if enc.enemies_json else [],
            "environment": enc.environment, "loot": enc.loot,
            "tags": enc.tags,
        }
        for enc in encounters
    ]

@app.post("/library/encounters")
async def api_create_encounter(data: dict):
    encounter = library.crear_encounter(data)
    return {"status": "ok", "id": encounter.id, "name": encounter.name}

@app.put("/library/encounters/{encounter_id}")
async def api_update_encounter(encounter_id: int, data: dict):
    encounter = library.actualizar_encounter(encounter_id, data)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encuentro no encontrado")
    return {"status": "ok", "id": encounter.id, "name": encounter.name}

@app.delete("/library/encounters/{encounter_id}")
async def api_delete_encounter(encounter_id: int):
    if not library.eliminar_encounter(encounter_id):
        raise HTTPException(status_code=404, detail="Encuentro no encontrado")
    return {"status": "ok"}

# ─── Biblioteca: Items ───────────────────────────────────

@app.get("/library/items")
async def api_list_items(tag: Optional[str] = None, item_type: Optional[str] = None):
    items = library.listar_items(tag, item_type)
    return [
        {
            "id": i.id, "name": i.name, "item_type": i.item_type,
            "rarity": i.rarity, "damage": i.damage, "properties": i.properties,
            "description": i.description, "value_gp": i.value_gp,
            "weight": i.weight, "tags": i.tags,
        }
        for i in items
    ]

@app.post("/library/items")
async def api_create_item(data: dict):
    item = library.crear_item(data)
    return {"status": "ok", "id": item.id, "name": item.name}

@app.put("/library/items/{item_id}")
async def api_update_item(item_id: int, data: dict):
    item = library.actualizar_item(item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"status": "ok", "id": item.id, "name": item.name}

@app.delete("/library/items/{item_id}")
async def api_delete_item(item_id: int):
    if not library.eliminar_item(item_id):
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"status": "ok"}

# ─── Búsqueda Global + Seed ──────────────────────────────

@app.get("/library/search")
async def api_search_library(
    q: Optional[str] = None,
    type: Optional[str] = None,
    cr_min: Optional[float] = None,
    cr_max: Optional[float] = None,
    tag: Optional[str] = None,
):
    """Búsqueda global en toda la biblioteca."""
    return library.buscar_biblioteca(q=q, content_type=type, cr_min=cr_min, cr_max=cr_max, tag=tag)

@app.post("/library/seed")
async def api_seed_library():
    """Recarga datos SRD manualmente."""
    from app.components.dnd.srd_data import seed_library_if_empty
    seed_library_if_empty()
    return {"status": "ok", "message": "SRD seed ejecutado"}

# ─── Sistema de Botín (Loot) ──────────────────────────────

from app.components.dnd.loot import generate_loot

@app.get("/api/loot/generate")
async def api_generate_loot(cr: int = 0, type: str = "individual"):
    """
    Genera un botín aleatorio basado en el CR del monstruo o encuentro.
    type puede ser 'individual' o 'hoard'
    """
    try:
        loot_result = generate_loot(cr, type)
        return {"status": "ok", "loot": loot_result}
    except Exception as e:
        logger.error(f"Error generando botín: {e}", exc_info=True)
        return {"status": "error", "message": "Fallo al generar botín"}

# ─── VTT Endpoints ───────────────────────────────────────

@app.post("/vtt/scene")
@limiter.limit("30/minute")
async def vtt_project_scene(request: Request, req: dict):
    """Proyecta una escena al VTT (mapa + tokens automáticos)."""
    session_id = req.get("session_id", "default_session")
    scene_id = req.get("scene_id", 0)

    logger.info(f"🎮 Proyectando escena {scene_id} al VTT ({session_id})")

    if session_id not in SESSIONS or "adventure" not in SESSIONS[session_id]:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    adv = SESSIONS[session_id]["adventure"]
    escenas = adv.get("historia", {}).get("escenas", [])
    if scene_id < 0 or scene_id >= len(escenas):
        raise HTTPException(status_code=404, detail="Escena no encontrada")

    escena = escenas[scene_id]

    # Guardar fondo
    img_url = escena.get("img")
    if img_url:
        vtt_state.set_background(session_id, img_url)

    # Enviar escena a todos los clientes (con flag show_vtt)
    await manager.send_to_session(session_id, {
        "type": "scene",
        "show_vtt": True,
        "img": img_url,
        "title": escena.get("nombre", ""),
        "text": escena.get("narrativa", ""),
        "narrativa": escena.get("narrativa", ""),
    })

    # Limpiar tokens previos
    vtt_state.clear_tokens(session_id)
    await manager.send_to_session(session_id, {"type": "clear_map"})

    # Crear tokens de PJs automáticamente
    pjs = adv.get("pjs", [])
    for idx, pj in enumerate(pjs):
        token_id = f"pj_{idx}"
        token_data = {
            "id": token_id,
            "name": pj.get("nombre", f"PJ {idx+1}"),
            "x": 128 + (idx * 64),
            "y": 128,
            "color": "#2ecc71",
            "img": pj.get("img"),
            "type": "pj",
        }
        vtt_state.add_token(session_id, token_id, token_data)
        await manager.send_to_session(session_id, {
            "type": "token_create",
            "token": token_data,
        })

    # Crear tokens de enemigos automáticamente
    enemigos = escena.get("enemigos", [])
    for idx, enemigo in enumerate(enemigos):
        cantidad_raw = enemigo.get("cantidad", "1")
        try:
            num = int(cantidad_raw) if "d" not in str(cantidad_raw) else random.randint(1, 4)
        except (ValueError, TypeError):
            num = 1

        for i in range(num):
            token_id = f"enemigo_{scene_id}_{idx}_{i}"
            token_data = {
                "id": token_id,
                "name": f"{enemigo['nombre']} #{i+1}" if num > 1 else enemigo["nombre"],
                "x": 64 + (i * 64),
                "y": 384,
                "color": "#ff4444",
                "type": "enemigo",
            }
            vtt_state.add_token(session_id, token_id, token_data)
            await manager.send_to_session(session_id, {
                "type": "token_create",
                "token": token_data,
            })

    return {"status": "projected", "scene_id": scene_id}


@app.post("/vtt/token/create")
@limiter.limit("60/minute")
async def create_token(request: Request, body: CreateTokenRequest):
    """Crea un nuevo token en el VTT"""
    session_id = body.session_id
    
    token_data = {
        "id": body.token_id,
        "name": body.name,
        "x": body.x, 
        "y": body.y,
        "color": body.color,
        "img": body.img,
        "type": body.token_type
    }
    
    vtt_state.add_token(session_id, request.token_id, token_data)
    
    # Notificar a clientes
    await manager.send_to_session(session_id, {
        "type": "token_created",
        "token": token_data
    })
    
    logger.info(f"♟️ Token creado: {request.name} ({request.token_id})")
    return {"status": "ok", "token": token_data}


@app.delete("/vtt/token")
@limiter.limit("60/minute")
async def remove_token(request: Request, body: DeleteTokenRequest):
    """Elimina un token del VTT"""
    session_id = body.session_id
    token_id = body.token_id
    
    if vtt_state.remove_token(session_id, token_id):
        await manager.send_to_session(session_id, {
            "type": "token_removed",
            "token_id": token_id
        })
        logger.info(f"🗑️ Token eliminado: {token_id}")
        return {"status": "ok"}
    
    raise HTTPException(status_code=404, detail="Token not found")


@app.post("/vtt/clear")
@limiter.limit("10/minute")
async def clear_map(request: Request, body: ClearMapRequest):
    """Limpia todos los tokens del mapa"""
    session_id = body.session_id
    
    vtt_state.clear_tokens(session_id)
    
    await manager.send_to_session(session_id, {
        "type": "clear_map"
    })
    
    logger.info(f"🧹 Mapa limpiado para sesión {session_id}")
    return {"status": "ok"}


@app.get("/vtt/state/{session_id}")
async def vtt_get_state(session_id: str):
    """Obtiene el estado actual del VTT."""
    s = vtt_state.get_session(session_id)
    return {
        "background": s["background"],
        "tokens": vtt_state.get_all_tokens(session_id),
        "grid_visible": s["grid_visible"],
    }

@app.get("/api/rate-limit-status")
@limiter.exempt
async def get_rate_limit_status(request: Request):
    """
    Returns rate limit information for debugging.
    Only available in development.
    """
    return {
        "limiter": "active",
        "default_limit": "100/minute",
        "client_ip": get_remote_address(request),
        "limits": {
            "/new_game": "3/minute",
            "/oracle": "10/minute",
            "/save": "20/minute",
            "/vtt/scene": "30/minute",
            "/roll": "60/minute",
            "/combat": "120/minute"
        }
    }

# ============================================
# AI CACHE MANAGEMENT ENDPOINTS
# ============================================

from app.components.ai.client import get_cache_stats, clear_prompt_cache

@app.get("/api/ai/cache/stats")
async def get_ai_cache_stats():
    """
    Get AI prompt cache statistics.
    Shows hit rate, size, and performance metrics.
    """
    stats = get_cache_stats()
    
    return {
        "status": "ok",
        "cache": stats,
        "recommendations": _get_cache_recommendations(stats)
    }

def _get_cache_recommendations(stats: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on cache performance"""
    recs = []
    
    hit_rate = stats.get("hit_rate_percent", 0)
    
    if hit_rate < 20:
        recs.append("⚠️ Low hit rate - consider enabling cache on more prompts")
    elif hit_rate > 60:
        recs.append("✓ Good hit rate - cache is working well")
    
    if stats["size"] >= stats["maxsize"] * 0.9:
        recs.append("⚠️ Cache nearly full - consider increasing maxsize")
    
    if stats["bypassed"] > stats["hits"]:
        recs.append("ℹ️ Many bypassed requests - verify use_cache flags")
    
    return recs


@app.post("/api/ai/cache/clear")
async def clear_ai_cache():
    """
    Clear all cached AI responses.
    Forces fresh generation on next requests.
    
    Use cases:
    - Testing new prompt variations
    - Model updated/changed
    - Suspected stale content
    """
    clear_prompt_cache()
    
    logger.info("AI cache cleared via API endpoint")
    
    return {
        "status": "cleared",
        "message": "All cached AI responses have been cleared",
        "new_stats": get_cache_stats()
    }


@app.post("/api/ai/cache/warmup")
async def warmup_cache(background_tasks: BackgroundTasks):
    """
    Pre-populate cache with common prompts.
    Useful after cache clear or server restart.
    """
    from app.components.ai.client import generar_con_ia
    
    common_prompts = [
        # Common character archetypes
        ("Genera NPC: comerciante humano amigable", True),
        ("Genera NPC: guardia orco intimidante", True),
        ("Genera NPC: mago élfico sabio", True),
        
        # Common items
        ("Describe: espada larga +1", False),
        ("Describe: poción de curación", False),
    ]
    
    def _warmup():
        for prompt, json_mode in common_prompts:
            generar_con_ia(prompt, json_mode=json_mode, use_cache=True)
            logger.info(f"Cache warmup: {prompt}")
    
    background_tasks.add_task(_warmup)
    
    return {
        "status": "warming",
        "message": f"Pre-caching {len(common_prompts)} common prompts in background"
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🎲 CRONISTA V80.1 (MODULARIZADO)")
    print("=" * 60)
    print(f"DM: http://localhost:8000/")
    print(f"PLAYER: http://0.0.0.0:8000/player")
    print(f"Logs: ./logs/")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        log_level="info",
        reload=True
    )
