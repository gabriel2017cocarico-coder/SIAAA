"""
Cliente HTTP hacia la API REST de Ollama.

Usa solo la librería estándar (urllib) para no agregar
dependencias al proyecto. Toda falla de red o del motor se
traduce a una excepción propia, para que la vista responda con
un mensaje controlado y nunca con un error 500.

Endpoints de Ollama usados:
  GET  /api/tags      -> modelos instalados (verificación de estado)
  POST /api/generate  -> generación de la respuesta
"""

import json
import logging
import socket
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


# ==========================================================
# EXCEPCIONES
# ==========================================================

class OllamaError(Exception):
    """Error genérico del motor de IA."""

    mensaje_usuario = 'El asistente tuvo un problema al generar la respuesta. Intenta de nuevo.'
    codigo_http = 502


class OllamaNoDisponible(OllamaError):
    """Ollama apagado o inalcanzable por red."""

    mensaje_usuario = 'El asistente no está disponible en este momento. Avisa a UTIC si el problema continúa.'
    codigo_http = 503


class OllamaTiempoAgotado(OllamaError):
    """Ollama no respondió dentro de OLLAMA_TIMEOUT."""

    mensaje_usuario = 'El asistente tardó demasiado en responder. Intenta con una pregunta más corta.'
    codigo_http = 504


class ModeloNoEncontrado(OllamaError):
    """El modelo configurado no existe en Ollama."""

    mensaje_usuario = 'El modelo de IA no está instalado en el servidor. Avisa a UTIC.'
    codigo_http = 503


# ==========================================================
# UTILIDADES INTERNAS
# ==========================================================

def _url(ruta):
    return settings.OLLAMA_URL.rstrip('/') + ruta


def _opciones(max_tokens=None):
    return {
        'num_predict': max_tokens or settings.OLLAMA_MAX_TOKENS,
    }


def _abrir(peticion, timeout):
    """Abre la conexión y traduce los errores de red a excepciones propias."""
    try:
        return urllib.request.urlopen(peticion, timeout=timeout)
    except urllib.error.HTTPError as error:
        cuerpo = error.read().decode('utf-8', 'replace')
        logger.warning('Ollama respondió HTTP %s: %s', error.code, cuerpo[:300])
        if error.code == 404 and 'not found' in cuerpo.lower():
            raise ModeloNoEncontrado(cuerpo) from error
        raise OllamaError(cuerpo) from error
    except (socket.timeout, TimeoutError) as error:
        raise OllamaTiempoAgotado(str(error)) from error
    except urllib.error.URLError as error:
        if isinstance(error.reason, (socket.timeout, TimeoutError)):
            raise OllamaTiempoAgotado(str(error)) from error
        logger.warning('No se pudo conectar con Ollama en %s: %s', settings.OLLAMA_URL, error.reason)
        raise OllamaNoDisponible(str(error.reason)) from error
    except (ConnectionError, OSError) as error:
        raise OllamaNoDisponible(str(error)) from error


def _peticion_generate(prompt, stream, max_tokens=None):
    datos = {
        'model': settings.OLLAMA_MODELO,
        'prompt': prompt,
        'stream': stream,
        'keep_alive': settings.OLLAMA_KEEP_ALIVE,
        'options': _opciones(max_tokens),
    }
    return urllib.request.Request(
        _url('/api/generate'),
        data=json.dumps(datos).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )


# ==========================================================
# API PÚBLICA
# ==========================================================

def estado():
    """Comprueba si Ollama responde y si el modelo está instalado."""
    try:
        with _abrir(urllib.request.Request(_url('/api/tags')), timeout=5) as respuesta:
            datos = json.loads(respuesta.read().decode('utf-8'))
    except OllamaError as error:
        return {'ollama': False, 'modelo_instalado': False, 'detalle': error.mensaje_usuario}

    nombres = [m.get('name', '') for m in datos.get('models', [])]
    modelo = settings.OLLAMA_MODELO
    instalado = any(n == modelo or n.split(':')[0] == modelo for n in nombres)
    return {'ollama': True, 'modelo_instalado': instalado, 'modelo': modelo}


def precalentar(prompt):
    """Carga el modelo y procesa por adelantado el contexto del usuario.

    Ollama guarda en caché el inicio del prompt ya procesado; la
    pregunta real que llegue después reutiliza ese trabajo y responde
    mucho más rápido. Se ejecuta en segundo plano: los errores se
    registran y se ignoran.
    """
    def tarea():
        try:
            generar(prompt, max_tokens=1)
        except OllamaError as error:
            logger.info('Precalentamiento omitido: %s', type(error).__name__)

    import threading
    threading.Thread(target=tarea, daemon=True).start()


def generar(prompt, max_tokens=None):
    """Genera la respuesta completa (sin streaming).

    Devuelve un diccionario con el texto y las métricas que
    informa Ollama (en milisegundos).
    """
    peticion = _peticion_generate(prompt, stream=False, max_tokens=max_tokens)
    with _abrir(peticion, timeout=settings.OLLAMA_TIMEOUT) as respuesta:
        try:
            datos = json.loads(respuesta.read().decode('utf-8'))
        except (socket.timeout, TimeoutError) as error:
            raise OllamaTiempoAgotado(str(error)) from error
        except ValueError as error:
            raise OllamaError('Respuesta no válida de Ollama') from error

    if datos.get('error'):
        raise OllamaError(datos['error'])

    return {
        'texto': (datos.get('response') or '').strip(),
        'metricas': _metricas(datos),
    }


def generar_stream(prompt):
    """Genera la respuesta fragmento a fragmento.

    Produce diccionarios {'texto': '...'} por cada fragmento y,
    al final, {'fin': True, 'metricas': {...}}.
    """
    respuesta = _abrir(_peticion_generate(prompt, stream=True), timeout=settings.OLLAMA_TIMEOUT)
    try:
        for linea in respuesta:
            if not linea.strip():
                continue
            try:
                datos = json.loads(linea.decode('utf-8'))
            except ValueError:
                continue
            if datos.get('error'):
                raise OllamaError(datos['error'])
            if datos.get('response'):
                yield {'texto': datos['response']}
            if datos.get('done'):
                yield {'fin': True, 'metricas': _metricas(datos)}
                return
    except (socket.timeout, TimeoutError) as error:
        raise OllamaTiempoAgotado(str(error)) from error
    finally:
        respuesta.close()


def _metricas(datos):
    """Convierte las métricas de Ollama (nanosegundos) a milisegundos."""
    def ms(clave):
        valor = datos.get(clave)
        return round(valor / 1_000_000) if valor else None

    tokens = datos.get('eval_count')
    duracion_eval = datos.get('eval_duration')
    return {
        'total_ms': ms('total_duration'),
        'carga_modelo_ms': ms('load_duration'),
        'lectura_prompt_ms': ms('prompt_eval_duration'),
        'generacion_ms': ms('eval_duration'),
        'tokens_prompt': datos.get('prompt_eval_count'),
        'tokens_respuesta': tokens,
        'tokens_por_segundo': round(tokens / (duracion_eval / 1e9), 1) if tokens and duracion_eval else None,
    }
