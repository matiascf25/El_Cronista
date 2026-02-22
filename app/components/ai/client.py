import requests
import json
import os
import html
import hashlib
from typing import Optional, Any, Dict
from cachetools import TTLCache
from app.logger import setup_logger
from app.config import OLLAMA_URL, MODELO, SYSTEM_INSTRUCTIONS

logger = setup_logger("ai_client")

# Timeout para requests desde variable de entorno
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))

# ============================================
# AI RESPONSE CACHE
# ============================================

# Cache with 200 entries, 1 hour TTL (3600 seconds)
# Stores up to 200 AI responses, each expires after 1 hour
_prompt_cache = TTLCache(maxsize=200, ttl=3600)

# Cache statistics
_cache_stats = {
    "hits": 0,
    "misses": 0,
    "bypassed": 0,
    "evictions": 0
}


def _get_cache_key(task_prompt: str, json_mode: bool, contexto: str) -> str:
    """
    Generate deterministic cache key from prompt inputs.
    
    Uses SHA256 hash of combined inputs to create unique key.
    Same inputs always produce same key.
    
    Args:
        task_prompt: The main prompt text
        json_mode: Whether JSON output is expected
        contexto: Additional context string
    
    Returns:
        Hexadecimal hash string (64 chars)
    """
    # Normalize inputs
    prompt_normalized = task_prompt.strip().lower()
    context_normalized = contexto.strip().lower() if contexto else ""
    
    # Combine all inputs that affect output
    combined = f"{prompt_normalized}|{json_mode}|{context_normalized}|{MODELO}"
    
    # Generate hash
    hash_obj = hashlib.sha256(combined.encode('utf-8'))
    cache_key = hash_obj.hexdigest()
    
    return cache_key


def clear_prompt_cache():
    """
    Clear all cached AI responses.
    Useful for forcing fresh generation or freeing memory.
    """
    global _cache_stats
    
    entries_cleared = len(_prompt_cache)
    _prompt_cache.clear()
    
    logger.info(f"Prompt cache cleared: {entries_cleared} entries removed")
    
    # Reset stats
    _cache_stats = {
        "hits": 0,
        "misses": 0,
        "bypassed": 0,
        "evictions": 0
    }


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache performance statistics.
    
    Returns:
        Dict with:
            - size: Current number of cached entries
            - maxsize: Maximum cache capacity
            - ttl: Time-to-live in seconds
            - hits: Number of cache hits
            - misses: Number of cache misses
            - bypassed: Number of times cache was intentionally bypassed
            - hit_rate: Percentage of requests served from cache
    """
    total_requests = _cache_stats["hits"] + _cache_stats["misses"]
    hit_rate = (_cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
    
    return {
        "size": len(_prompt_cache),
        "maxsize": _prompt_cache.maxsize,
        "ttl_seconds": _prompt_cache.ttl,
        "hits": _cache_stats["hits"],
        "misses": _cache_stats["misses"],
        "bypassed": _cache_stats["bypassed"],
        "evictions": _cache_stats["evictions"],
        "hit_rate_percent": round(hit_rate, 2),
        "total_requests": total_requests
    }


def sanitizar_texto(texto: str) -> str:
    """Escapa caracteres HTML peligrosos"""
    try:
        sanitized = html.escape(str(texto))
        logger.debug(f"Texto sanitizado: {len(texto)} caracteres")
        return sanitized
    except Exception as e:
        logger.error(f"Error al sanitizar texto: {e}")
        return ""


def generar_con_ia(
    task_prompt: str, 
    json_mode: bool = True, 
    contexto: str = "",
    use_cache: bool = True
) -> Optional[Any]:
    """
    Genera contenido usando Ollama/LLM con soporte de caché.
    
    Args:
        task_prompt: Prompt principal de la tarea
        json_mode: Si True, espera respuesta en formato JSON
        contexto: Contexto adicional previo
        use_cache: Si True, usa caché para evitar llamadas duplicadas.
                   Si False, siempre consulta Ollama (para contenido único/temporal)
    
    Returns:
        Respuesta parseada (dict si JSON, str si texto) o None si error
    """
    global _cache_stats
    
    # Check cache if enabled
    if use_cache:
        cache_key = _get_cache_key(task_prompt, json_mode, contexto)
        
        if cache_key in _prompt_cache:
            _cache_stats["hits"] += 1
            cached_value = _prompt_cache[cache_key]
            
            logger.info(
                f"✓ Cache HIT ({_cache_stats['hits']} total) - "
                f"Prompt: {task_prompt[:60]}..."
            )
            # logger.debug(f"Cache stats: {get_cache_stats()}")
            
            return cached_value
        else:
            _cache_stats["misses"] += 1
            # logger.debug(
            #     f"Cache MISS ({_cache_stats['misses']} total) - "
            #     f"Prompt: {task_prompt[:60]}..."
            # )
    else:
        _cache_stats["bypassed"] += 1
        # logger.debug(
        #     f"Cache BYPASSED (use_cache=False) - "
        #     f"Prompt: {task_prompt[:60]}..."
        # )
    
    # Build full prompt (existing logic)
    full_prompt = f"{SYSTEM_INSTRUCTIONS}"
    
    if contexto:
        full_prompt += f"\n\nCONTEXTO PREVIO:\n{contexto}"
        
    full_prompt += f"\n\nTAREA:\n{task_prompt}"
    if json_mode:
        full_prompt += "\n\nFORMATO: JSON válido ÚNICAMENTE."
    
    logger.info(f"Generando contenido con IA (JSON={json_mode}, cached={use_cache})")
    # logger.debug(f"Prompt: {task_prompt[:100]}...")
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": full_prompt,
                "format": "json" if json_mode else "",
                "stream": False
            },
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        text = data.get('response', '')
        
        if not text:
            logger.error("Respuesta vacía de Ollama")
            return None
        
        # logger.info(f"✓ Respuesta recibida de Ollama ({len(text)} caracteres)")
        
        # Parse JSON if needed
        if json_mode:
            try:
                start = text.find('{')
                end = text.rfind('}') + 1
                
                if start != -1 and end > start:
                    json_text = text[start:end]
                    parsed = json.loads(json_text)
                    logger.info("✓ JSON parseado exitosamente")
                    
                    # Store in cache
                    if use_cache:
                        _prompt_cache[cache_key] = parsed
                        # logger.debug(f"Resultado almacenado en caché (key: {cache_key[:16]}...)")
                    
                    return parsed
                else:
                    parsed = json.loads(text)
                    logger.info("✓ JSON parseado exitosamente")
                    
                    if use_cache:
                        _prompt_cache[cache_key] = parsed
                    
                    return parsed
                    
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON de IA: {e}")
                logger.debug(f"Texto recibido: {text[:500]}")
                return None
        
        # Store text response in cache
        if use_cache:
            _prompt_cache[cache_key] = text
            # logger.debug(f"Resultado almacenado en caché (key: {cache_key[:16]}...)")
        
        return text
        
    except requests.Timeout:
        logger.error(f"Timeout al contactar Ollama ({OLLAMA_TIMEOUT}s): {OLLAMA_URL}")
        return None
        
    except requests.ConnectionError:
        logger.error(f"No se pudo conectar a Ollama: {OLLAMA_URL}")
        logger.warning("Verifica que Ollama esté corriendo: 'ollama serve'")
        return None
        
    except requests.HTTPError as e:
        logger.error(f"Error HTTP de Ollama: {e.response.status_code} - {e}")
        return None
        
    except Exception as e:
        logger.error(f"Error inesperado en generar_con_ia: {e}", exc_info=True)
        return None
