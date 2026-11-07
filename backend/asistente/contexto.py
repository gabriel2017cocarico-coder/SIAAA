"""
Contexto operativo que se adjunta a cada consulta del asistente.

PRIVACIDAD: el asistente solo recibe la información que el
usuario ya puede ver en las pantallas de SIGTA. Para garantizarlo
no se reescriben las reglas de visibilidad: se reutiliza el
get_queryset() de los mismos ViewSets que alimentan las bandejas
(soporte, mantenimiento y compras). Si mañana cambia una regla de
visibilidad en el sistema, el asistente la respeta automáticamente.
"""

from django.db.models import Count
from django.utils import timezone

from usuarios.models import obtener_codigos_rol_efectivos

# Cantidad máxima de expedientes activos listados por módulo:
# más contexto = respuestas más lentas en equipos sin GPU.
MAX_ITEMS = 6

ESTADOS_TERMINALES_COMPRA = {'CERRADO_ARCHIVADO', 'RECHAZADO', 'ANULADO'}


def _queryset_visible(viewset_cls, request):
    """Ejecuta el get_queryset() real del ViewSet para este usuario."""
    vista = viewset_cls()
    vista.request = request
    vista.action = 'list'
    vista.kwargs = {}
    vista.format_kwarg = None
    return vista.get_queryset()


def _nombre(usuario):
    if not usuario:
        return 'sin asignar'
    return usuario.nombre_completo or usuario.email


def _fecha(valor):
    if not valor:
        return '-'
    return timezone.localtime(valor).strftime('%d/%m/%Y')


def _resumen_por_estado(queryset, campo_estado, etiquetas=None):
    conteo = (
        queryset.order_by()
        .values(campo_estado)
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    partes = []
    for fila in conteo:
        clave = fila[campo_estado]
        nombre = etiquetas.get(clave, clave) if etiquetas else clave
        partes.append(f'{nombre}: {fila["total"]}')
    return ', '.join(partes) if partes else 'ninguno'


# ==========================================================
# SECCIONES POR MÓDULO
# ==========================================================

def _quien(usuario, request):
    """'ti' si el expediente es del usuario que pregunta."""
    return 'ti' if usuario and usuario.pk == request.user.pk else _nombre(usuario)


def _encabezado(titulo, total, activos_total, qs, campo_estado, etiquetas=None):
    # Totales explícitos: el modelo no debe confundir "total" con "activos".
    return [
        f'{titulo}: {total} en total, de los cuales {activos_total} están activos (en curso) '
        f'y {total - activos_total} finalizados (cerrados, rechazados o anulados).',
        f'Cantidad por estado: {_resumen_por_estado(qs, campo_estado, etiquetas)}.',
    ]


# Los expedientes se describen como frases naturales (sin barras ni
# columnas) porque el modelo tiende a copiarlos y la respuesta también
# se lee en voz alta.

def _seccion_soporte(request):
    from soporte.views import TicketViewSet

    qs = _queryset_visible(TicketViewSet, request)
    total = qs.count()
    if not total:
        return 'TICKETS DE SOPORTE TÉCNICO: no tienes ninguno visible.'

    activos_qs = qs.filter(estado__es_terminal=False)
    lineas = _encabezado('TICKETS DE SOPORTE TÉCNICO', total, activos_qs.count(), qs, 'estado__nombre')
    activos = activos_qs[:MAX_ITEMS]
    if activos:
        lineas.append(f'Los {len(activos)} tickets activos más recientes:')
        for t in activos:
            sla = f', con plazo de atención hasta el {_fecha(t.sla_fecha_limite)}' if t.sla_fecha_limite else ''
            lineas.append(
                f'- Ticket {t.codigo}, "{t.titulo}": estado {t.estado.nombre}, prioridad {t.get_prioridad_display()}, '
                f'lo atiende {_nombre(t.tecnico_asignado)}, solicitado por {_quien(t.solicitante, request)} '
                f'el {_fecha(t.creado_en)}{sla}.'
            )
    return '\n'.join(lineas)


def _seccion_mantenimiento(request):
    from mantenimiento.views import RequerimientoMantenimientoViewSet

    qs = _queryset_visible(RequerimientoMantenimientoViewSet, request)
    total = qs.count()
    if not total:
        return 'REQUERIMIENTOS DE MANTENIMIENTO: no tienes ninguno visible.'

    activos_qs = qs.filter(estado__es_terminal=False)
    lineas = _encabezado('REQUERIMIENTOS DE MANTENIMIENTO', total, activos_qs.count(), qs, 'estado__nombre')
    activos = activos_qs[:MAX_ITEMS]
    if activos:
        lineas.append(f'Los {len(activos)} requerimientos activos más recientes:')
        for r in activos:
            prioridad = f'prioridad {r.prioridad_jefatura.lower()}' if r.prioridad_jefatura else 'prioridad aún sin definir'
            lineas.append(
                f'- Requerimiento {r.codigo}, "{r.titulo}": estado {r.estado.nombre}, {prioridad}, '
                f'lo atiende {_nombre(r.auxiliar_asignado)}, solicitado por {_quien(r.solicitante, request)} '
                f'el {_fecha(r.creado_en)}.'
            )
    return '\n'.join(lineas)


def _seccion_compras(request):
    from compras.models import SolicitudCompra
    from compras.views import SolicitudCompraViewSet

    qs = _queryset_visible(SolicitudCompraViewSet, request)
    total = qs.count()
    if not total:
        return 'SOLICITUDES DE COMPRA POR CAJA CHICA: no tienes ninguna visible.'

    activos_qs = qs.exclude(estado__in=ESTADOS_TERMINALES_COMPRA)
    lineas = _encabezado(
        'SOLICITUDES DE COMPRA POR CAJA CHICA', total, activos_qs.count(), qs, 'estado', dict(SolicitudCompra.ESTADOS)
    )
    activos = activos_qs[:MAX_ITEMS]
    if activos:
        lineas.append(f'Las {len(activos)} solicitudes activas más recientes:')
        for s in activos:
            lineas.append(
                f'- Solicitud {s.codigo}, "{s.titulo}": estado {s.get_estado_display()}, '
                f'monto estimado {s.monto_estimado} bolivianos, solicitada por {_quien(s.solicitante, request)} '
                f'el {_fecha(s.creado_en)}.'
            )
    return '\n'.join(lineas)


def _seccion_configuracion():
    try:
        from auditoria.models import PreferenciaSistema
        pref = PreferenciaSistema.objects.first()
    except Exception:  # la configuración es opcional para el asistente
        pref = None
    if not pref or pref.limite_caja_chica is None:
        return ''
    return f'CONFIGURACIÓN: el límite de una compra por Caja Chica es de {pref.limite_caja_chica} bolivianos (Bs).'


# ==========================================================
# API PÚBLICA
# ==========================================================

def construir_contexto(request):
    """Arma el texto de contexto para el usuario autenticado."""
    usuario = request.user
    roles = obtener_codigos_rol_efectivos(usuario)

    # Orden pensado para el caché de Ollama: lo que casi no cambia va
    # primero y la fecha/hora (cambia cada minuto) va al final. Así
    # Ollama reutiliza lo ya procesado y solo lee lo nuevo.
    secciones = [
        f'USUARIO QUE PREGUNTA: {_nombre(usuario)}, con rol {", ".join(roles) or "sin rol"}.',
    ]
    for constructor in (_seccion_soporte, _seccion_mantenimiento, _seccion_compras):
        try:
            secciones.append(constructor(request))
        except Exception:  # un módulo con error no debe tumbar al asistente
            import logging
            logging.getLogger(__name__).exception('Error armando contexto en %s', constructor.__name__)

    config = _seccion_configuracion()
    if config:
        secciones.append(config)

    secciones.append(f'FECHA Y HORA ACTUAL: {timezone.localtime().strftime("%d/%m/%Y %H:%M")}')
    return '\n\n'.join(secciones)
