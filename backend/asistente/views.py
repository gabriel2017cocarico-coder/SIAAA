"""
Endpoints del asistente de IA.

  GET  /api/asistente/estado/        -> ¿Ollama y el modelo están listos?
  POST /api/asistente/chat/          -> respuesta completa en JSON
  POST /api/asistente/chat/stream/   -> respuesta en fragmentos (NDJSON)

Todos exigen sesión iniciada (token de SIGTA). Ante cualquier
falla del motor de IA responden con un mensaje controlado
(503 / 504 / 502), nunca con un error 500.
"""

import json
import logging
import time

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import servicios
from .contexto import construir_contexto

logger = logging.getLogger(__name__)

MAX_TURNOS_HISTORIAL = 4
MAX_CARACTERES_TURNO = 500


# ==========================================================
# VALIDACIÓN Y ARMADO DEL PROMPT
# ==========================================================

def _validar(request):
    """Devuelve (mensaje, historial) o lanza ValueError con el motivo."""
    mensaje = request.data.get('mensaje')
    if not isinstance(mensaje, str) or not mensaje.strip():
        raise ValueError('Escribe una consulta válida.')
    mensaje = mensaje.strip()
    if len(mensaje) > settings.ASISTENTE_MAX_CARACTERES:
        raise ValueError(f'La consulta no puede superar los {settings.ASISTENTE_MAX_CARACTERES} caracteres.')

    historial = []
    crudo = request.data.get('historial') or []
    if isinstance(crudo, list):
        for turno in crudo[-MAX_TURNOS_HISTORIAL:]:
            if not isinstance(turno, dict):
                continue
            rol = 'Usuario' if turno.get('rol') == 'usuario' else 'Asistente'
            texto = str(turno.get('texto') or '').strip()[:MAX_CARACTERES_TURNO]
            if texto:
                historial.append((rol, texto))
    return mensaje, historial


def _prefijo(request):
    """Inicio del prompt (datos del usuario). Es idéntico entre consultas
    seguidas, por eso Ollama puede reutilizarlo desde su caché."""
    return '\n\n'.join([
        '### DATOS ACTUALES DE SIGTA (usa solo estos datos para responder sobre el estado del sistema)',
        construir_contexto(request),
    ])


def _armar_prompt(request, mensaje, historial):
    partes = [_prefijo(request)]
    if historial:
        partes.append('### CONVERSACIÓN PREVIA')
        partes.extend(f'{rol}: {texto}' for rol, texto in historial)
    partes.append('### PREGUNTA DEL USUARIO')
    partes.append(mensaje)
    return '\n\n'.join(partes)


def _error(exc):
    return Response({'ok': False, 'error': exc.mensaje_usuario}, status=exc.codigo_http)


# ==========================================================
# VISTAS
# ==========================================================

class EstadoAsistenteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datos = servicios.estado()
        # El chat consulta el estado al abrirse: se aprovecha para
        # cargar el modelo y procesar los datos del usuario mientras
        # escribe su pregunta.
        if datos.get('modelo_instalado'):
            servicios.precalentar(_prefijo(request))
        return Response(datos)


class ChatAsistenteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            mensaje, historial = _validar(request)
        except ValueError as exc:
            return Response({'ok': False, 'error': str(exc)}, status=400)

        inicio = time.perf_counter()
        try:
            resultado = servicios.generar(_armar_prompt(request, mensaje, historial))
        except servicios.OllamaError as exc:
            logger.warning('Asistente: fallo de Ollama (%s) para %s', type(exc).__name__, request.user.email)
            return _error(exc)

        duracion_ms = round((time.perf_counter() - inicio) * 1000)
        logger.info('Asistente: %s respondió en %s ms', request.user.email, duracion_ms)
        return Response({
            'ok': True,
            'respuesta': resultado['texto'] or 'No pude generar una respuesta. Intenta reformular la pregunta.',
            'modelo': settings.OLLAMA_MODELO,
            'duracion_ms': duracion_ms,
            'metricas': resultado['metricas'],
        })


class ChatStreamAsistenteView(APIView):
    """Igual que /chat/, pero envía la respuesta a medida que se genera.

    Formato: una línea JSON por evento (NDJSON)
      {"texto": "..."}                       fragmento de la respuesta
      {"fin": true, "duracion_ms": ..., ...} respuesta terminada
      {"error": "..."}                       falla a mitad de la respuesta
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            mensaje, historial = _validar(request)
        except ValueError as exc:
            return Response({'ok': False, 'error': str(exc)}, status=400)

        inicio = time.perf_counter()
        generador = servicios.generar_stream(_armar_prompt(request, mensaje, historial))

        # Se pide el primer fragmento ANTES de abrir el stream: así un
        # Ollama apagado se informa con su código HTTP (503/504).
        try:
            primero = next(generador)
        except StopIteration:
            primero = {'fin': True, 'metricas': {}}
        except servicios.OllamaError as exc:
            logger.warning('Asistente (stream): fallo de Ollama (%s)', type(exc).__name__)
            return _error(exc)

        primer_fragmento_ms = round((time.perf_counter() - inicio) * 1000)
        email = request.user.email

        def eventos():
            def linea(dato):
                return (json.dumps(dato, ensure_ascii=False) + '\n').encode('utf-8')

            def cierre(evento):
                total = round((time.perf_counter() - inicio) * 1000)
                logger.info('Asistente (stream): %s primer fragmento %s ms, total %s ms', email, primer_fragmento_ms, total)
                return linea({
                    'fin': True,
                    'modelo': settings.OLLAMA_MODELO,
                    'duracion_ms': total,
                    'primer_fragmento_ms': primer_fragmento_ms,
                    'metricas': evento.get('metricas', {}),
                })

            try:
                if primero.get('fin'):
                    yield cierre(primero)
                    return
                yield linea(primero)
                for evento in generador:
                    if evento.get('fin'):
                        yield cierre(evento)
                        return
                    yield linea(evento)
            except servicios.OllamaError as exc:
                yield linea({'error': exc.mensaje_usuario})

        respuesta = StreamingHttpResponse(eventos(), content_type='application/x-ndjson; charset=utf-8')
        respuesta['Cache-Control'] = 'no-cache'
        respuesta['X-Accel-Buffering'] = 'no'
        return respuesta
